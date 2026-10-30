"""Real installed-Chrome custom-control acceptance with a fixed transport adapter.

No saved model or installed-extension claim is made by this lower-level suite.
"""
import argparse
import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock
from urllib.request import urlopen
APP=Path(__file__).resolve().parents[1];sys.path[:0]=[str(APP),str(Path(__file__).resolve().parent)]
from assistant.builder_fixture import BuilderFixture
from assistant.chrome_control import ChromeControl
from assistant.permissions import Permissions,origin
from assistant.storage import Store,private_directory
from assistant.attachments import Attachments
from chrome_dom_acceptance import Adapter


def main():
    if '--approve-synthetic-tests' not in sys.argv:raise SystemExit('Synthetic opt-in required')
    directory=private_directory()/'verification/complex-builder-20261029';directory.mkdir(parents=True,exist_ok=True);results={}
    def record(key,value=True):results[key]=value;(directory/'results.json').write_text(json.dumps(results,indent=2));print(key+': '+str(value),flush=True)
    fixture=BuilderFixture();from playwright.sync_api import sync_playwright
    try:
        with tempfile.TemporaryDirectory() as state,sync_playwright() as playwright:
            store=Store(Path(state));conversation=store.new();permissions=Permissions();permissions.resume(conversation)
            approve=Mock(return_value=False);controller=ChromeControl(permissions,store,approve,Mock(),Attachments(store.directory))
            browser=playwright.chromium.launch(channel='chrome',headless=True,chromium_sandbox=True)
            try:
                page=browser.new_page();page.goto(fixture.url);adapter=Adapter(page,(APP/'chrome_extension/content.js').read_text(encoding='utf-8'));adapter.call('grant',origin=origin(fixture.url))
                class Transport:
                    def status(self):return {'session':'session','tabs':[{'tab':7,'origin':origin(fixture.url),'manual':False}]}
                    def request(self,operation,args,guard=None,**kwargs):
                        if guard:guard()
                        response=adapter.call(operation,**{k:v for k,v in args.items() if k!='tab'})
                        if not response['ok']:raise RuntimeError(response.get('error'))
                        return response['result']
                controller.bridge=Transport();controller.attach(conversation,7,ask=False);controller.register_draft_fixture(conversation,fixture.url)
                def action(label,operation='click',**args):
                    snapshot=controller.call(conversation,'inspect',{'tab':7});found=next(c for c in snapshot['controls'] if c['label']==label)
                    controller.call(conversation,'action',{'tab':7,'operation':operation,'observation':snapshot['observation'],'element':found['element'],**args})
                action('About Me');assert page.locator('#about-panel').is_visible();action('About text','fill',text='Practical business tools\nCreated for small teams')
                action('Colors');action('Violet swatch');assert page.locator('#color').input_value()=='#7c3aed';action('Brand color','fill',text='#125e77')
                action('Layout controls');action('Choose layout');action('Editorial layout');action('Show spacing menu','hover');action('Comfortable spacing')
                action('Save draft');page.wait_for_function("document.querySelector('#status').textContent==='Unpublished draft saved'")
                state=fixture.state;assert state['draft_saves']==1;assert state['publication_requests']==0 and state['payment_requests']==0
                assert state['dom']['color']=='#125e77' and state['dom']['layout']=='Editorial' and state['dom']['spacing']=='Comfortable',state
                assert state['saved']['about']==['Practical business tools\nCreated for small teams'];assert approve.call_count==0
                record('custom_sidebar_swatches_color_picker_dropdown_hover_and_rich_text');record('independent_server_verified_one_unpublished_draft');record('zero_routine_approvals')
                action('Publish');assert approve.call_count==1;assert state['publication_requests']==0
            except PermissionError:
                assert approve.call_count==1 and fixture.state['publication_requests']==0;record('out_of_scope_publication_denied');record('complete')
            finally:browser.close();store.close()
    finally:fixture.close()


if __name__=='__main__':main()
