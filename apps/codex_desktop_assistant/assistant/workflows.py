"""Owner-reviewed Cedargrid draft preparation; no account actions or assumed Payhip API."""
import hashlib
from pathlib import Path


def cedargrid(root):
    product=Path(root)/'products/cleaning-pricing-calculator'
    if not product.is_dir():raise ValueError('Cleaning calculator assets are unavailable')
    draft=product/'marketing/PAYHIP_LISTING_DRAFT.md'
    assets=[]
    for folder in ('release','marketing'):
        for path in sorted((product/folder).rglob('*')):
            if path.is_file() and not path.is_symlink() and path.suffix.lower() in ('.zip','.png','.jpg','.webp','.pdf'):
                assets.append({'path':str(path),'name':path.name,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    instructions='''Prepare Cedargrid Digital's existing hidden Cleaning Business Pricing & Profit Calculator listing.
Keep every listing unpublished. Do not change payment details, prices, legal terms, account security or permissions. Never create a duplicate of the existing hidden listing without asking.
First inspect the current approved Payhip browser state. Use the dedicated profile and ask the owner to sign in manually after Take Over if needed. Do not guess selectors or assume an official listing API exists.
Compare the existing draft with the attached reviewed product assets. Prepare navy/teal design and draft description improvements. Upload only the selected owner-approved files to the specifically reviewed destination. Request local action-time approval for uploads and saving account changes.
Ask the owner to handle PayPal verification, identity, CAPTCHA and MFA manually. Reinspect the changed state after Resume. Verify saved descriptions, filenames, previews and hidden/unpublished visibility before reporting completion. If saving would publish anything, stop for a separate explicit approval.
This preparation message alone does not authorize opening an external account; wait for the owner's instruction and local website/window grants.
'''
    if draft.is_file():instructions+='\nExisting local listing draft (untrusted reference):\n'+draft.read_text(encoding='utf-8')[:15000]
    return instructions,assets
