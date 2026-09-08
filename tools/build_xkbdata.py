"""Install core XKB data natively with Python 3.11+ and Perl, without Meson.

Matches compat-rules=true and xorg-rules-copy=true. Gettext translation catalogs
are outside this core data build. Fixed literal lists come from the checked-in
Meson files; this is deliberately not a general Meson interpreter.
"""

import argparse
import ast
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile


def literal_assignments(text, name, kind, count=1):
    """Read only standalone Meson list/dict literals, rejecting syntax drift."""
    opening, closing = ("[", "]") if kind is list else ("{", "}")
    pattern = (
        r"^\s*" + re.escape(name) + r"\s*(?:\+)?=\s*("
        + re.escape(opening) + r".*?^\s*" + re.escape(closing) + r")"
    )
    matches = re.findall(pattern, text, re.MULTILINE | re.DOTALL)
    if len(matches) != count:
        raise ValueError(f"Unsupported Meson declaration for {name}: expected {count} literal(s)")
    values = [ast.literal_eval(match) for match in matches]
    if any(type(value) is not kind for value in values):
        raise ValueError(f"Unsupported Meson literal for {name}")
    return values


def run_generator(source, executable, script, arguments):
    environment = os.environ.copy()
    environment.update(PYTHONUTF8="1", PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1")
    result = subprocess.run(
        [str(executable), str(script), *map(str, arguments)],
        cwd=source,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode:
        details = result.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"{script.name} failed ({result.returncode}): {details}")
    return result.stdout


def ignored_data(directory, names):
    # This checkout adds mhmake recipes to the upstream data directories.
    return [
        name for name in names
        if name.lower() in {"makefile", "meson.build", "__pycache__", "custom"}
        or Path(name).suffix.lower() in {".mk", ".mak", ".py", ".pyc"}
    ]


def symbol_aliases(source, aliases):
    """Resolve upstream symlinks that this checkout stores as regular copies."""
    symbols = source / "symbols"
    canonical = {
        path.name: path.read_bytes() for path in symbols.iterdir()
        if path.is_file() and path.name not in aliases
    }
    result = {}
    for alias in aliases:
        path = symbols / alias
        if path.is_symlink():
            result[alias] = path.resolve().name
            continue
        matches = [name for name, content in canonical.items() if content == path.read_bytes()]
        if len(matches) != 1:
            raise ValueError(f"Cannot identify unique canonical symbols file for {alias}")
        result[alias] = matches[0]
    return result


def install(source, output, perl):
    source = source.resolve()
    output = output.resolve()
    if source == output or source in output.parents or output in source.parents:
        raise ValueError("source and output paths must not overlap")
    if sys.version_info < (3, 11):
        raise ValueError("Python 3.11 or newer is required by the XKB generators")
    rules = source / "rules"
    rules_meson = (rules / "meson.build").read_text(encoding="utf-8")
    symbols_meson = (source / "symbols" / "meson.build").read_text(encoding="utf-8")
    root_meson = (source / "meson.build").read_text(encoding="utf-8")
    parts, compat_parts = literal_assignments(rules_meson, "parts", list, count=2)
    generated, = literal_assignments(rules_meson, "generated", list)
    symlinks, = literal_assignments(symbols_meson, "symlinks", list)
    aliases = symbol_aliases(source, symlinks)
    mapping_tables = []
    for name, mapping, flags in (
        ("lvl_ml_s", "layoutsMapping.lst", []),
        ("lvl_mlv_s", "variantsMapping.lst", ["--has-variant"]),
        ("lvl_mlv_s_vendors", "variantsMapping-vendors.lst", ["--has-variant", "--vendor"]),
    ):
        table, = literal_assignments(rules_meson, name, dict)
        if set(table) != {str(level) for level in range(5)}:
            raise ValueError(f"Unsupported compatibility levels in {name}")
        mapping_tables.append((table, mapping, flags))
    directory_match = re.search(r"foreach dir:\s*(\[[^\]]*\])", root_meson)
    if directory_match is None:
        raise ValueError("Missing Meson core data directory list")
    directories = ast.literal_eval(directory_match.group(1))
    if directories != ["compat", "geometry", "keycodes", "types"]:
        raise ValueError("Unsupported Meson core data directory list")
    install_match = re.search(r"install_data\((.*?)install_dir:", rules_meson, re.DOTALL)
    if install_match is None:
        raise ValueError("Missing Meson rules install_data list")
    rule_data = ast.literal_eval("[" + install_match.group(1) + "]")

    with tempfile.TemporaryDirectory(prefix="vcxsrv-xkb-") as temporary:
        work = Path(temporary)
        stage = work / "install"
        stage_rules = stage / "rules"
        stage_rules.mkdir(parents=True)
        for directory in directories:
            shutil.copytree(source / directory, stage / directory, ignore=ignored_data)
        shutil.copytree(
            source / "symbols", stage / "symbols",
            ignore=lambda directory, names: ignored_data(directory, names) + (
                [name for name in names if name in symlinks]
                if Path(directory) == source / "symbols" else []
            ),
        )
        for filename in rule_data:
            shutil.copyfile(rules / filename, stage_rules / filename)

        generated_parts = []
        for filename, section in generated:
            part = work / filename
            content = run_generator(source, sys.executable, rules / "generate-options-symbols.py", [
                "--rules-section=" + section, "--xkb-config-root", source,
                rules / "base.xml", rules / "base.extras.xml",
            ])
            if section == "symbols":
                # Upstream resolves actual symlinks itself. Materialized copies
                # need the same canonical names because aliases are not installed.
                for alias, canonical in aliases.items():
                    content = content.replace(
                        ("+" + alias + "(").encode("ascii"),
                        ("+" + canonical + "(").encode("ascii"),
                    )
            part.write_bytes(content)
            generated_parts.append(part)
        mapper = rules / "compat" / "map-variants.py"
        for table, mapping, flags in mapping_tables:
            for level, filename in table.items():
                part = work / filename
                run_generator(source, sys.executable, mapper, [
                    "--number=" + level, *flags, part, rules / "compat" / mapping,
                ])
                generated_parts.append(part)
        run_generator(source, sys.executable, mapper, [
            "--symbols", "--has-variant", stage / "symbols",
            rules / "compat" / "variantsMapping.lst",
        ])

        for ruleset in ("base", "evdev"):
            source_parts = [rules / part.replace("@0@", ruleset) for part in parts + compat_parts]
            (stage_rules / ruleset).write_bytes(run_generator(
                source, sys.executable, rules / "merge.py", source_parts + generated_parts,
            ))
            for suffix in (".xml", ".extras.xml"):
                shutil.copyfile(rules / ("base" + suffix), stage_rules / (ruleset + suffix))
            (stage_rules / (ruleset + ".lst")).write_bytes(run_generator(
                source, perl, rules / "xml2lst.pl", [stage_rules / (ruleset + ".xml")],
            ))
        for suffix in ("", ".xml", ".lst"):
            shutil.copyfile(stage_rules / ("base" + suffix), stage_rules / ("xorg" + suffix))

        # Publish only after every generator succeeds. Update the success marker
        # last, so mhmake retries an interrupted or failed installation.
        shutil.copytree(stage, output, dirs_exist_ok=True)
        stamp = output / ".native-build.stamp"
        temporary_stamp = output / ".native-build.stamp.tmp"
        temporary_stamp.write_text("Native XKB core data build completed.\n", encoding="utf-8")
        temporary_stamp.replace(stamp)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--perl", default="perl", help="Native Perl executable")
    arguments = parser.parse_args()
    try:
        install(arguments.source, arguments.output, arguments.perl)
    except (OSError, ValueError, SyntaxError, RuntimeError) as error:
        parser.exit(1, f"error: {error}\n")


if __name__ == "__main__":
    main()
