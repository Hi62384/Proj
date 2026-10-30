"""Generate one verified sample and probe the live Payhip create UI read-only."""
import json
import sys
from pathlib import Path
APP=Path(__file__).resolve().parents[1];sys.path[:0]=[str(APP),str(Path(__file__).resolve().parent),str(APP.parents[1])]
from assistant.storage import private_directory
from live_app import LiveApp


def main():
    if '--owner-authorized-readonly' not in sys.argv:raise SystemExit('Read-only owner scope required; account mutations are NOT authorized')
    app=LiveApp();conversation=app.new()
    prompt='''Prepare the next real Payhip integration test, READ ONLY on the account. Create one persistent project for an Inventory Reorder Planner integration-test product. Plan/generate/validate/package one product with id inventory-test, recipe inventory, title "Inventory Reorder Planner - Private Integration Test", illustrative price_cents 1900 and currency USD. Start the local pipeline; no real listing creation is authorized yet. While it runs, call projects.payhip_probe for this project. That is a host read-only Products/new-product-link inspection through the already owner-granted Payhip site scope; it must not upload, fill, click, save or publish. Report its actual observed controls, whether Invisible/Hidden is observable before upload/save, the exact form page and whether currency is visible. Do not infer unsupported controls. Then use bounded projects.wait calls to finish native QA and packaging, deliver the generated package into this chat and report its hash/size. Do not use any real account mutations, direct file/shell/desktop tools or other personal tabs. If projects.* is absent from this saved enum, use its files.read_approved projects.* compatibility alias. Finish with the concrete remaining account-authorization step; do not request it yourself in-app.'''
    result=app.send(conversation,prompt,900);out=private_directory()/'verification/payhip-preparation-20261029';out.mkdir(parents=True,exist_ok=True);(out/'results.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2),flush=True)
    if result['state']!='Completed':raise RuntimeError('Real preparation did not complete: '+result['state'])


if __name__=='__main__':main()
