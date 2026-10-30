"""Owner-approved read-only reconciliation; never renews write scopes."""
import json
import zipfile
from assistant.permissions import Denied
from assistant.payhip import PayhipBrowserAdapter
from assistant.products import ProductFactory, digest


def verify_saved(runtime):
    project='811d41672eed4b009822b111e0411a30';product='inventory-test'
    editor='https://payhip.com/product/edit/dotFZ'
    queue=runtime.broker.projects.queue;chrome=runtime.broker.chrome;owner=runtime.owner
    chrome.check(owner);epoch=runtime.permissions.generation
    package=queue.result(project,owner,product+':package')['result']
    rows=queue.rows('SELECT manifest FROM scopes WHERE project=? ORDER BY rowid DESC LIMIT 1',(project,))
    if not rows:raise Denied('Original approved manifest unavailable')
    manifest=json.loads(rows[0]['manifest'])
    if manifest.get('sha256')!=package['sha256'] or manifest.get('visibility')!='invisible':raise Denied('Original listing manifest mismatch')
    if not runtime.approve(owner,'Verify saved Invisible listing (read only)',{'operation':'payhip_saved_readonly','approval_reason':'Read only the existing Invisible CAD19 test listing and its observed owner download; hash approved ZIP and images. No uploads, saves, creation, publication or renewal of write scopes.','project':project,'editor':editor,'sha256':package['sha256'],'bytes':143072}):raise Denied('Read-only verification was not approved')
    def existing(url):
        chrome.check(owner,epoch)
        matches=chrome.request(owner,'find_tabs',{'query':url},epoch)['tabs']
        tabs=[t for t in matches if t.get('url')==url]
        if not tabs:raise Denied('Required existing exact-URL tab is unavailable; no new tab created')
        tab=tabs[0]['tab'];chrome.request(owner,'adopt_tab',{'tab':tab},epoch,unattached=True);chrome.attach(owner,tab,ask=False)
        return tab
    tab=existing(editor)
    snapshot=chrome.call(owner,'inspect',{'tab':tab})
    adapter=PayhipBrowserAdapter(chrome,owner,runtime.store,runtime.attachments);adapter.scope=manifest
    if not adapter.verify_fields(snapshot):raise Denied('Saved exact title/price/Invisible fields mismatch')
    controls=[c for c in snapshot['controls'] if '/product/download/' in c.get('href','')]
    if len(controls)!=1:raise Denied('Saved owner download is missing or ambiguous')
    actual=chrome.request(owner,'asset_digest',{'tab':tab,'observation':snapshot['observation'],'element':controls[0]['element'],'kind':'delivery'},epoch)
    if actual.get('sha256')!=package['sha256'] or actual.get('bytes')!=143072:
        raise Denied('Owner download did not match approved ZIP: bytes='+str(actual.get('bytes'))+', sha256='+str(actual.get('sha256'))+'. No upload/save was attempted.')
    factory=ProductFactory(queue.root/project/'artifacts');archive=factory.path(package['archive'])
    if digest(archive)!=actual['sha256']:raise Denied('Local archive changed')
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None:raise Denied('ZIP integrity failure')
    images={};snapshot=chrome.call(owner,'inspect',{'tab':tab})
    for receipt in snapshot.get('commerce',{}).get('cover_images',[]):
        name=receipt.get('name');expected=manifest['assets'].get(name)
        if not expected or name in images:raise Denied('Unexpected or duplicate saved image')
        found=chrome.request(owner,'asset_digest',{'tab':tab,'observation':snapshot['observation'],'asset':receipt['asset'],'kind':'uploaded_image'},epoch)
        if found.get('sha256')!=expected['sha256'] or found.get('bytes')!=expected['bytes']:raise Denied('Saved image hash mismatch')
        images[name]={'sha256':found['sha256'],'bytes':found['bytes']}
    if set(images)!={'Cover.png','Preview-1.png','Preview-2.png'}:raise Denied('Incomplete saved image verification')
    baseline=chrome.call(owner,'inspect',{'tab':existing('https://payhip.com/products')})
    original=[c for c in baseline['controls'] if c.get('href')=='https://payhip.com/b/bP6YN' and c.get('label')=='Cleaning Business Pricing & Profit Calculator']
    if len(original)!=1 or 'HIDDEN' not in original[0].get('nearby','') or 'CAD29.00' not in original[0].get('nearby',''):raise Denied('Original calculator state not verified')
    result={'verified':True,'product':product,'visibility':'invisible','listing':{'title':manifest['title'],'url':'https://payhip.com/b/dotFZ','visibility':'invisible','price_cents':1900,'currency':'CAD','saved_fields_verified':True,'files_verified':True,'delivery':actual,'images':images,'zip_integrity':True,'original_calculator_unchanged':True}}
    chrome.check(owner,epoch)
    with queue.lock:
        for key in (product+':prepare-hidden',product+':verify-hidden'):
            queue.db.execute("UPDATE jobs SET state='completed',error='',result=? WHERE project=? AND key=? AND state='blocked'",(json.dumps(result),project,key))
        queue.db.execute("UPDATE projects SET state='completed' WHERE id=? AND NOT EXISTS(SELECT 1 FROM jobs WHERE project=? AND state!='completed')",(project,project))
        queue.event(project,None,'saved_readonly_verified',result);queue.db.commit()
    return result
