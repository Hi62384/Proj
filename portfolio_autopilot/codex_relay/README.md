# Codex Relay

A Windows, local-first shared inbox for **Hi62384/Proj**. ChatGPT proposes an Issue; you approve its exact file scope locally; an isolated Codex app-server thread edits those files. GitHub comments carry status and reviewed questions/reports. Valid follow-ups resume the saved thread. ChatGPT reads the inbox **when you ask it to check**, not through automatic injection into a chatgpt.com conversation.

No new repository, VS Code, OpenAI account, hosting, database service, or API key is required. Python 3.11+ and the official Codex CLI are required. This is a separate app-server session, not attachment to an existing desktop chat window.

## Start on Windows

Double-click **`portfolio_autopilot/Start_Codex_Relay.cmd`**. A console hosts the service and your default browser opens its authenticated dashboard. The runner initially stays stopped. Close the console or press Ctrl+C to shut it down. **Stop runner** pauses active execution and stops polling; it leaves the dashboard open.

The dashboard binds only to `127.0.0.1:8766`. A random link fragment establishes an HttpOnly/SameSite session, and all changes also require a secret request header. The fragment is removed from the address bar after login. Do not share that initial link or browser session. Host validation, origin checks, CSP, and frame restrictions protect the local interface. Text from GitHub is rendered using DOM text nodes.

If the port is in use, close the existing instance or change `port` in the runtime configuration. A process lock prevents two runners sharing the same journal. Do not run separate relay data directories against this repository concurrently: the single-runner guarantee applies to one installation/journal.

## Exactly what to configure manually

1. Create a **fine-grained GitHub personal access token** for **only Hi62384/Proj**. Grant **Issues: read and write**, with the automatically required metadata read permission. Do **not** grant Contents write, Actions, repository administration, or other repositories. Set an expiry. The relay cannot introspect a fine-grained token's full grants; verify these in GitHub yourself. Revoke broader tokens rather than reusing them here. GitHub CLI was not available in the implementation environment, so this version uses Windows Credential Manager instead of shelling out to `gh`.
2. In **Setup**, paste that token locally and choose **Verify and save setup**. It is sent only to GitHub's API, stored in Windows Credential Manager as `CodexRelay:Hi62384/Proj:Issues`, and never saved in source/configuration. The verified token account's immutable numeric ID becomes the owner. Further setup attempts must use that same owner.
3. If ChatGPT posts using a **different GitHub account**, deliberately add that account's numeric ID to **Additional trusted IDs**. If it posts as your owner account, leave this blank. Usernames, labels, Issue text and `author_association` are not authorization. Anyone able to post as a trusted account has the same inbox authority; the relay cannot prove a comment came from ChatGPT rather than a human using that account.
4. Click **Test connections**. This initializes app-server and checks authentication without starting an AI turn. The relay imports an existing file-based **ChatGPT** CLI login into its isolated home on first use. If none is reusable, see the login fallback below. API-key, Bedrock and other billing modes are rejected; inherited API-key/token variables are removed. ChatGPT plan usage is still subject to your account's limits and access. The test checks sign-in, not model inference entitlement.
5. Click **Start runner**. Approve each new task locally after reviewing all instructions and exact file names. You must check the nonsensitive/public-test acknowledgement. Starting the runner alone never approves tasks.

No credentials were installed or GitHub permissions changed during implementation. Live Issue writes and AI executions have not been run as part of the normal test suite.

## Files and privacy

Runtime files live in **`%LOCALAPPDATA%\CodexRelay`**, outside Git:

- `config.json`: workspace, fixed repository, numeric owner/trusted IDs, port (8766), polling interval (60 seconds), optional absolute `codex_binary` path and optional model ID.
- `relay.sqlite3` and its WAL: tasks, approvals, communication history, inbox deduplication, publication outbox, ETag cache, and rate-limit recovery timestamp.
- `codex-home/`: isolated Codex settings, reused CLI authentication and persistent Codex threads. The CLI owns authentication refresh. Its auth file is sensitive, as in a normal CLI installation.
- `backups/`: original contents of overwritten approved files. No automated deletion or Git rollback is performed.
- `instance.lock`: runner process lock, released by the OS on exit.

Keep the runtime directory within your private Windows user profile. Local transcripts and backups are **not encrypted by the relay**. The GitHub token uses Windows Credential Manager. Do not copy the runtime directory into the repository, a public share or an Issue. Root `.gitignore` also excludes common secret/runtime files defensively.

The public/unknown-repository warning is always visible. Privacy is rechecked during polling. Only deliberately approved nonsensitive tasks are enabled even if you later make the repository private. **Automatic comments use fixed status text only**, including task ID, status, scope grant ID and reply anchor. Source, raw output, local paths, test logs and session IDs are not automatically published.

Questions and completion reports remain visible locally. To send their actual content to ChatGPT, use **Release a reviewed question or report to GitHub**, write the exact sanitized text, check the publication acknowledgement, and queue it. An obvious-secret/path filter is an additional check, not a guarantee that arbitrary text is safe. Review the exact text yourself. This extra review is deliberate for a public repository.

## Security and execution boundaries

Each task receives one locally approved list of **exact relative file names**; directory grants and globs are unsupported. Read/write operations are enforced in Python, with traversal, Windows alternate-stream, device-name, link/junction and protected-path checks. Overwrites require the hash from a previous read, preserving preexisting edits against stale writes. Original bytes are backed up outside Git. `.git`, `.codex`, `.agents`, `.github`, credentials, runtime folders and the relay's own code are excluded. The relay cannot edit `AGENTS.md` or `SKILL.md` instruction files. Normal files within an approved task scope may be created or changed, never deleted.

Codex receives one capability tool, `relay_workspace`: list approved paths, read UTF-8, write UTF-8, and check Python/JSON syntax. It can also read the root `AGENTS.md`. File size is limited to 500 KB. App-server runs with a read-only sandbox, command tools disabled, isolated configuration, no inherited plugins/MCP servers, no web search, and no automatic permission approvals. Unknown server-side requests are rejected. These are enforced capabilities; a prompt merely saying “don't push” is not the security boundary.

**Executable project tests are an owner action in this version.** Running arbitrary repository Python, npm scripts, or shell commands would let task-generated code make network calls, spend money, use credentials or publish. The relay therefore supports deterministic Python/JSON syntax checks, and records them explicitly as syntax checks. It cannot autonomously run full test suites, install packages or build systems. Codex must request your decision when that is necessary. Its claimed test results are displayed separately from checks actually performed by the relay. You can run reviewed project tests yourself, or ask this desktop chat to run them in its existing managed sandbox. No unrestricted “allow shell” switch is provided.

An automatic follow-up must be from a trusted numeric GitHub ID, use the current scope and reply anchor, arrive after local approval, be unedited, and match the strict message schema. It retains exactly the same file/tool permissions. The relay cannot mechanically prove the semantic meaning of arbitrary technical prose; trusted correspondents must keep corrections within the approved requirements. Material requirement/path changes must be proposed by editing the Issue or creating a new task, which revokes approval and requires local review. Sensitive/business decisions never gain approval from an `OWNER_DECISION` comment alone: they wait for local review. No external-effect tool is available even after local Resume.

For a security-critical or money/account/publication request, Codex returns `kind: owner`; it pauses as **Needs Owner**. A technical question returns `kind: question` and pauses as **Needs ChatGPT**. Paused, cancelled, failed, completed and owner-blocked tasks cannot be restarted by ordinary remote comments. A local Resume is needed where permitted. Cancellation preserves changes already made; inspect them manually. Stop and file writes share a local gate so no new tool operation starts after cancellation is recorded. An operation already in flight may finish first. Active app-server turns are interrupted and the process is terminated.

Issue edits/closure, including malformed edits, revoke approval on the next poll. Before local approval the inbox is refreshed. There is no remote kill-switch guarantee while the network is down; use local **Stop runner/Cancel** for immediate control. One approved turn may finish locally during a network outage. New executions are launched only after a successful poll.

## Task Issue format

Ask ChatGPT to create an Issue in `Hi62384/Proj` with a normal title and **exactly this body**, changing values as appropriate. No Markdown fences or surrounding prose; the first line must be `CODEX_RELAY_V1`.

```text
CODEX_RELAY_V1
{
  "type": "TASK",
  "task_id": "relay-demo-001",
  "description": "Create a harmless local test file using Codex Relay.",
  "priority": "normal",
  "requirements": ["Write Hello from Codex Relay followed by a newline. No external services."],
  "paths": ["codex_relay_demo.txt"],
  "dependencies": [],
  "acceptance_criteria": ["The approved file exists with the requested text."]
}
```

IDs must be unique (3–64 letters/digits/underscores/hyphens, starting with a letter/digit). Priorities are `low`, `normal`, `high`. Dependencies are other relay task IDs and must be marked **Completed** locally before dependent execution starts. Cycles/unknown dependencies wait; they do not trigger inference. A PR is never treated as a task. Arbitrary labels or comments containing magic strings have no authority.

Local states are **Proposed**, **Approved**, **Running**, **Needs ChatGPT**, **Needs Owner**, **Awaiting Review**, **Completed**, **Failed**, **Cancelled**. After implementation finishes it enters Awaiting Review; only the owner's **Mark reviewed / Completed** finishes it. These states are reflected by structured status comments. The relay deliberately does not create labels, close Issues, open PRs or change repository settings.

## Reply format and first live two-way test

1. Finish Setup and test connections. Verify ChatGPT's GitHub connection actually exposes Issue creation/comment writing. Available capabilities differ between ChatGPT installations; do not assume read access includes writes.
2. Ask ChatGPT to create the harmless task above. Start the runner, wait for the Proposed task, inspect the exact text and file scope, check the public-test acknowledgement, and click Approve. This approval authorizes a real Codex turn using your ChatGPT plan.
3. Wait for Awaiting Review. Inspect `codex_relay_demo.txt`, the local report, files changed and history. No commit or push occurs. Release a concise reviewed completion comment for ChatGPT, for example “The harmless text file was created. Please ask for the same-file follow-up.”
4. Ask ChatGPT to fetch that Issue and its comments. It should read the **latest relay comment**, copy its `task_id`, `scope`, and `message_id`, then post this exact message schema (with those copied values) as a new unedited comment:

```text
CODEX_RELAY_V1
{
  "type": "CHATGPT_REPLY",
  "task_id": "relay-demo-001",
  "message_id": "reply-demo-001",
  "reply_to": "COPY_LATEST_RELAY_MESSAGE_ID",
  "scope": "COPY_CURRENT_SCOPE",
  "action": "continue",
  "text": "Within the same approved test file, change the greeting to Hello again from Codex Relay followed by a newline. Do not change other files."
}
```

5. The runner validates the author ID and grant and starts a new turn on the **same thread ID**. Inspect the correction and the unchanged thread ID locally. Release a second sanitized completion message, then ask ChatGPT to fetch/review it. Mark Completed locally when satisfied.
6. You decide whether to commit/push anything yourself. The relay does not do either.

Other actions: `pause`, `cancel`, `report`, `decision`. `report` requests a final report using another turn on the same approved scope. `pause` requires local Resume. `cancel` is terminal. `OWNER_DECISION` always queues for local review. Message types accepted for display/validation are `CODEX_PROGRESS`, `CODEX_QUESTION`, `CODEX_ERROR`, `CODEX_RESULT`, `CHATGPT_REPLY`, `OWNER_DECISION`; only the latter two enter the inbound command queue. Every message requires the same seven fields shown above. Do not edit a submitted reply; post a new message with a new `message_id` instead.

If ChatGPT's GitHub connection cannot create Issues or comments, use GitHub's web interface signed in as a trusted account to create/paste the same structured Issue/reply. ChatGPT can still read the shared inbox if its connection permits it. This minimal fallback requires manual posting and therefore cannot deliver the full no-copy workflow until an Issue-write-capable connection is available. No tunnel, custom public endpoint or additional billing is substituted.

## Reliability and recovery

SQLite transactions persist approval, inbox messages, task claims, session IDs and history. GitHub comment IDs and message IDs are unique. An execution is claimed durably **before** starting app-server; after a crash, a previously Running task becomes Needs Owner. Inspect its files, then Resume explicitly. No automatic replay of an ambiguous AI execution occurs. New turns resume the saved `thread_id`; they do not start a fresh conversation. If a thread was never successfully created, Resume creates one.

The installed app-server does not persist an empty thread before a first turn. If it reports “no rollout found,” the task fails visibly rather than silently losing conversation context. Review its files, choose **Reset failed session**, then **Resume** to authorize a replacement conversation within the same file scope. This exception is recorded in the audit history; ordinary follow-ups keep the original thread.

Polling uses conditional requests/ETags and cached unchanged responses; all pages are read (up to 10,000 entries per list, then fail closed). One active AI execution is allowed. Network errors back off; GitHub rate-limit reset/Retry-After timestamps persist across restart. Failed inference is not retried automatically. Turns have a 30-minute limit. No model is selected by the relay unless you configure one; app-server uses its available default.

Publication has a durable outbox. Before a POST the relay searches existing comments for its message ID. If a POST response is lost or fails, its outcome is marked **uncertain** and is **not automatically reposted**, avoiding duplicate externally visible comments. The dashboard shows uncertain deliveries. Inspect the Issue and manually release a new reviewed message if the old one truly was not posted. GitHub has no general exactly-once comment-creation API, so this conservative recovery is intentional.

## Authentication fallback and troubleshooting

Official CLI installation/sign-in: [Codex CLI](https://learn.chatgpt.com/docs/codex-cli), [authentication](https://developers.openai.com/codex/auth).

If the relay cannot import your existing file login, sign in with the same ChatGPT account in its isolated home. A one-time PowerShell setup (not needed during everyday use):

```powershell
$previousCodexHome = $env:CODEX_HOME
try {
    $env:CODEX_HOME = Join-Path $env:LOCALAPPDATA 'CodexRelay\codex-home'
    codex login
} finally {
    $env:CODEX_HOME = $previousCodexHome
}
```

Choose ChatGPT sign-in; do not supply an API key. If the imported login becomes invalid, stop the relay and repeat that login. Do not paste auth.json contents in chat. No account email/token is returned by connection tests. CLI executables installed by npm are resolved to their native binary rather than launching a `.cmd` shell. An absolute native `.exe` can be specified as `codex_binary` if necessary.

`Codex account routing discovery failed` means app-server initialized but could not discover the authenticated workspace (network connectivity or login refresh may be involved). A successful CLI `login status` alone does not prove app-server/inference can reach the service. Check the connection and repeat the no-inference test before approving work.

From the repository root, optional diagnostics:

```powershell
python -m portfolio_autopilot.codex_relay doctor
python -m portfolio_autopilot.codex_relay serve --no-browser
```

`--no-browser` prints a private localhost capability link; do not share its output. Connection failures remain visible in the dashboard. The doctor reports each integration separately.

## Tests

All regular tests are deterministic, use mock Codex/GitHub clients, and consume no inference or paid API usage:

```powershell
python -m unittest discover -s portfolio_autopilot/codex_relay/tests -v
```

Coverage includes strict parsing, task creation/tracking, numeric identities, approvals/rejection, thread start/resumption, output events, persistence/recovery, inbox/outbox deduplication, connectivity/rate limits, pause/cancel, failures, malicious instructions, forbidden publishing/billing capabilities, path boundaries, hashes, public-output filtering, and HTTP session/CSRF/Host/origin protections.

Optional **real inference** smoke test, only after you deliberately approve ChatGPT plan usage by running this command (stop the dashboard first):

```powershell
python -m portfolio_autopilot.codex_relay.live_test --approve-chatgpt-usage
```

It creates and corrects `codex_relay_demo.txt` in two turns on the same real thread, refusing to overwrite a preexisting file. It does not post to GitHub and is **not** a substitute for the live two-way acceptance test above. Leave that file for review/remove it yourself. Neither test is reported as passed unless it was actually run.

## Implementation references

Significant implementation files (relative to this repository):

| Files | Purpose |
| --- | --- |
| `portfolio_autopilot/Start_Codex_Relay.cmd` | One-click Windows launcher |
| `portfolio_autopilot/codex_relay/__main__.py`, `__init__.py` | Entrypoint, process lock and lifecycle |
| `portfolio_autopilot/codex_relay/config.py`, `credentials.py` | Configuration, path validation, Windows Credential Manager |
| `portfolio_autopilot/codex_relay/github.py`, `messages.py` | Restricted Issues client and strict wire protocol |
| `portfolio_autopilot/codex_relay/store.py`, `scheduler.py` | Journal, approvals, inbox/outbox, scheduling and recovery |
| `portfolio_autopilot/codex_relay/codex.py`, `workspace.py` | App-server transport, session reuse and bounded file capabilities |
| `portfolio_autopilot/codex_relay/dashboard.py`, `static/index.html`, `static/app.js`, `static/style.css` | Authenticated loopback dashboard |
| `portfolio_autopilot/codex_relay/tests/test_relay.py`, `live_test.py` | Offline suite and explicitly opt-in real-inference test |
| `portfolio_autopilot/codex_relay/README.md`, `portfolio_autopilot/README.md` | Configuration, operation, protocol and acceptance-test instructions |
| `.gitignore`, `.github/workflows/codex-relay-tests.yml` | Runtime exclusion and offline Windows/Linux CI |

Verification on this Windows machine: the offline relay suite, existing Autopilot suite (10 tests), and existing factory suite (40 tests) were run. Both the Python entrypoint and actual Windows `.cmd` launcher were exercised against an authenticated local dashboard without network or inference. JavaScript syntax and Git whitespace checks were run. A real app-server initialized, verified the existing **ChatGPT** login, created an empty thread with the bounded dynamic tool, and reported zero external MCP servers. Attempting to resume that empty thread confirmed the “no rollout” condition documented above. Actual inference, persisted-thread continuation after inference, live GitHub reads/writes with a relay token, and the full ChatGPT↔GitHub↔Codex acceptance test remain untested. The optional real-inference test was not run. No commits or pushes were made.

Implementation verified against the installed `codex-cli 0.162.1` generated app-server schemas plus current official documentation:

- [Codex app-server](https://developers.openai.com/codex/app-server): stdio initialization, persistent threads, turn events, interruption, authentication and experimental dynamic tools. Dynamic tool APIs are experimental: fail closed if a future CLI changes their schema; no insecure fallback.
- [Codex as a platform](https://developers.openai.com/blog/codex-as-a-platform): choosing app-server for persistent, interactive sessions.
- [Codex configuration](https://developers.openai.com/codex/config-reference): forced ChatGPT login and disabled command tools.
- [GitHub Issues API](https://docs.github.com/en/rest/issues/issues), [comments API](https://docs.github.com/en/rest/issues/comments), [API practices](https://docs.github.com/en/rest/using-the-rest-api/best-practices-for-using-the-rest-api): issue/comment transport, conditional polling and rate limits.

The installed CLI rejects the legacy `untrusted` approval policy even though it appears in its schema; the implementation uses `on-request` and rejects all permission requests. It never silently switches to unrestricted execution.
