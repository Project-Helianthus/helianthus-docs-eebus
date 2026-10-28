from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tests.test_msp_055_api_freeze import load_validator


class MSP055ExamplePathTests(unittest.TestCase):
    def test_examples_compile_from_escaped_local_source_paths(self) -> None:
        validator = load_validator()
        local_env = dict(os.environ, GOTOOLCHAIN="local", GOWORK="off")
        version = subprocess.run(
            ["go", "env", "GOVERSION"], env=local_env,
            check=True, capture_output=True, text=True,
        ).stdout.strip().removeprefix("go")
        with tempfile.TemporaryDirectory(prefix="msp-example-path-") as temporary:
            root = Path(temporary)
            source = root / 'source with spaces "quotes" and café'
            source.mkdir()
            (source / "go.mod").write_text(
                "module github.com/Project-Helianthus/helianthus-eebusreg\n"
                "\ngo 1.24.0\n", encoding="utf-8",
            )
            (source / "example.go").write_text(
                "package eebusreg\n\nfunc Example() {}\n", encoding="utf-8",
            )
            reference = root / validator.REFERENCE_REL
            reference.parent.mkdir(parents=True)
            for expression, expected in (
                ("eebusreg.Example()", set()),
                ("eebusreg.Undefined()", {"offline: example-compilation"}),
            ):
                with self.subTest(expression=expression):
                    reference.write_text(
                        "<!-- go-example:compile -->\n```go\npackage main\n\n"
                        'import "github.com/Project-Helianthus/helianthus-eebusreg"\n\n'
                        f"func main() {{ {expression} }}\n```\n", encoding="utf-8",
                    )
                    compilations = []

                    def runner(command, **kwargs):
                        # Use the installed toolchain: this regression tests path
                        # encoding, independently of frozen-source provenance.
                        kwargs["env"] = dict(
                            kwargs["env"], GOTOOLCHAIN="local",
                            GOPROXY="off", GOSUMDB="off",
                        )
                        result = subprocess.run(
                            command, capture_output=True, text=True, **kwargs
                        )
                        if command[1] == "test":
                            compilations.append(result)
                        return result

                    with patch.object(validator, "GO_VERSION", version):
                        errors = validator._example_errors(root, source, runner)
                    self.assertEqual(len(compilations), 1)
                    self.assertEqual(errors, expected, compilations[0].stderr)
                    self.assertEqual(compilations[0].returncode == 0, not expected)
