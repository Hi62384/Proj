"""Native QA of declarative spreadsheet and editable Word/PDF checklist recipes."""
import argparse
import json
import sys
import time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from assistant.projects import ProjectQueue


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--approve-synthetic-tests',action='store_true');parser.add_argument('--directory',required=True);args=parser.parse_args()
    if not args.approve_synthetic_tests:raise SystemExit('Explicit synthetic opt-in required')
    root=Path(args.directory);root.mkdir(parents=True,exist_ok=True);q=ProjectQueue(root);results={}
    def record(key,value=True):results[key]=value;(root/'results.json').write_text(json.dumps(results,indent=2));print(key+': '+str(value),flush=True)
    try:
        p=q.create('owner','Generate and validate a sales worksheet and launch-readiness checklist')['project'];record('project',p)
        products=[{'id':'sales','recipe':'spreadsheet','title':'Sales Scenario Planner','purpose':'Compare revenue and gross contribution from unit price, quantity and unit costs.','sheets':[{'name':'Sales','rows':[['Units','Unit price','Revenue','Unit cost','Total cost','Contribution'],[25,40,None,15,None,None]],'calculations':[{'cell':'C2','operation':'product','inputs':['A2','B2']},{'cell':'E2','operation':'product','inputs':['A2','D2']},{'cell':'F2','operation':'difference','inputs':['C2','E2']}]}]},
                  {'id':'readiness','recipe':'checklist','title':'Digital Product Launch Readiness','purpose':'A practical internal checklist for validating a small-business digital download before release.','sections':[{'heading':'Validate the deliverable','paragraphs':['Use a clean copy of the customer package. Keep internal notes outside it.'],'items':['Open every included file in its intended application.','Change sample inputs and confirm advertised calculations update.','Check blank inputs and zero denominators.']},{'heading':'Check the listing','items':['Compare the advertised features with the actual package.','Confirm title, price, currency and visibility against the approved launch scope.','Check images at a readable size and confirm delivery links work.']},{'heading':'Confirm release authority','items':['Obtain the owner’s approval for the exact batch and prices.','Do not change payment settings or accept legal terms as part of a listing task.','Record the verified listing URL and avoid duplicate submissions.']}]}]
        products.append({'id':'cashflow','recipe':'cashflow','title':'Cash Flow Planner'})
        q.products(p,'owner',products);q.control(p,'owner','start');deadline=time.monotonic()+450
        while time.monotonic()<deadline:
            state=q.summary(p,'owner')
            if state['state']=='completed':break
            errors=q.rows("SELECT key,error FROM jobs WHERE project=? AND state IN ('failed','blocked','review')",(p,))
            if errors:raise AssertionError(errors)
            time.sleep(.2)
        assert state['state']=='completed'
        for product in products:
            package=q.result(p,'owner',product['id']+':package')['result']
            assert package['qa_verified'] and package['bytes']>1000
        document=q.result(p,'owner','readiness:package')['result'];assert {'product.docx','product.pdf','LICENSE.txt'}<=set(document['files'])
        custom=q.result(p,'owner','sales:validate')['result'];assert [c['expected'] for c in custom['checks']]==[1000,375,625]
        record('native_custom_spreadsheet_outputs_verified');record('editable_word_pdf_sections_and_previews_verified');record('customer_archives_verified');record('artifacts',str(q.root/p/'artifacts'));record('complete')
    except Exception as error:record('complete',False);record('error',type(error).__name__+': '+str(error));raise
    finally:q.close()


if __name__=='__main__':main()
