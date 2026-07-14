#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path
from event_store import canonical_hash, read_events, reduce_events, verify_chain

ROOT = Path(__file__).resolve().parents[1]
POLICY = json.loads((ROOT/'config'/'enterprise-policy.json').read_text(encoding='utf-8'))
TRANSITIONS = {
 'DRAFT': {'PROPOSAL_REVIEW','CANCELLED'},
 'PROPOSAL_REVIEW': {'REQUIREMENTS_REVIEW','DRAFT','REJECTED','BLOCKED'},
 'REQUIREMENTS_REVIEW': {'DESIGN_REVIEW','PROPOSAL_REVIEW','REJECTED','BLOCKED'},
 'DESIGN_REVIEW': {'READY_FOR_IMPLEMENTATION','REQUIREMENTS_REVIEW','REJECTED','BLOCKED'},
 'READY_FOR_IMPLEMENTATION': {'IMPLEMENTING','DESIGN_REVIEW','CANCELLED','BLOCKED'},
 'IMPLEMENTING': {'VERIFYING','BLOCKED','CANCELLED'},
 'VERIFYING': {'RELEASE_READY','IMPLEMENTING','BLOCKED','REJECTED'},
 'RELEASE_READY': {'RELEASING','VERIFYING','CANCELLED'},
 'RELEASING': {'MONITORING','ROLLED_BACK','BLOCKED'},
 'MONITORING': {'CLOSED','ROLLED_BACK','BLOCKED'},
 'BLOCKED': {'DRAFT','PROPOSAL_REVIEW','REQUIREMENTS_REVIEW','DESIGN_REVIEW','READY_FOR_IMPLEMENTATION','IMPLEMENTING','VERIFYING','RELEASE_READY','RELEASING','MONITORING','CANCELLED'},
}
parser=argparse.ArgumentParser()
parser.add_argument('--change',required=True); parser.add_argument('--to',required=True)
parser.add_argument('--actor',required=True); parser.add_argument('--evidence',required=True)
parser.add_argument('--actor-role', required=True, choices=POLICY['allowed_roles'])
parser.add_argument('--reason', choices=['retrospective_governance_remediation'])
args=parser.parse_args()
choices=[d for d in (ROOT/'changes').glob(args.change+'*') if d.is_dir()]
if len(choices)!=1: raise SystemExit(f'Expected exactly one change directory, found {len(choices)}')
p=choices[0]/'state.json'; state=json.loads(p.read_text(encoding='utf-8'))
current=state['status']; target=args.to
if target not in TRANSITIONS.get(current,set()):
    raise SystemExit(f'Illegal transition: {current} -> {target}')
required_gate = POLICY['required_gate_for_target'].get(target)
if required_gate:
    approvals_dir = choices[0] / 'approvals'
    valid = []
    for approval_file in approvals_dir.glob('*.json') if approvals_dir.exists() else []:
        approval = json.loads(approval_file.read_text(encoding='utf-8'))
        rule = POLICY['gate_policy'][required_gate]
        is_example = state.get('change_id', '').startswith('CHG-EXAMPLE-')
        example_allowed = POLICY['trusted_identity'].get('allow_example_identity_for_example_changes') and is_example
        trusted_provider = (approval.get('identity_provider') in POLICY['trusted_identity']['providers']
                            or (example_allowed and approval.get('identity_provider') == 'example-oidc'))
        commit_bound = bool(approval.get('commit_sha')) or example_allowed
        if (approval.get('gate') == required_gate and approval.get('decision') == 'approved'
                and approval.get('actor_role') in rule['roles'] and trusted_provider and commit_bound):
            valid.append(approval)
    required_count = POLICY['gate_policy'][required_gate]['min_approvals']
    if len({a['actor_id'] for a in valid}) < required_count:
        raise SystemExit(f'{target} requires {required_count} valid approval(s) for {required_gate}')
events_path = choices[0] / 'events.jsonl'
events = read_events(events_path)
chain_errors = verify_chain(events)
if chain_errors:
    raise SystemExit('Invalid event chain: ' + '; '.join(chain_errors))
occurred_at = datetime.now(timezone(timedelta(hours=8))).isoformat()
payload = {'from': current, 'to': target, 'evidence': args.evidence}
if args.reason:
    payload['reason'] = args.reason
event = {
    'event_id': 'EVT-' + uuid.uuid4().hex.upper(), 'change_id': state['change_id'],
    'sequence': len(events) + 1, 'event_type': 'STATE_TRANSITIONED',
    'occurred_at': occurred_at, 'actor_id': args.actor, 'actor_role': args.actor_role,
    'payload': payload,
    'previous_hash': events[-1]['event_hash'] if events else None, 'commit_sha': None,
}
event['event_hash'] = canonical_hash(event)
with events_path.open('a', encoding='utf-8', newline='\n') as handle:
    handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + '\n')
state = reduce_events(events + [event])
p.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'{current} -> {target}')
