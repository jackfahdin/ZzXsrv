"""Build ZzXsrv release artifacts from a portable runtime directory.

Produces, under the output directory:
  zzxsrv-<version>-x64-portable.zip  - xcopy-runnable portable archive
  zzxsrv-<version>-x64-setup.exe     - Inno Setup installer (per-user by
                                       default, optional all-users via dialog)

Usage:
  python tools/package_release.py --dist-dir dist/x64/Release \
      [--version 2026.9.17] [--output-dir dist/release] \
      [--inno "D:\\SoftWare\\Inno Setup 7\\ISCC.exe"] [--zip-only]
"""

import argparse
import os
import subprocess
import sys
import zipfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INNO = r"D:\SoftWare\Inno Setup 7\ISCC.exe"


def default_version() -> str:
    today = date.today()
    return f"{today.year}.{today.month}.{today.day}"


def make_zip(dist_dir: Path, zip_path: Path) -> int:
    count = 0
    arc_root = zip_path.stem
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in sorted(dist_dir.rglob("*")):
            if path.is_file():
                zf.write(path, f"{arc_root}/{path.relative_to(dist_dir).as_posix()}")
                count += 1
    return count


def build_installer(args, iss: Path) -> Path:
    cmd = [
        args.inno,
        f"/DZxVersion={args.version}",
        f"/DZxDistDir={args.dist_dir}",
        f"/DZxOutDir={args.output_dir}",
        f"/DZxLicenseFile={ROOT / 'COPYING'}",
        f"/DZxOutName=zzxsrv-{args.version}-x64-setup",
        str(iss),
    ]
    subprocess.run(cmd, check=True)
    return Path(args.output_dir) / f"zzxsrv-{args.version}-x64-setup.exe"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build ZzXsrv release artifacts")
    parser.add_argument("--dist-dir", required=True, help="portable runtime directory")
    parser.add_argument("--version", default=default_version())
    parser.add_argument("--output-dir", default=str(ROOT / "dist" / "release"))
    parser.add_argument("--inno", default=DEFAULT_INNO, help="path to ISCC.exe")
    parser.add_argument("--zip-only", action="store_true")
    args = parser.parse_args()

    dist_dir = Path(args.dist_dir)
    if not (dist_dir / "vcxsrv.exe").is_file():
        print(f"error: {dist_dir} is not a portable runtime (vcxsrv.exe missing)", file=sys.stderr)
        return 1

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    zip_path = out_dir / f"zzxsrv-{args.version}-x64-portable.zip"
    count = make_zip(dist_dir, zip_path)
    print(f"portable zip: {zip_path} ({count} files, {zip_path.stat().st_size} bytes)")

    if not args.zip_only:
        if not Path(args.inno).is_file():
            print(f"error: Inno Setup compiler not found: {args.inno}", file=sys.stderr)
            return 1
        setup = build_installer(args, ROOT / "installer" / "zzxsrv-64.iss")
        print(f"installer: {setup} ({setup.stat().st_size} bytes)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
