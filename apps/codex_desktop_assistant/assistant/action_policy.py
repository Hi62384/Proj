"""Classify host-observed actions, never model-authored permission hints.

Text entry is not activation. Labels are only secondary evidence on an actual
activating control; matching fragments of a field name/document is insufficient.
"""
import re
from dataclasses import dataclass
from urllib.parse import urlsplit,parse_qs,unquote


@dataclass(frozen=True)
class Review:
    reason: str=''
    category: str='routine'

    @property
    def required(self):return bool(self.reason)


COMMIT=[
    (r'^(?:pay(?:\s|$)|purchase(?:\s|$)|buy(?:\s|$)|place (?:the |my )?order\b|confirm (?:the |my )?(?:order|purchase|payment)\b|complete (?:purchase|payment|checkout)\b|checkout\b|check out\b)', 'payment', 'This activates a purchase, payment or checkout control.'),
    (r'^(?:publish\b|unpublish\b|go live\b|make (?:public|live)\b|deploy\b|update (?:public |live )?(?:listing|storefront|website)\b|release (?:product|listing|website|site|version)\b|save(?: and)? (?:publish|send)\b)', 'publication', 'This activates a publication or deployment control and can change public content.'),
    (r'^(?:send\b|submit\b|post (?:message|comment|reply|review)\b|invite\b|subscribe\b|unsubscribe\b)', 'submission', 'This activates a send, submit or subscription control and may communicate externally.'),
    (r'^(?:delete\b|erase\b|remove$|remove (?:file|folder|account|product|listing|user|member|workspace|project)\b|empty (?:trash|recycle bin)\b|format (?:drive|disk)\b|reset (?:account|device|password)\b)', 'destructive', 'This activates a destructive or removal control.'),
    (r'^(?:transfer\b|refund\b|withdraw\b|change (?:password|credentials|security|authentication)\b|reset password\b|disable (?:mfa|two.factor|security)\b|grant (?:access|permission|administrator)\b|revoke (?:access|permission)\b|install\b|run (?:script|command|installer|macro|program|executable)\b)', 'security', 'This can change funds, credentials, access rights or installed software.'),
]
NAVIGATION=re.compile(r'^(?:purchase|payment|order|security|privacy|subscription|publication|transfer|refund|verification) (?:history|details|settings|preferences|options|help|guide|status)\b',re.I)


def commit_label(label):
    text=re.sub(r'\s+',' ',str(label).replace('&','')).strip(' .:…').lower()
    if NAVIGATION.search(text):return Review()
    for pattern,category,reason in COMMIT:
        if re.search(pattern,text,re.I):return Review(reason,category)
    return Review()


def request_review(method,url):
    """Backstop known consequential HTTP dispatch, without substring URL bans."""
    method=method.upper();parts=urlsplit(url)
    if method=='DELETE':return Review('The website is issuing an HTTP DELETE request.','destructive')
    for key,values in parse_qs(parts.query).items():
        if key.lower() in ('action','operation','command','do'):
            for value in values:
                result=commit_label(unquote(value).replace('_',' '))
                if result.required:return Review('The destination explicitly requests an action: '+result.reason,result.category)
    if method not in ('GET','HEAD','OPTIONS'):
        for segment in parts.path.split('/'):
            name=re.sub(r'([a-z])([A-Z])',r'\1 \2',unquote(segment)).replace('_',' ').replace('-',' ')
            result=commit_label(name)
            if result.required or name.lower()=='charge':
                return Review('The website is dispatching a consequential request to an explicit action endpoint.',result.category if result.required else 'submission')
    return Review()


def classify(operation,context):
    source=context.get('source','unknown');role=context.get('role','').lower();label=context.get('label','')
    key=str(context.get('key','')).upper()
    # A field named "Send message" or text mentioning a purchase is still data.
    if operation=='type' and source=='desktop' and role not in ('edit','document','combobox','textbox'):
        return Review('The target is not a verified text-editing control. Keyboard characters could activate this control instead of entering text.','unverified_target')
    if operation in ('type','fill','select','check','hover','focus','move_window','move_mouse','scroll','navigate','new_tab','switch_tab') or (source=='browser' and operation in ('tabs','close_tab','back','forward','reload','wait')):
        return Review()
    if operation=='upload':return Review('This transfers the attached file to the approved website.','submission')
    if operation=='drag' and source=='browser' and context.get('section_reorder') is True:
        return Review()  # Host-observed same-list draft editor sections only.
    if operation in ('coordinate_click','drag'):
        return Review('The pixel target has no verified semantic action; review this exact pointer operation.','unverified_target')
    if operation=='right_click':return Review()  # Opens a menu; later activation is classified separately.
    if context.get('explicit_action'):
        action=commit_label(context['explicit_action'].replace('_',' '))
        if action.required:return action
    if context.get('expands_menu') and (operation in ('click','double_click') or key in ('ENTER','RETURN')):return Review() if role in ('menuitem','menu item') else commit_label(label)
    if context.get('filesystem_activation') and (operation in ('click','double_click') or key in ('ENTER','RETURN')):
        return Review('This activates a filesystem or shell item and may open a file, execute a program, or change files. Desktop scope does not grant file-operation or code-execution permission.','filesystem')
    if operation in ('keypress','press'):
        if key=='CTRL+S':return Review('This asks the native application to save a file. Its exact path and configured file policy must be reviewed separately.','filesystem')
        if key not in ('ENTER','RETURN'):return Review()
        if source=='desktop' and not context.get('file_dialog') and role in ('edit','document','combobox') and (context.get('local_editor') or context.get('multiline')):return Review()
        if source=='browser' and context.get('tag')=='TEXTAREA' and not context.get('enter_submits'):return Review()
        if role in ('button','menuitem','hyperlink','link'):
            pass  # Enter activates the same host-observed control as a click.
        elif source=='browser' and context.get('form_method')=='GET' and not context.get('enter_submits'):
            return Review()
        elif not context.get('form_submission'):
            return Review('Enter in this target can activate a default button or send a form/message. Use semantic text entry for newlines; this is a key activation, not text insertion.','submission')
    elif operation not in ('click','double_click','right_click'):
        return Review('The action type cannot be verified as a routine operation.','unverified_target')
    if role in ('edit','document','combobox','textbox') and operation in ('click','double_click') and not context.get('form_submission') and (source!='browser' or context.get('editable')):return Review()
    if context.get('credential_form'):return Review('This activates a form containing credential fields and may change account access.','security')
    if context.get('local_editor') and not context.get('file_dialog'):
        if re.fullmatch(r'(?:delete|delete (?:line|selection)|remove formatting|clear formatting)',label.strip(),re.I):return Review()
        if re.fullmatch(r'save(?: as)?(?:\.\.\.|…)?',label.strip(),re.I):return Review('This native editor action saves a file; desktop editing does not grant direct file-write permission.','filesystem')
    result=commit_label(label)
    if result.required:return result
    if source=='browser' and re.fullmatch(r'save(?: changes| draft| product| listing)?',label.strip(),re.I) and not context.get('local_editor'):
        return Review('This save can persist account or website content. Its unpublished destination must be verified by an approved draft workflow.','submission')
    if context.get('form_submission'):
        if context.get('form_method')=='GET' and not context.get('enter_submits'):return Review()
        return Review('The target is an actual form submission control (method '+context.get('form_method','unknown')+'), rather than a text-editing operation.','submission')
    return Review()
