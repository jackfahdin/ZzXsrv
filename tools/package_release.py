"""Build ZzXsrv release artifacts from a portable runtime directory.

Produces, under the output directory (full edition):
  zzxsrv-<version>-x64-portable.zip  - xcopy-runnable portable archive
  zzxsrv-<version>-x64-setup.exe     - Inno Setup installer (per-user by
                                       default, optional all-users via dialog)

The slim edition (--edition slim) ships the same server without the software
GL stack, the SSH launcher dependency, the XLaunch wizard and the demo
clients; artifact names gain a "-slim" infix.

Usage:
  python tools/package_release.py --dist-dir dist/x64/Release \
      [--version 2026.9.17] [--edition full|slim] \
      [--output-dir dist/release] [--inno ISCC.exe] [--zip-only]
"""

import argparse
import os
import shutil
import subprocess
import sys
import zipfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FALLBACK_INNO = r"D:\SoftWare\Inno Setup 7\ISCC.exe"
EDITIONS = ("full", "slim")

# Files dropped from the slim edition, relative to the dist root. Every entry
# was verified against the dist tree: libxml2.dll/libiconv.dll are only
# imported by xlaunch.exe and xclock.exe (both removed here), so no kept
# binary loses a dependency. Fonts are always kept.
SLIM_EXCLUDES = {
    # Mesa software rendering chain (swrast / texture compression helpers).
    "swrast_dri.dll": "Mesa software rasterizer",
    "swrastwgl_dri.dll": "Mesa software rasterizer (WGL variant)",
    "dxtn.dll": "Mesa S3TC texture compression helper",
    # External SSH client used only for X11 forwarding launches.
    "plink.exe": "SSH forwarding helper (external dependency)",
    # XLaunch wizard and its exclusive XML stack.
    "xlaunch.exe": "XLaunch wizard",
    "libxml2.dll": "XML parser used only by xlaunch/xclock",
    "libiconv.dll": "charset converter used only via libxml2",
    # Demo clients and their app-defaults resource files.
    "xclock.exe": "demo client",
    "xcalc.exe": "demo client",
    "XClock": "xclock app-defaults",
    "XClock-color": "xclock app-defaults",
    "XCalc": "xcalc app-defaults",
    "XCalc-color": "xcalc app-defaults",
}


def default_version() -> str:
    today = date.today()
    return f"{today.year}.{today.month}.{today.day}"


def resolve_inno(explicit: str | None) -> Path | None:
    """Locate ISCC.exe: explicit arg, INNO_SETUP_ISCC, PATH, fallback path."""
    if explicit:
        return Path(explicit)
    env = os.environ.get("INNO_SETUP_ISCC")
    if env:
        return Path(env)
    on_path = shutil.which("ISCC.exe")
    if on_path:
        return Path(on_path)
    fallback = Path(FALLBACK_INNO)
    return fallback if fallback.is_file() else None


def slim_exclusions(dist_dir: Path) -> tuple[set[str], list[str]]:
    """Return (excluded relative paths, warnings for missing targets).

    A missing exclusion target means upstream renamed or dropped a file and
    this list silently stopped matching; warn loudly instead of skipping.
    """
    excluded: set[str] = set()
    warnings: list[str] = []
    for rel, reason in SLIM_EXCLUDES.items():
        if (dist_dir / rel).is_file():
            excluded.add(rel)
        else:
            warnings.append(f"warning: slim exclusion target missing: {rel} ({reason})")
    return excluded, warnings


def make_zip(dist_dir: Path, zip_path: Path, exclude: set[str] | None = None) -> int:
    count = 0
    arc_root = zip_path.stem
    exclude = exclude or set()
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in sorted(dist_dir.rglob("*")):
            if path.is_file():
                rel = path.relative_to(dist_dir).as_posix()
                if rel in exclude:
                    continue
                zf.write(path, f"{arc_root}/{rel}")
                count += 1
    return count


def artifact_stem(version: str, edition: str) -> str:
    infix = "-slim" if edition == "slim" else ""
    return f"zzxsrv-{version}-x64{infix}"


def build_installer(args, iss: Path, inno: Path, excludes: set[str]) -> Path:
    out_name = f"{artifact_stem(args.version, args.edition)}-setup"
    # ISCC misparses forward slashes inside /D values as new options; pass
    # Windows-native separators.
    cmd = [
        str(inno),
        f"/DZxVersion={args.version}",
        f"/DZxDistDir={os.path.normpath(args.dist_dir)}",
        f"/DZxOutDir={os.path.normpath(args.output_dir)}",
        f"/DZxLicenseFile={ROOT / 'COPYING'}",
        f"/DZxOutName={out_name}",
        f"/DZxEdition={args.edition}",
    ]
    if excludes:
        # Same source list as the zip filter, handed to Inno's Excludes so the
        # installer mirrors the slim file set.
        cmd.append("/DZxExcludes=" + ",".join(sorted(excludes)))
    cmd.append(str(iss))
    subprocess.run(cmd, check=True)
    return Path(args.output_dir) / f"{out_name}.exe"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build ZzXsrv release artifacts")
    parser.add_argument("--dist-dir", required=True, help="portable runtime directory")
    parser.add_argument("--version", default=default_version())
    parser.add_argument("--edition", choices=EDITIONS, default="full")
    parser.add_argument("--output-dir", default=str(ROOT / "dist" / "release"))
    parser.add_argument("--inno", default=None,
                        help="path to ISCC.exe (default: $INNO_SETUP_ISCC, then PATH, "
                             f"then {FALLBACK_INNO})")
    parser.add_argument("--zip-only", action="store_true")
    args = parser.parse_args()

    dist_dir = Path(args.dist_dir)
    if not (dist_dir / "vcxsrv.exe").is_file():
        print(f"error: {dist_dir} is not a portable runtime (vcxsrv.exe missing)", file=sys.stderr)
        return 1

    excludes: set[str] = set()
    if args.edition == "slim":
        excludes, warnings = slim_exclusions(dist_dir)
        for warning in warnings:
            print(warning, file=sys.stderr)

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    zip_path = out_dir / f"{artifact_stem(args.version, args.edition)}-portable.zip"
    count = make_zip(dist_dir, zip_path, excludes)
    print(f"portable zip: {zip_path} ({count} files, {zip_path.stat().st_size} bytes)")

    if not args.zip_only:
        inno = resolve_inno(args.inno)
        if inno is None or not inno.is_file():
            print("error: Inno Setup compiler (ISCC.exe) not found; pass --inno, set "
                  "INNO_SETUP_ISCC, or add it to PATH", file=sys.stderr)
            return 1
        setup = build_installer(args, ROOT / "installer" / "zzxsrv-64.iss", inno, excludes)
        print(f"installer: {setup} ({setup.stat().st_size} bytes)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
