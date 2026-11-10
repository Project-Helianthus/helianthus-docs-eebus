import importlib.util
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('naming_contract', ROOT / 'scripts/check_naming_contract.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)

def test_contract():
    checker.validate()

def test_schema_rejects_old_key(tmp_path, monkeypatch):
    import json
    contract = tmp_path / 'architecture/naming-contract.json'
    contract.parent.mkdir(parents=True)
    contract.write_bytes((ROOT / 'architecture/naming-contract.json').read_bytes())
    schema = tmp_path / 'api/_candidate/msp-06/helianthus.eebus.mcp.v1.raw.schema.json'
    schema.parent.mkdir(parents=True)
    data = json.loads((ROOT / schema.relative_to(tmp_path)).read_text())
    data['$defs']['OperatorSnapshotProfileV1']['properties']['usecases'] = data['$defs']['OperatorSnapshotProfileV1']['properties']['use_cases']
    schema.write_text(json.dumps(data))
    monkeypatch.setattr(checker, 'ROOT', tmp_path)
    with pytest.raises(AssertionError):
        checker.validate()

@pytest.mark.parametrize('component', range(4))
def test_structural_identity_components_are_checked(tmp_path, monkeypatch, component):
    import json
    contract = tmp_path / 'architecture/naming-contract.json'
    contract.parent.mkdir(parents=True)
    data = json.loads((ROOT / 'architecture/naming-contract.json').read_text())
    row = next(r for r in data['rows'] if r['status'] == 'structural')
    row['identity'][component] += '_changed'
    contract.write_text(json.dumps(data))
    monkeypatch.setattr(checker, 'ROOT', tmp_path)
    with pytest.raises(AssertionError):
        checker.validate()
