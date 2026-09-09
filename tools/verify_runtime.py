#!/usr/bin/env python3
"""Check a Windows x64 portable runtime and query an authenticated X root window.

Only Python's standard library is used. Evidence is written to a fresh directory;
the caller supplies the build's source commit, which is an assertion of provenance.
"""
import argparse
from contextlib import ExitStack
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import platform
import re
import secrets
import socket
import struct
import subprocess
import sys
import tempfile
import time


class VerificationError(Exception):
    def __init__(self, reason, exit_code=None):
        super().__init__(reason)
        self.exit_code = exit_code


def parse_dependencies(text):
    """Read dumpbin /dependents direct and delay imports; reject unknown output."""
    dependencies = []
    seen = set()
    in_section = False
    recognized = False
    for line in text.splitlines():
        stripped = line.strip()
        if re.fullmatch(r"Image has the following (?:delay load )?dependencies:", stripped):
            recognized = in_section = True
        elif stripped == "Summary":
            in_section = False
        elif stripped.startswith("File Type:"):
            recognized = True
        elif in_section and stripped:
            if not re.fullmatch(r"[^\\/:\s]+\.(?:dll|exe)", stripped, re.IGNORECASE):
                raise ValueError(f"Unrecognized dumpbin import line: {stripped}")
            if stripped.casefold() not in seen:
                dependencies.append(stripped)
                seen.add(stripped.casefold())
    if not recognized:
        raise ValueError("Unrecognized dumpbin output; cannot determine dependencies")
    return dependencies


def pe_machine(path):
    """Read the PE COFF Machine field, checking the complete DOS/COFF headers."""
    with Path(path).open("rb") as stream:
        dos = stream.read(64)
        if len(dos) != 64 or dos[:2] != b"MZ":
            raise ValueError(f"{path}: invalid or truncated DOS header")
        offset = struct.unpack_from("<I", dos, 0x3c)[0]
        if offset < 64:
            raise ValueError(f"{path}: invalid PE header offset")
        stream.seek(offset)
        header = stream.read(24)
        if len(header) != 24 or header[:4] != b"PE\0\0":
            raise ValueError(f"{path}: invalid or truncated PE/COFF header")
        return struct.unpack_from("<H", header, 4)[0]


def require_host():
    if os.name != "nt" or struct.calcsize("P") != 8 or platform.machine().lower() not in ("amd64", "x86_64"):
        raise ValueError("Windows x64 with 64-bit Python is required")
    if sys.version_info < (3, 11):
        raise ValueError("Python 3.11 or newer is required")
    # Query Windows itself instead of trusting a caller's SystemRoot override.
    import ctypes
    buffer = ctypes.create_unicode_buffer(32768)
    length = ctypes.windll.kernel32.GetSystemDirectoryW(buffer, len(buffer))
    if not length or length >= len(buffer):
        raise ValueError("Cannot determine the native Windows System32 directory")
    system32 = Path(buffer.value)
    if not system32.is_dir():
        raise ValueError("Native Windows System32 directory is missing")
    return system32


def child_environment(runtime, system32):
    removed = {"PATH", "DISPLAY", "XAUTHORITY", "XLOCALEDIR", "XKEYSYMDB",
               "XERRORDB", "XKB_CONFIG_ROOT"}
    env = {key: value for key, value in os.environ.items() if key.upper() not in removed}
    env["PATH"] = str(runtime) + os.pathsep + str(system32)
    return env


def process_options(runtime, env):
    options = {"cwd": str(runtime), "env": env, "stdin": subprocess.DEVNULL}
    if os.name == "nt":
        startup = subprocess.STARTUPINFO()
        startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startup.wShowWindow = subprocess.SW_HIDE
        options.update(startupinfo=startup, creationflags=subprocess.CREATE_NO_WINDOW)
    return options


def stop_owned_process(process):
    """Only act on a Popen handle created by this invocation; never by image name."""
    if process is not None and process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


def step_record(name):
    return {"name": name, "status": "NOT_RUN", "exit_code": None,
            "log_paths": [], "reason": None, "commands": []}


def run_command(args, runtime, env, output, prefix, timeout, step, secret=None):
    """File-backed output prevents pipe deadlock; timeout always reaps our child."""
    stdout_path = output / (prefix + ".stdout.log")
    stderr_path = output / (prefix + ".stderr.log")
    step["log_paths"].extend([str(stdout_path), str(stderr_path)])
    step["commands"].append(["<redacted>" if secret and str(arg) == secret else str(arg) for arg in args])
    process = None
    try:
        with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
            process = subprocess.Popen([str(arg) for arg in args], stdout=stdout, stderr=stderr,
                                       **process_options(runtime, env))
            try:
                return process.wait(timeout=max(0.001, timeout))
            except subprocess.TimeoutExpired:
                raise VerificationError(f"{prefix}: command timed out after {timeout:.2f} seconds") from None
    except OSError as error:
        # Do not stringify subprocess exceptions: they can contain secret argv.
        raise VerificationError(f"{prefix}: cannot execute ({type(error).__name__}, error {error.errno})") from None
    finally:
        stop_owned_process(process)
        if secret:
            for path in (stdout_path, stderr_path):
                if path.exists():
                    data = path.read_bytes()
                    path.write_bytes(data.replace(secret.encode("ascii"), b"<redacted>"))


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def scan_dependencies(runtime, dumpbin, output, timeout, system32, step):
    files = sorted((path for path in runtime.rglob("*")
                    if path.is_file() and path.suffix.lower() in (".exe", ".dll")),
                   key=lambda path: str(path).casefold())
    local = {path.name.casefold(): path for path in runtime.iterdir() if path.is_file()}
    system = {path.name.casefold(): path for path in system32.iterdir() if path.is_file()}
    # Validate every packaged image before launching even dumpbin.
    for path in files:
        machine = pe_machine(path)
        if machine != 0x8664:
            raise VerificationError(f"{path.relative_to(runtime)}: expected x64 PE (0x8664), got 0x{machine:04x}")
    results = []
    evidence = output / "dependencies.json"
    step["log_paths"].append(str(evidence))
    try:
        for index, path in enumerate(files):
            prefix = f"dependency-{index:03d}"
            code = run_command([dumpbin, "/nologo", "/dependents", path], runtime,
                               child_environment(runtime, system32), output, prefix, timeout, step)
            if code:
                raise VerificationError(f"dumpbin failed for {path.relative_to(runtime)}", code)
            imports = parse_dependencies((output / (prefix + ".stdout.log")).read_text(errors="replace"))
            record = {"path": str(path.relative_to(runtime)), "machine": "x64", "imports": []}
            results.append(record)
            for name in imports:
                key = name.casefold()
                if key.startswith(("api-ms-win-", "ext-ms-win-")):
                    record["imports"].append({"name": name, "resolution": "system_contract", "path": None})
                    continue
                resolved = local.get(key) or system.get(key)
                if resolved is None:
                    record["imports"].append({"name": name, "resolution": "missing", "path": None})
                    raise VerificationError(f"{path.relative_to(runtime)}: missing import {name} (runtime/System32)")
                if pe_machine(resolved) != 0x8664:
                    raise VerificationError(f"{path.relative_to(runtime)}: import {name} is not an x64 PE: {resolved}")
                record["imports"].append({"name": name, "resolution": "runtime" if key in local else "system32",
                                          "path": str(resolved)})
    finally:
        write_json(evidence, {"files": results, "search_directories": [str(runtime), str(system32)]})
    step["file_count"] = len(files)
    step.update(status="PASS", exit_code=0)


def check_display_port(display):
    port = 6000 + display
    addresses = [(socket.AF_INET, "127.0.0.1")]
    if socket.has_ipv6:
        addresses.append((socket.AF_INET6, "::1"))
    for family, address in addresses:
        with socket.socket(family, socket.SOCK_STREAM) as probe:
            if os.name == "nt":
                probe.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
            try:
                probe.bind((address, port))
            except OSError as error:
                # Hosts may disable IPv6 entirely; an unavailable IPv6 stack
                # is distinct from an occupied port on a usable interface.
                if family == socket.AF_INET6 and error.errno in (10047, 10049, 97, 99):
                    continue
                raise VerificationError(f"Display :{display} port {port} unavailable on {address}; choose another --display") from None


def run_smoke(runtime, output, display, timeout, system32=None):
    system32 = require_host() if system32 is None else system32
    env = child_environment(runtime, system32)
    steps = [step_record(name) for name in ("version", "display_port", "authentication", "startup", "root_window", "cleanup")]
    by_name = {step["name"]: step for step in steps}
    active = by_name["version"]
    server = None
    authority_directory = None
    cookie = None
    try:
        code = run_command([runtime / "vcxsrv.exe", "-version"], runtime, env, output,
                           "version", timeout, active)
        if code:
            raise VerificationError("vcxsrv -version failed", code)
        active.update(status="PASS", exit_code=0)
        active = by_name["display_port"]
        check_display_port(display)
        active.update(status="PASS", exit_code=0)
        active = by_name["authentication"]
        authority_directory = tempfile.TemporaryDirectory(prefix="vcxsrv-auth-")
        authority = Path(authority_directory.name) / "Xauthority"
        cookie = secrets.token_hex(16)
        address = f"127.0.0.1:{display}"
        code = run_command([runtime / "xauth.exe", "-f", authority, "add", address, ".", cookie],
                           runtime, env, output, "xauth", timeout, active, secret=cookie)
        if code or not authority.is_file():
            raise VerificationError("xauth did not create a usable authority file", code)
        active.update(status="PASS", exit_code=0)
        env["XAUTHORITY"] = str(authority)
        active = by_name["startup"]
        server_log = output / "server.log"
        stdout_path, stderr_path = output / "server.stdout.log", output / "server.stderr.log"
        active["log_paths"] = [str(server_log), str(stdout_path), str(stderr_path)]
        args = [str(runtime / "vcxsrv.exe"), f":{display}", "-multiwindow", "-clipboard",
                "-listen", "tcp", "-auth", str(authority), "-silent-dup-error", "-logfile", str(server_log)]
        active["commands"].append(args)
        deadline = time.monotonic() + timeout
        with ExitStack() as stack:
            stdout = stack.enter_context(stdout_path.open("wb"))
            stderr = stack.enter_context(stderr_path.open("wb"))
            try:
                server = subprocess.Popen(args, stdout=stdout, stderr=stderr, **process_options(runtime, env))
            except OSError as error:
                raise VerificationError(f"Cannot start vcxsrv (error {error.errno})") from None
            try:
                active = by_name["root_window"]
                attempt = 0
                last_code = None
                while time.monotonic() < deadline:
                    if server.poll() is not None:
                        active = by_name["startup"]
                        raise VerificationError("Server exited before a successful root query", server.returncode)
                    attempt += 1
                    prefix = f"client-{attempt:03d}"
                    last_code = run_command([runtime / "xwininfo.exe", "-display", address, "-root"],
                                            runtime, env, output, prefix,
                                            min(5, max(0.001, deadline - time.monotonic())), active)
                    text = (output / (prefix + ".stdout.log")).read_text(errors="replace")
                    width = re.search(r"^\s*Width:\s*(\d+)\s*$", text, re.MULTILINE)
                    height = re.search(r"^\s*Height:\s*(\d+)\s*$", text, re.MULTILINE)
                    if last_code == 0 and width and height and int(width[1]) > 0 and int(height[1]) > 0:
                        if server.poll() is not None:
                            active = by_name["startup"]
                            raise VerificationError("Server exited during root query", server.returncode)
                        active.update(status="PASS", exit_code=0, width=int(width[1]), height=int(height[1]))
                        by_name["startup"].update(status="PASS", reason="Authenticated root query succeeded")
                        break
                    remaining = deadline - time.monotonic()
                    if remaining > 0:
                        time.sleep(min(0.15, remaining))
                else:
                    raise VerificationError("Timed out waiting for an authenticated positive-size root window", last_code)
            finally:
                stop_owned_process(server)
    except (VerificationError, ValueError, OSError) as error:
        reason = str(error)
        if cookie:
            reason = reason.replace(cookie, "<redacted>")
        active.update(status="FAIL", reason=reason, exit_code=getattr(error, "exit_code", None))
    finally:
        cleanup = by_name["cleanup"]
        try:
            stop_owned_process(server)
            if authority_directory is not None:
                authority_directory.cleanup()
            cleanup.update(status="PASS", exit_code=0, reason="Owned children exited; temporary authority removed")
        except (OSError, subprocess.TimeoutExpired) as error:
            cleanup.update(status="FAIL", reason=f"Cleanup failed: {type(error).__name__}")
        if cookie:
            # Defensive redaction also covers server/client diagnostic output.
            for path in output.glob("*.log"):
                data = path.read_bytes()
                if cookie.encode("ascii") in data:
                    path.write_bytes(data.replace(cookie.encode("ascii"), b"<redacted>"))
    for step in steps:
        if step["status"] == "NOT_RUN" and step["reason"] is None:
            step["reason"] = "A prerequisite step did not complete"
    return steps


def verify(runtime, dumpbin, source_commit, output, display=97, timeout=30):
    runtime, dumpbin, output = (Path(path).resolve() for path in (runtime, dumpbin, output))
    # Reject before writing anything: failed evidence is never overwritten and
    # neither directory can contain the other (including resolved symlinks).
    if runtime == output or runtime in output.parents or output in runtime.parents:
        raise ValueError("Output and runtime directories must not overlap")
    if output.exists():
        raise ValueError("Output directory already exists; use a fresh path to preserve previous evidence")
    output.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    report = {"schema_version": 1, "source_commit": source_commit, "runtime": str(runtime),
              "started_at": datetime.now(timezone.utc).isoformat(), "duration_seconds": None,
              "status": "NOT_RUN", "steps": [],
              "host": {"platform": platform.platform(), "python": sys.version.split()[0],
                       "python_path": sys.executable},
              "parameters": {"dumpbin": str(dumpbin), "display": display,
                             "timeout": timeout if math.isfinite(timeout) else str(timeout)},
              "limitations": ["source_commit is supplied by the caller, not proof of binary provenance",
                              "Static imports do not cover every LoadLibrary path",
                              "A root query does not establish broad application or OpenGL compatibility"]}
    active = step_record("preconditions")
    report["steps"].append(active)
    try:
        system32 = require_host()
        if not isinstance(display, int) or not 0 <= display <= 59535:
            raise ValueError("Display must be an integer from 0 through 59535")
        if not math.isfinite(timeout) or timeout <= 0:
            raise ValueError("Timeout must be a finite positive number")
        if not re.fullmatch(r"[0-9a-fA-F]{40}|[0-9a-fA-F]{64}", source_commit):
            raise ValueError("source-commit must be a full 40- or 64-character Git commit ID")
        if not runtime.is_dir():
            raise ValueError(f"Runtime directory is missing: {runtime}")
        missing = [name for name in ("vcxsrv.exe", "xauth.exe", "xwininfo.exe") if not (runtime / name).is_file()]
        if missing:
            raise ValueError("Missing required runtime executables: " + ", ".join(missing))
        if not dumpbin.is_file():
            raise ValueError(f"dumpbin executable is missing: {dumpbin}")
        report["environment"] = {"path_directories": [str(runtime), str(system32)],
                                 "removed_variables": ["DISPLAY", "XAUTHORITY", "XLOCALEDIR", "XKEYSYMDB", "XERRORDB", "XKB_CONFIG_ROOT"]}
        active.update(status="PASS", exit_code=0)
        active = step_record("dependencies")
        report["steps"].append(active)
        scan_dependencies(runtime, dumpbin, output, timeout, system32, active)
        report["steps"].extend(run_smoke(runtime, output, display, timeout, system32))
        report["status"] = "PASS" if all(s["status"] == "PASS" for s in report["steps"]) else "FAIL"
    except (VerificationError, ValueError, OSError) as error:
        status = "NOT_RUN" if active["name"] == "preconditions" else "FAIL"
        active.update(status=status, reason=str(error), exit_code=getattr(error, "exit_code", None))
        report["status"] = status
    finally:
        report["duration_seconds"] = round(time.monotonic() - started, 3)
        write_json(output / "result.json", report)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime", required=True, type=Path)
    parser.add_argument("--dumpbin", required=True, type=Path)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--output", required=True, type=Path, help="Fresh evidence directory outside the runtime")
    parser.add_argument("--display", default=97, type=int)
    parser.add_argument("--timeout", default=30, type=float, help="Per scan/version/auth command and startup deadline in seconds")
    args = parser.parse_args(argv)
    try:
        report = verify(args.runtime, args.dumpbin, args.source_commit, args.output, args.display, args.timeout)
    except (ValueError, OSError) as error:
        print(f"NOT_RUN: {error}", file=sys.stderr)
        return 2
    print(f"{report['status']}: {args.output.resolve() / 'result.json'}")
    for step in report["steps"]:
        if step["status"] in ("FAIL", "NOT_RUN"):
            print(f"  {step['name']}: {step['reason']}", file=sys.stderr)
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
