"""Owner-enabled routine approvals. Unknown or consequential scopes still ask."""
import re
from pathlib import Path
from urllib.parse import urlsplit
from assistant.permissions import origin,Denied

PROJECT_ROOT=Path(__file__).resolve().parents[3]
PROTECTED={'payment','publication','security','destructive','filesystem','unverified_target'}


def explicit_file_rule(policy,path,action):
    path=Path(path).resolve()
    for rule in policy.rules+policy.session:
        root=Path(rule['path']);scope=rule['scope']
        if action not in rule['decisions']:continue
        if path==root or scope=='folder' and path.parent==root or scope=='recursive' and path.is_relative_to(root):return True
    return False


def routine_reason(details,*,file_policy,roots,authorized_origins):
    """Only host-observed context is passed here, never model approval flags."""
    if details.get('manual_step') or details.get('approval_category') in PROTECTED:return None
    operation=details.get('operation')
    if details.get('file_permission'):
        if operation!='read' or details.get('expected',{}).get('kind') not in ('file','folder'):return None
        path=Path(details.get('path','')).resolve()
        # Independent explicit Ask/Deny rules retain their original meaning.
        if explicit_file_rule(file_policy,path,'read') or file_policy.decision(path,'read')=='deny':return None
        if any(path.is_relative_to(Path(root).resolve()) for root in roots):return 'Read or list ordinary project content; protected locations and explicit file rules remain enforced.'
        return None
    context=details.get('target_context',{})
    if operation=='existing_tab_reference':
        query=details.get('query','')
        try:
            if urlsplit(query).scheme in ('http','https') and origin(query) in authorized_origins:return 'Reuse an exact URL within an already authorized website.'
        except (Denied,ValueError):pass
        return None
    if operation=='website_access' and details.get('chrome_tab') and details.get('origin') in authorized_origins:
        return 'Attach a tab within the website access already granted in this session.'
    if operation=='chrome_screenshot' and context.get('origin') in authorized_origins:
        return 'Observe an already authorized Chrome tab; foreground, frame and sensitive-screen checks still apply.'
    # A platform-specific existing PRIVATE product save, not a generic POST
    # exemption. Uploads, public changes, new listings and unknown forms ask.
    if operation!='click' or details.get('approval_category')!='submission':return None
    if context.get('source')!='browser' or context.get('credential_form') is not False:return None
    if not context.get('form_submission') or context.get('form_visibility')!='invisible':return None
    if context.get('form_method')!='POST' or context.get('form_id')!='addproduct':return None
    try:
        page=urlsplit(context.get('page_url',''))
        same=origin(context['page_url']) in authorized_origins
    except (Denied,ValueError,KeyError):return None
    if same and page.scheme=='https' and page.netloc=='payhip.com' and re.fullmatch(r'/product/edit/[A-Za-z0-9]+',page.path) and context.get('form_action')=='https://payhip.com/product/editit' and context.get('label','').strip().lower()=='save changes':
        return 'Save edits to the existing Invisible Payhip product; public visibility, uploads and payments remain separately reviewed.'
    return None
