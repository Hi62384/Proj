"""Real saved-model/installed-extension broad browsing, no attached tab setup."""
import json
import sys
from pathlib import Path
APP=Path(__file__).resolve().parents[1];sys.path[:0]=[str(APP),str(Path(__file__).resolve().parent),str(APP.parents[1])]
from assistant.storage import private_directory
from live_app import LiveApp


def main():
    if '--approve-synthetic-tests' not in sys.argv:raise SystemExit('Browser test opt-in required')
    root=private_directory();health=json.loads((root/'chrome-health.json').read_text())
    if not health.get('full_browser'):raise SystemExit('Owner must enable Full Browser Access through Chrome first')
    app=LiveApp();conversation=app.new()
    result=app.send(conversation,'''Verify owner-enabled Full Browser Access using only chrome.* tools. Start with no manually attached tab. List tabs and remember active tabs without inspecting unrelated pages. Create one new background tab for https://example.org and another for https://example.com. Inspect only your two new tabs and verify Example Domain text. Do not show/activate tabs, use desktop/files/screenshots, submit forms or access any personal account. Close only the two tabs you created, then list tabs to verify both removed and prior active tabs unchanged. Do not ask for routine website or conversation attachment approvals; host Full Browser scope is already enabled. Report actual outcomes and any network blocker without claiming success on a failed page.''',240)
    out=root/'verification/autonomous-browser-20261029';out.mkdir(parents=True,exist_ok=True)
    actions=result['actions'];result['two_tabs_created']=sum(a['operation']=='chrome.open_tab' and a['state']=='completed' for a in actions)==2
    result['two_tabs_closed']=sum(a['operation']=='chrome.close_tab' and a['state']=='completed' for a in actions)==2
    result['zero_approval_or_manual_cards']=not app.rows("SELECT id FROM messages WHERE conversation=? AND state='Waiting for local approval'",(conversation,))
    result['complete']=result['state']=='Completed' and result['two_tabs_created'] and result['two_tabs_closed'] and result['zero_approval_or_manual_cards']
    (out/'results.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2),flush=True)
    assert result['complete']


if __name__=='__main__':main()
