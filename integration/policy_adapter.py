"""Host adapter helpers; the bundled GdprRouter and Rego files stay unchanged."""
import json
import math
import secrets
from pathlib import Path
from .privacy_lib.gdpr_router import GdprRouter

POLICIES = {
    'consent': (), 'lawful': (), 'information': (), 'access': (),
    'rectification': ('request_id', 'updates'),
    'erasure': ('request_id', 'reason', 'fields'),
    'restriction': ('request_id', 'reason', 'fields'),
    'portability': ('request_id', 'transfer_requested', 'transfer_service_id'),
    'objection': ('request_id', 'reason', 'fields'),
    'complaint': ('request_id', 'authority_id', 'description'),
    'breach': ('incident_id', 'detected', 'hours_since_detected', 'risks', 'summary'),
}

class InvalidInput(ValueError):
    pass

def decode(raw):
    if len(raw) > 16384:
        raise OverflowError('Request too large')
    try:
        value = json.loads(raw, parse_constant=lambda _: (_ for _ in ()).throw(ValueError('Nonfinite JSON')))
    except (ValueError, UnicodeDecodeError) as exc:
        raise InvalidInput('Invalid JSON') from exc
    if not isinstance(value, dict):
        raise InvalidInput('JSON object required')
    return value

def validate(policy, value, fields, mutable, write=False):
    if policy not in POLICIES:
        raise InvalidInput('Unknown GDPR operation')
    allowed = ('value', 'withdrawn') if write else POLICIES[policy]
    if set(value) - set(allowed):
        raise InvalidInput('Unknown request field')
    for key, item in value.items():
        if key in ('withdrawn', 'detected', 'transfer_requested'):
            if type(item) is not bool:
                raise InvalidInput(key + ' must be boolean')
        elif key == 'hours_since_detected':
            if type(item) not in (int, float) or not math.isfinite(item) or item < 0:
                raise InvalidInput('Invalid incident time')
        elif key in ('fields', 'risks'):
            choices = fields if key == 'fields' else ('rights_freedoms', 'identity_theft', 'discrimination', 'financial_loss', 'reputational_damage', 'minor')
            if not isinstance(item, list) or not item or len(item) > len(choices):
                raise InvalidInput('Invalid ' + key)
            if any(not isinstance(x, str) or x not in choices for x in item) or len(set(item)) != len(item):
                raise InvalidInput('Invalid ' + key)
        elif key == 'updates':
            if not isinstance(item, dict) or not item:
                raise InvalidInput('Updates must be a nonempty object')
            for field, updated in item.items():
                if field not in mutable or not isinstance(updated, str) or not updated.strip() or len(updated) > 200:
                    raise InvalidInput('Invalid update')
                if field == 'email' and ('@' not in updated or any(c.isspace() for c in updated)):
                    raise InvalidInput('Invalid email')
        elif not isinstance(item, str) or not item or len(item) > (2000 if key in ('description', 'summary') else 128):
            raise InvalidInput('Invalid ' + key)
    required = ('value', 'withdrawn') if write else {'rectification': ('updates',), 'complaint': ('authority_id', 'description'), 'breach': ('incident_id',)}.get(policy, ())
    if any(key not in value for key in required):
        raise InvalidInput('Required field missing')
    if write and value['value'] not in ('yes', 'no'):
        raise InvalidInput('Invalid consent value')
    return value

def evaluate(policy, values, user_id, consent, request):
    config = json.loads((Path(__file__).parent / 'privacy-config.json').read_text(encoding='utf-8'))
    data = {k: config[k] for k in ('controller', 'dpo', 'storage', 'lawful_purposes', 'third_parties', 'services', 'exceptions', 'supervisory_authorities') if k in config}
    data['consents'] = {user_id: consent} if consent else {}
    data['users'] = [{'id': user_id, 'data_items': [{'field': field, 'value': value, 'purpose': 'contract', 'source': 'user', 'purpose_presented': True} for field, value in values.items()]}]
    data['request'] = {}
    if policy == 'access':
        data['request']['access'] = {'user_id': user_id}
    if policy in ('rectification', 'erasure', 'restriction', 'portability', 'objection', 'complaint'):
        part = dict(config.get('request_defaults', {}).get(policy, {}))
        if policy == 'portability':
            part.update(transfer_requested=False, transfer_service_id='')
        part.update(request)
        part.update(user_id=user_id, target_user_id=user_id, request_id=request.get('request_id', secrets.token_hex(16)))
        data['request'][policy] = part
    if policy == 'breach':
        data['breach'] = {**config['breach_defaults'], **request, 'affected_users': [user_id]}
    return GdprRouter().route(policy, data, user_id)
