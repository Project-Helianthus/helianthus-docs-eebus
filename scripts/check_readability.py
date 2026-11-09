"""Offline Ruff ratchet keyed by relative path, qualified symbol and rule."""

import argparse
import ast
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
RUFF_VERSION = "0.15.10"
BASELINE = ROOT / "scripts/readability-baseline.json"


def positive_count(value):
    if type(value) is not int or value < 1:
        raise ValueError("count must be a positive integer")
    return value


def record_key(record):
    if set(record) != {"path", "symbol", "rule", "count"}:
        raise ValueError("invalid baseline record fields")
    path = record["path"]
    if not isinstance(path, str) or not path:
        raise ValueError("invalid relative path")
    parsed = PurePosixPath(path)
    if (parsed.is_absolute() or ".." in parsed.parts or "\\" in path
            or str(parsed) != path or parsed.suffix != ".py"
            or parsed.parts[0] not in {"scripts", "tests"}):
        raise ValueError("invalid relative Python path")
    for field in ("symbol", "rule"):
        if not isinstance(record[field], str) or not record[field].strip():
            raise ValueError(f"invalid {field}")
    positive_count(record["count"])
    return path, record["symbol"], record["rule"]


def baseline_records(document):
    if (not isinstance(document, dict)
            or set(document) != {"schema", "ruff_version", "generation", "entries"}
            or type(document["schema"]) is not int or document["schema"] != 1
            or document["ruff_version"] != RUFF_VERSION
            or not isinstance(document["generation"], str)
            or not document["generation"].strip()
            or not isinstance(document["entries"], list)):
        raise ValueError("invalid baseline metadata")
    result = {}
    for record in document["entries"]:
        key = record_key(record)
        if key in result:
            raise ValueError(f"duplicate baseline record: {key}")
        result[key] = record["count"]
    return result


def symbol_ranges(source):
    ranges = []
    names = set()

    def visit(node, parents):
        scope = parents
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            scope = (*parents, node.name)
            name = ".".join(scope)
            if name in names:
                raise ValueError(f"ambiguous duplicate symbol: {name}")
            names.add(name)
            ranges.append((node.lineno, node.end_lineno, len(scope), name))
        for child in ast.iter_child_nodes(node):
            visit(child, scope)

    visit(ast.parse(source), ())
    return ranges


def diagnostic_record(item, root, sources):
    path = Path(item["filename"]).resolve()
    relative = path.relative_to(root.resolve()).as_posix()
    row = positive_count(item["location"]["row"])
    rule, message = item["code"], item["message"]
    if not isinstance(rule, str) or not isinstance(message, str):
        raise ValueError("invalid Ruff rule or message")
    if path not in sources:
        sources[path] = symbol_ranges(path.read_text(encoding="utf-8"))
    matching = [entry for entry in sources[path] if entry[0] <= row <= entry[1]]
    symbol = max(matching, key=lambda entry: entry[2])[3] if matching else "<module>"
    count = 1
    if rule in {"C901", "PLR0915"}:
        match = re.search(r"\((\d+) > \d+\)", message)
        if match is None:
            raise ValueError("missing measured Ruff count")
        count = positive_count(int(match[1]))
    record = dict(path=relative, symbol=symbol, rule=rule, count=count)
    record_key(record)
    return record


def parse_findings(output, root):
    items = json.loads(output, object_pairs_hook=reject_duplicate_keys)
    if not isinstance(items, list):
        raise ValueError("Ruff JSON must be an array")
    findings, sources = {}, {}
    for item in items:
        record = diagnostic_record(item, root, sources)
        key = record_key(record)
        if key in findings and record["rule"] in {"C901", "PLR0915"}:
            raise ValueError(f"duplicate measured diagnostic: {key}")
        findings[key] = findings.get(key, 0) + record["count"]
    return findings


def compare_findings(current, baseline):
    errors = []
    for key, count in sorted(current.items()):
        if key not in baseline:
            errors.append(f"new finding: {key}: {count}")
        elif count > baseline[key]:
            errors.append(f"grown finding: {key}: {baseline[key]} -> {count}")
    for key in sorted(baseline.keys() - current.keys()):
        errors.append(f"resolved or unused baseline entry; remove it: {key}")
    return errors


def run_ruff(root):
    version = subprocess.run(["ruff", "--version"], capture_output=True,
                             text=True, timeout=15, check=True)
    if version.stdout.strip() != f"ruff {RUFF_VERSION}":
        raise ValueError(f"requires Ruff {RUFF_VERSION}")
    result = subprocess.run(
        ["ruff", "check", "--no-cache", "--output-format=json", "--config",
         str(root / "ruff.toml"), "scripts", "tests"],
        cwd=root, capture_output=True, text=True, timeout=120,
    )
    if result.returncode not in {0, 1}:
        raise ValueError(f"Ruff tool failure ({result.returncode}): {result.stderr.strip()}")
    findings = parse_findings(result.stdout, root)
    if bool(findings) != bool(result.returncode):
        raise ValueError("Ruff status disagrees with JSON findings")
    return findings


def reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true")
    group.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        suite = unittest.defaultTestLoader.discover(
            str(ROOT / "tests"), pattern="test_readability_gate.py")
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        return 0 if result.testsRun and result.wasSuccessful() else 1
    try:
        document = json.loads(BASELINE.read_text(encoding="utf-8"),
                              object_pairs_hook=reject_duplicate_keys)
        baseline = baseline_records(document)
        current = run_ruff(ROOT)
        errors = compare_findings(current, baseline)
        if errors:
            print("\n".join(errors), file=sys.stderr)
            return 1
        print(f"Readability: {len(current)} measured records within baseline")
        return 0
    except (OSError, ValueError, KeyError, TypeError, SyntaxError,
            subprocess.SubprocessError) as error:
        print(f"Readability failed closed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
