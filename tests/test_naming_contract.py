import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class NamingContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Reduced policy fixtures deliberately omit the fixture builder and may
        # replace the validator with a stub to isolate shell content checks.
        for relative in ('tests/policy_test_support.py',
                         'scripts/check_naming_contract.py',
                         'architecture/naming-contract.json'):
            if not (ROOT / relative).is_file():
                raise unittest.SkipTest(f'missing naming contract prerequisite: {relative}')
        spec = importlib.util.spec_from_file_location(
            'naming_contract', ROOT / 'scripts/check_naming_contract.py')
        cls.checker = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.checker)

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        for name in (
            'architecture/naming-contract.json',
            'api/_candidate/msp-06/helianthus.eebus.mcp.v1.raw.schema.json',
            'api/_candidate/raw-snapshot-view-v1.md',
        ):
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((ROOT / name).read_bytes())
        self.path = self.root / 'architecture/naming-contract.json'
        self.contract = json.loads(self.path.read_text())

    def test_contract(self):
        self.checker.validate()

    def test_schema_rejects_old_key(self):
        schema = self.root / 'api/_candidate/msp-06/helianthus.eebus.mcp.v1.raw.schema.json'
        data = json.loads(schema.read_text())
        properties = data['$defs']['OperatorSnapshotProfileV1']['properties']
        properties['usecases'] = properties['use_cases']
        schema.write_text(json.dumps(data))
        with self.assertRaises(AssertionError):
            self.checker.validate(self.root)

    def test_structural_identity_components_are_checked(self):
        row = next(r for r in self.contract['rows'] if r['status'] == 'structural')
        for component in range(4):
            with self.subTest(component=component):
                row['identity'][component] += '_changed'
                self.path.write_text(json.dumps(self.contract))
                with self.assertRaises(AssertionError):
                    self.checker.validate(self.root)
                row['identity'][component] = row['identity'][component].removesuffix('_changed')

    def test_method_identities(self):
        methods = [r for r in self.contract['rows'] if r['kind'] == 'go_func'
                   and len(r['identity']) == 5 and r['identity'][3] != 'package']
        self.assertTrue(methods)
        for row in methods:
            with self.subTest(identity=row['identity']):
                self.assertNotRegex(row['identity'][3], r'[()]')
                self.assertEqual(row['identity'][4], row['current_name'])
                self.assertEqual(row['target'], row['current_name'])
        clone = next(r for r in methods if r['identity'][3] == 'snapshot SnapshotV1'
                     and r['identity'][4] == 'Clone')
        self.assertEqual(clone['target'], 'Clone')
        locator = next(r for r in methods if r['identity'][3] == 'target FeatureTargetV1'
                       and r['identity'][4] == 'Locator')
        self.assertEqual(locator['target'], 'Locator')

    def test_rejects_absorbed_method_name(self):
        row = next(r for r in self.contract['rows'] if r['identity'][-2:] ==
                   ['snapshot SnapshotV1', 'Clone'])
        row['identity'][-2:] = ['snapshot SnapshotV1) Clone(', 'SnapshotV1']
        row['current_name'] = row['target'] = 'SnapshotV1'
        self.path.write_text(json.dumps(self.contract))
        with self.assertRaisesRegex(AssertionError, 'invalid method receiver'):
            self.checker.validate(self.root)

    def test_repository_policy_rejects_invented_target(self):
        row = next(r for r in self.contract['rows'] if r['status'] == 'unchanged')
        row['target'] = 'invented_target'
        self.path.write_text(json.dumps(self.contract))
        # Invoke the required gate on a candidate root, not only the standalone checker.
        result = subprocess.run(
            [sys.executable, str(ROOT / 'scripts/validate_repository_policy.py'),
             '--repo', str(self.root)], capture_output=True, text=True, check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('invalid naming contract', result.stderr)

    def test_both_ci_entry_points_register_tests(self):
        self.assertIn('python3 -m unittest tests.test_naming_contract',
                      (ROOT / 'scripts/ci_local.sh').read_text())
        self.assertIn('run: python3 -m unittest tests.test_naming_contract',
                      (ROOT / '.github/workflows/docs-ci.yml').read_text())

    def test_policy_fixture_explicitly_skips_suite_but_enforces_contract(self):
        from tests.policy_test_support import materialize_policy_fixture

        root = materialize_policy_fixture(self.root / 'policy-fixture')
        result = subprocess.run(
            [sys.executable, '-m', 'unittest', 'tests.test_naming_contract', '-v'],
            cwd=root, capture_output=True, text=True, check=False, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('Ran 0 tests', result.stderr)
        self.assertIn('OK (skipped=1)', result.stderr)
        self.assertIn('tests/policy_test_support.py', result.stderr)
        contract_path = root / 'architecture/naming-contract.json'
        contract = json.loads(contract_path.read_text())
        row = next(r for r in contract['rows'] if r['status'] == 'unchanged')
        row['target'] = 'invented_target'
        contract_path.write_text(json.dumps(contract))
        result = subprocess.run(
            [sys.executable, str(root / 'scripts/validate_repository_policy.py'),
             '--repo', str(root)],
            cwd=root, capture_output=True, text=True, check=False, timeout=30,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('invalid naming contract', result.stderr)

    def test_discovery_skips_when_prerequisites_are_missing(self):
        for missing in ('tests/policy_test_support.py',
                        'scripts/check_naming_contract.py',
                        'architecture/naming-contract.json'):
            with self.subTest(missing=missing):
                root = self.root / Path(missing).stem
                tests = root / 'tests'
                tests.mkdir(parents=True)
                (tests / 'test_naming_contract.py').write_bytes(
                    Path(__file__).read_bytes())
                for relative in ('tests/policy_test_support.py',
                                 'scripts/check_naming_contract.py',
                                 'architecture/naming-contract.json'):
                    if relative != missing:
                        target = root / relative
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_bytes((ROOT / relative).read_bytes())
                result = subprocess.run(
                    [sys.executable, '-m', 'unittest', 'discover', '-s',
                     str(tests), '-p', 'test_naming_contract.py', '-v'],
                    cwd=root, capture_output=True, text=True, check=False,
                    timeout=30,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn('Ran 0 tests', result.stderr)
                self.assertIn('OK (skipped=1)', result.stderr)
                self.assertIn(missing, result.stderr)

    def test_missing_candidate_file_has_contract_diagnostic(self):
        schema = self.root / 'api/_candidate/msp-06/helianthus.eebus.mcp.v1.raw.schema.json'
        schema.rename(self.root / 'saved-schema.json')
        errors = self.checker.naming_contract_errors(self.root)
        self.assertEqual(errors, [
            'architecture/naming-contract.json: invalid naming contract: missing referenced file: '
            'api/_candidate/msp-06/helianthus.eebus.mcp.v1.raw.schema.json'])

    def test_missing_api_preserves_owner_domain_diagnostic(self):
        from tests.policy_test_support import materialize_policy_fixture, check_repository_result

        root = materialize_policy_fixture(self.root / 'missing-api-fixture')
        (root / 'api').rename(self.root / 'saved-api')
        result = check_repository_result(root)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('invalid naming contract: missing referenced file', result.stderr)
        self.assertIn('path-domain owner must be a directory', result.stderr)

    def test_missing_candidate_preserves_preflight_diagnostics(self):
        from tests.policy_test_support import materialize_policy_fixture, check_repository_result

        root = materialize_policy_fixture(self.root / 'missing-candidate-fixture')
        schema = root / 'api/_candidate/msp-06/helianthus.eebus.mcp.v1.raw.schema.json'
        schema.rename(self.root / 'saved-schema.json')
        result = check_repository_result(root)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('invalid naming contract: missing referenced file', result.stderr)
        self.assertIn('candidate machine artifact is missing', result.stderr)

    def test_contract_errors_preserve_prior_early_return_decision(self):
        from tests import policy_test_support
        from validate_repository_policy import _append_naming_contract_errors

        self.assertTrue(callable(policy_test_support.check_repository))
        row = next(r for r in self.contract['rows'] if r['status'] == 'unchanged')
        row['target'] = 'invented_target'
        self.path.write_text(json.dumps(self.contract))
        for prior in ([], ['existing diagnostic']):
            with self.subTest(prior=prior):
                errors = prior.copy()
                self.assertEqual(_append_naming_contract_errors(self.root, errors), bool(prior))
                self.assertEqual(errors[:len(prior)], prior)
                self.assertIn('invalid naming contract', errors[-1])
