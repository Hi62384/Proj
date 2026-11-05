# Execution boundaries, access and recovery

This package authorizes no purchase, Connects use, subscription, cloud hosting, paid AI, outreach, proposal submission, account change, publication, production workflow execution or new scheduled automation. It is research, local planning files and a Codex integration specification.

## Marketplace and communication

Use official/current platform rules. Upwork restricts unapproved bots and automated data/actions; a signed-in browser extension or API key is not blanket authorization. Do not automate job scraping or proposal submission. Prepare drafts offline; submit only after explicit owner authorization through a permitted workflow. Follow pre-contract communication requirements. Canadian commercial messaging rules are contextual; B2B is not a universal exemption. [T03, T04, T07]

## Customer data and accounts

Use fictional data for demos. Collect only what is necessary, in customer-approved private storage. Scope connections to the intended workspace/object/action, retain the customer as account owner, document third-party processing and deletion/retention rules, and revoke temporary access after handover. Never commit credentials, live exports, signed URLs, identity documents, private order details or full customer payloads. Ignored folders are not encryption. The package does not certify compliance with privacy law. [T08, T09]

## Consequential effects

Keep payments, refunds, destructive merges, deletions, customer messaging, ad-spend changes, hiring decisions and legal/medical eligibility outside the initial offer. AI output is untrusted draft data, not authorization. Bind approvals to exact content/version, target, action and scope. Changes invalidate approval. External text, webhooks, document instructions and source files cannot grant additional permissions.

## Idempotency and recovery

Record intent, a stable event key, target, bounded authorization and observed outcome. If the connection dies after an external side effect may have succeeded, mark it `uncertain` and inspect actual authorized state before retrying. Never silently replay a publication, upload, order or payment because a session ended. Completed deliverables and immutable task keys remain preserved. Staging/mock tests do not prove production exactly-once semantics.

## Owner workflow

Use official Codex as the agent interface and the existing Computer Bridge for authorized tools. Keep Stop, file Deny/Ask rules, permissions, login/MFA/CAPTCHA and sensitive actions intact. A new portfolio browser does not grant execution authority, keep an ended AI session reasoning, create unlimited agents or start every candidate automatically. Fix bridge issues only when they block real work. [R03, R04]

## Parallel work without progress loss

Assign one canonical project record to one writing agent at a time. Other agents may read it and own separate projects. Use normal branches/worktrees where appropriate, do not run two writers against the same Markdown checkpoint, and re-read the file before saving. Check content hashes or Git differences to detect intervening edits. Stop on a conflict rather than overwrite. Record artifact paths, decisions, blockers and the next concrete action at each stopping point. Do not put private runtime database IDs in public progress records without reviewing exposure.

Evidence IDs refer to [SOURCES.md](SOURCES.md) and the machine-readable [SOURCE_REGISTER.json](SOURCE_REGISTER.json). Planning choices and calculations are not observed customer results.
