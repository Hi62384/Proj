"""Shared paths and validation for the offline business factory."""
from __future__ import annotations
from decimal import Decimal, InvalidOperation
import json
import os
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
ATLAS = ROOT / 'research_merge' / 'opportunity_atlas_expanded.csv'
PRIVATE = ROOT / 'portfolio_autopilot' / '.local' / 'factory'
SAMPLE_PROFILE = Path(__file__).parent / 'templates' / 'seller_profile.example.json'
PROFILE_FIELDS = {'business_name', 'support_email', 'country', 'currency',
                  'monthly_external_spend_cap_cad', 'contact_url', 'approved_channels'}
ID_RE = re.compile(r'^[A-Za-z0-9][A-Za-z0-9_-]{0,79}$')

class SetupError(ValueError):
    pass

def safe_id(value: str) -> str:
    if not isinstance(value, str) or not ID_RE.fullmatch(value):
        raise SetupError('ID must be 1–80 ASCII letters, digits, hyphens, or underscores.')
    return value

def money(value: object) -> Decimal:
    try:
        n = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as e:
        raise SetupError('Expected a CAD decimal amount.') from e
    if not n.is_finite() or n < 0 or n.as_tuple().exponent < -2:
        raise SetupError('Amount must be non-negative with at most 2 decimal places.')
    return n

def private_path(relative: str, root: Path = PRIVATE) -> Path:
    """Restrict output to a private local folder. Reject symlink traversal."""
    parts = Path(relative)
    if parts.is_absolute() or not parts.parts or any(p in ('..', '.') for p in parts.parts):
        raise SetupError('Unsafe relative path.')
    base = root.resolve()
    target = (base / parts).resolve()
    if not target.is_relative_to(base):
        raise SetupError('Output would escape the private workspace.')
    return target

def init_private(root: Path = PRIVATE) -> Path:
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    if root.is_symlink():
        raise SetupError('Private workspace must not be a symlink.')
    try:
        if os.name != 'nt':
            root.chmod(0o700)
    except OSError:
        pass
    return root

def load_profile(path: Path | None = None) -> dict:
    path = path or (PRIVATE / 'seller_profile.json')
    if not path.exists():
        return { 'business_name': '[Your business name]',
                 'support_email': '[Your business email]', 'country': 'CA',
                 'currency': 'CAD', 'monthly_external_spend_cap_cad': '0',
                 'contact_url': '', 'approved_channels': [] }
    obj = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(obj, dict) or set(obj) - PROFILE_FIELDS:
        raise SetupError('Profile has unknown fields; never store credentials or identifiers here.')
    if obj.get('country', 'CA') != 'CA' or obj.get('currency', 'CAD') != 'CAD':
        raise SetupError('This prototype currently supports CAD/CA seller placeholders only.')
    money(obj.get('monthly_external_spend_cap_cad', '0'))
    for s in ('business_name','support_email','contact_url'):
        if not isinstance(obj.get(s, ''), str) or len(obj.get(s, '')) > 160:
            raise SetupError('Invalid profile field: '+s)
    if not isinstance(obj.get('approved_channels', []), list) or any(
        not isinstance(x, str) or x not in ('upwork', 'direct', 'marketplace')
        for x in obj.get('approved_channels', [])):
        raise SetupError('Invalid approved channels.')
    return obj

def bootstrap(root: Path = PRIVATE) -> Path:
    init_private(root)
    profile = root / 'seller_profile.json'
    if not profile.exists():
        profile.write_bytes(SAMPLE_PROFILE.read_bytes())
        if os.name != 'nt':
            profile.chmod(0o600)
    return profile
