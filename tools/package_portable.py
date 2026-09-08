"""Copy the existing NSIS runtime file list without executing an installer.

Only File and SetOutPath declarations in the required/Fonts sections are read.
Registry, shortcuts, uninstall and other installer actions are never executed.
"""
import argparse
from pathlib import Path
import re
import shutil


def package(manifest, crt_directory, output):
    output = output.resolve()
    files = []
    active = False
    destination = Path()
    sections = set()
    for line in manifest.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        section = re.fullmatch(r'Section "([^"]+)"', line)
        if section:
            active = section[1] in {"VcXsrv (required)", "Fonts"}
            if active:
                sections.add(section[1])
            continue
        if line == "SectionEnd":
            active = False
        if not active:
            continue
        target = re.fullmatch(r'SetOutPath \$INSTDIR(?:\\(.*))?', line)
        if target:
            destination = Path((target[1] or "").replace("\\", "/"))
            if destination.is_absolute() or ".." in destination.parts:
                raise ValueError(f"Unsupported output path: {line}")
            continue
        entry = re.fullmatch(r'File\s+(/r\s+)?"([^"]+)"', line)
        if not entry:
            if line.startswith("File ") or line.startswith("SetOutPath "):
                raise ValueError(f"Unsupported runtime declaration: {line}")
            continue
        source = Path(entry[2].replace("\\", "/"))
        if entry[1]:
            if source.name != "*.*":
                raise ValueError(f"Unsupported recursive declaration: {line}")
            source = (manifest.parent / source.parent).resolve()
            if source == output or source in output.parents or output in source.parents:
                raise ValueError(f"Output must be separate from runtime data: {source}")
            if not source.is_dir():
                raise FileNotFoundError(f"Missing runtime data directory: {source}")
            contents = [path for path in source.rglob("*") if path.is_file()]
            if not contents:
                raise FileNotFoundError(f"Empty runtime data directory: {source}")
            files.extend((path, destination / path.relative_to(source)) for path in contents)
        else:
            # The installer receives these CRT files from packageall.sh.
            base = crt_directory if len(source.parts) == 1 else manifest.parent
            source = (base / source).resolve()
            files.append((source, destination / source.name))
    if sections != {"VcXsrv (required)", "Fonts"}:
        raise ValueError("Missing expected runtime sections in NSIS manifest")
    # Include companion runtime DLLs used by newer MSVC standard libraries.
    files.extend((path.resolve(), Path(path.name)) for path in crt_directory.glob("*.dll"))
    for source, relative in files:
        if not source.is_file():
            raise FileNotFoundError(f"Missing runtime file; build the selected configuration first: {source}")
        if output == source.parent or output in source.parents:
            raise ValueError(f"Output must be separate from runtime inputs: {source}")
        target = (output / relative).resolve()
        if output not in target.parents:
            raise ValueError(f"Output escapes runtime folder: {target}")
    # All inputs are checked before creating/updating the runtime directory.
    for source, relative in files:
        target = output / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    print(f"Portable runtime ready: {output} ({len(files)} files)")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--crt-directory", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        package(args.manifest.resolve(), args.crt_directory.resolve(), args.output)
    except (OSError, ValueError) as error:
        parser.exit(1, f"error: {error}\n")


if __name__ == "__main__":
    main()
