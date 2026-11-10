#!/usr/bin/env python3
"""Validate the bounded public naming correspondence."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def validate():
    contract = json.loads((ROOT / 'architecture/naming-contract.json').read_text())
    rows = contract['rows']
    assert len(rows) == 1833
    assert len({tuple(r['identity']) for r in rows}) == len(rows)
    assert sum(r['status'] == 'provisional' for r in rows) == 175
    assert all(r['open_question'] and r['target'] is None for r in rows if r['status'] == 'provisional')
    assert all(r['status'] in {'structural', 'unchanged', 'provisional'} for r in rows)
    renamed = [r for r in rows if r['status'] == 'structural']
    assert {':'.join(r['identity']) for r in renamed} == {
        'eebusruntime:NativeSnapshotV2.UseCases:serialized:usecases',
        'eebusruntime:SnapshotV1.UseCases:serialized:usecases',
        'eebusruntime:RedactedSnapshotV1.UseCases:serialized:usecases',
    }
    assert all(r['current_name'] == 'usecases' and r['target'] == 'use_cases' and r['public_evidence'] == [r['owning_file']] for r in renamed)
    assert all(r['target'] == r['current_name'] for r in rows if r['status'] == 'unchanged')
    assert all(r['public_evidence'] and r['owning_file'] in r['public_evidence'] for r in rows)
    schema = json.loads((ROOT / 'api/_candidate/msp-06/helianthus.eebus.mcp.v1.raw.schema.json').read_text())
    snapshot = schema['$defs']['OperatorSnapshotProfileV1']
    assert 'use_cases' in snapshot['required'] and 'usecases' not in snapshot['required']
    assert 'use_cases' in snapshot['properties'] and 'usecases' not in snapshot['properties']
    assert '`use_cases`' in (ROOT / 'api/_candidate/raw-snapshot-view-v1.md').read_text()
    print('naming contract: OK')

if __name__ == '__main__':
    validate()
