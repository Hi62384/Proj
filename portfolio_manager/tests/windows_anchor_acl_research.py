"""Fail-closed research audit of opened Windows directories, not an authorization boundary."""
from contextlib import ExitStack


def audit_open_anchor(anchor, *, expected_identity, expected_owner, allowed_masks, required_masks):
    """Inspect one handle's owner and simple non-inherited allow ACEs.

    This does not validate ancestors, effective token access, integrity labels,
    later changes, or trusted provenance of any expected value.
    """
    import win32security

    if anchor.handle is None or not anchor.final_reparse_checked:
        raise ValueError('Anchor must be open and checked for a final reparse point')
    if anchor.identity != expected_identity:
        raise ValueError('Anchor identity mismatch')
    info = win32security.OWNER_SECURITY_INFORMATION | win32security.DACL_SECURITY_INFORMATION
    descriptor = win32security.GetSecurityInfo(anchor.handle, win32security.SE_FILE_OBJECT, info)
    owner = win32security.ConvertSidToStringSid(descriptor.GetSecurityDescriptorOwner())
    if owner != expected_owner:
        raise ValueError('Anchor owner mismatch')
    dacl = descriptor.GetSecurityDescriptorDacl()
    if dacl is None:
        raise ValueError('Null DACL is not acceptable')
    granted = {}
    for index in range(dacl.GetAceCount()):
        ace = dacl.GetAce(index)
        (ace_type, flags), mask, sid = ace
        if ace_type != win32security.ACCESS_ALLOWED_ACE_TYPE or flags & win32security.INHERITED_ACE:
            raise ValueError('Unsupported or inherited access entry')
        principal = win32security.ConvertSidToStringSid(sid)
        if principal not in allowed_masks or mask & ~allowed_masks[principal]:
            raise ValueError('Unexpected principal or access rights')
        granted[principal] = granted.get(principal, 0) | mask
    if any(granted.get(principal, 0) & required != required for principal, required in required_masks.items()):
        raise ValueError('Required explicit access entry is missing')
    return {'identity': anchor.identity, 'owner': owner, 'ace_count': dacl.GetAceCount()}


def audit_open_chain(anchor, policies):
    """Audit a pre-opened root and no-reparse children while retaining handles.

    The first policy describes the root; subsequent policies add a 'name'.
    This doesn't establish initial-root provenance or effective access.
    """
    if not isinstance(policies, (tuple, list)) or not 1 <= len(policies) <= 64:
        raise ValueError('Expected 1 to 64 policies')
    def check(handle, policy):
        return audit_open_anchor(handle, expected_identity=policy['identity'], expected_owner=policy['owner'],
                                 allowed_masks=policy['allowed_masks'], required_masks=policy['required_masks'])
    with ExitStack() as stack:
        results = [check(anchor, policies[0])]
        current = anchor
        for policy in policies[1:]:
            current = stack.enter_context(current.probe_open_child_handle(policy['name'], read_security=True))
            results.append(check(current, policy))
        return results
