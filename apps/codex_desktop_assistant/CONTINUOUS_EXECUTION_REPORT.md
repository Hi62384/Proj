# Continuous autonomous execution — October 28, 2026

Implemented in the existing Desktop Assistant. Ordinary input and foreground changes no longer halt desktop authority or interrupt an active Codex turn. No Relay source, external account, public listing or financial workflow was changed. No commit, push or dependency installation was performed.

## Root cause and repair

The old `InputGuard.physical()` set `desktop_suspended` and invoked the UI pause callback. The polling watcher also invoked that callback when the assistant became foreground. The UI callback could halt permissions and call `engine.pause()`, leading to `turn/interrupt`. A pre-change executable reproduction confirmed `desktop_suspended=true` and the reason `Paused — Your Input` after an ordinary physical-class input signal.

The replacement keeps three states separate:

1. **Model execution:** runs until completion, an explicit Stop, or a genuine failure. Ordinary input never sends `turn/interrupt`.
2. **Input availability:** per-action coordination, including target window, held keys/buttons, recent meaningful input, authorization epoch and observation freshness. It never changes the task to Waiting for User or Stopped.
3. **Human decisions:** exact pending requests shown in chat. A manual request waits for Done on its existing call/turn; an operation approval waits for the exact owner decision.

`attention.py` now records input telemetry only. Low-level hooks distinguish injected events and always pass events onward. There is no `BlockInput`, input swallowing or second cursor. Foreground polling is informational and provides a conservative fallback when hooks are unavailable. Shared mouse/keyboard input is refused if physical input monitoring is unavailable, while safe background accessibility/browser operations remain available.

`desktop.py` uses short transactions. Shared-pointer/focus actions wait for quiet; background semantic input can proceed in a different application. Held modifiers/buttons prevent unsafe shared typing. Before input it checks live window identity, permission generation, observation tokens and editable values. If the owner changed fields, the action is rejected for re-inspection instead of overwriting those edits. Fallback typing checks focus/cancellation between characters and limits each transaction to 256 characters/two seconds. Interrupted or ambiguous input is never automatically replayed. Only a never-dispatched action is automatically continued after its quiet interval.

`engine.py` has bounded host workers plus one dedicated COM desktop worker. A desktop action waiting for input access does not block the model event loop, steering, or independent Playwright work. Playwright remains on its owning thread. Pending work carries the original turn cancellation token and permission generation; queued work cannot adopt later replacement authority. Stop closes dispatch immediately, cancels pending work, and interrupts the turn. Completion after Stop cannot change the task back to Working. An inactivity watchdog is refreshed by model events rather than ending an otherwise-progressing task after a fixed total duration.

Steering remains durable. A definitively rejected correction, such as one arriving after a turn ended, is queued once for the next turn of the same saved conversation. Ambiguous delivery is retained for review rather than resent and possibly duplicated.

`ui.py` displays Ready, Working, Waiting for User, Stopped, Completed and Error. Only the activity detail says Waiting for input access. The main controls are Continue and Stop, with manual Done — Continue controls directly on actionable request cards. Opening chat, settings, minimizing/restoring, changing theme or notification preferences never triggers automatic Stop. Security-policy changes invalidate stale operations while remaining authorized work can continue.

`human.request_input` now waits for the owner, instead of raising an interruption. It explains the manual step, notifies with a safe category, and offers Done — Continue / Cannot complete. Typing Done in that chat also resolves the request. After the response, the same tool/turn/thread continues with instructions to inspect the actual current state and skip completed actions. Automated desktop/browser input is gated during a genuine manual step; manual browsing stays within approved origins. File and consequential-operation approval buttons continue their corresponding operation without an extra Resume click.

Existing file policy, protected locations, exact origins, account authentication, model/effort selectors, attachments, monitor/window scopes, program launching, screen observation, history, backups and Cedargrid workflows are retained. A consistent SQLite backup is taken before the first continuous-execution upgrade open. Pending approvals are expired on restart, never silently authorized.

## Measured verification

**74 assistant tests and 81 original Relay tests passed: 155 total.** Compilation and whitespace checks passed. Tests include policy/queue fault injection as well as actual Windows file operations. Mock protocol tests are not presented as live model evidence.

Real acceptance used the authenticated Codex app-server, disposable native Qt editors and a localhost Playwright form:

| Test | Measured result |
|---|---|
| Dedicated browser while typing into another real Windows editor | Passed; browser form completed and unrelated editor text stayed unchanged |
| Open assistant and send a correction during work | Passed; actual turn/steer accepted; same saved thread; no interrupt |
| Windows mouse-event delivery | Actual low-level motion events observed; task did not halt |
| Shared keyboard conflict | Synthetic physical-class typing activity deferred only the native action; steering remained responsive |
| Quiet interval after conflict | Deferred HOME key proceeded once; no text reached the wrong window |
| Owner edit after inspection | Actual native field edit preserved; stale overwrite denied |
| Actionable manual request | Waiting for User, exact instructions, unread notification fallback and Done — Continue button visible |
| Done reply | Same active turn and thread continued; native value verified after the owner edit |
| No external-action replay | Fixture save event list contained exactly one earlier save after the manual step |
| File approval/denial | Actual Codex create completed with local approval and no Resume; denied overwrite left bytes unchanged |
| Ordinary activity and decisions | RPC trace contained no turn/interrupt before explicit Stop |
| Explicit Stop | Cancelled a pending manual step, displayed Stopped, denied new desktop/browser input and did not restart |
| Ctrl+Alt+F12 | Actual registered Windows shortcut disabled input |
| Original full integration regression | Passed: streaming, persisted thread restart, image perception, native forms, five attachment formats, both browser modes, upload, active steering, explicit takeover/manual change/resume and emergency controls |
| Native controller/launcher regression | Passed: real control values, screenshot, global hotkey, redirect isolation, actual upload bytes, CMD/pythonw launch and normal close |

Private synthetic evidence under `%LOCALAPPDATA%\CodexDesktopAssistant\verification\`:

- `continuous-20261028-174157/results.json`: complete continuous execution and human interaction acceptance.
- `continuous-20261028-174739/results.json`: repeated complete run after the coordinator, held-input, permission-generation and settings changes.
- `continuous-20261028-174739/specific-human-request.png`: real native waiting card with the exact synthetic request and Done button.
- `20261028-174525/results.json`: complete original real Codex/browser/desktop/attachment/takeover regression.
- `controllers-20261028-174854/results.json`: real controller, upload, redirect, revocation and emergency checks.
- `launcher-20261028-174859/results.json`: actual Windows launcher verification.
- `continuous-owner-launch-20261028-175242/results.json`: finished app opened through the Windows launcher and connected with all restricted-runtime checks passing. Hash comparisons preserved both existing conversations, all 33 existing messages and their saved thread IDs; a consistent pre-upgrade backup was confirmed. The app was left open with desktop access disabled.

The first partial continuous test ended on a test-driver timing assertion before the queued notification/card event had been processed. The driver now waits for the actual visible card and unread indicator. The complete runs above exercised the full resolution path.

## Windows and testing limits

- Windows shares one pointer and foreground keyboard focus. This implements coordinated short actions and independent browser operations, not simultaneous independent cursors. An application can also choose to activate its own dialog after a semantic action.
- Tests used real Windows focus changes, Windows-generated mouse events and injected Unicode typing into actual native editors. Shared-input conflict conditions were explicitly injected into the physical-event classifier. A person did not supply hardware keyboard/mouse input during acceptance; no claim is made that every hardware/application combination was tested.
- Human input arriving after an atomic native operation has already dispatched cannot undo it. Mid-typing conflict stops remaining characters and requires re-inspection. A continuously busy channel returns a specific no-dispatch blocker after five seconds rather than retrying indefinitely or interrupting inference.
- Native UI Automation or browser calls already inside an application may finish at their own dispatch boundary. Stop denies subsequent actions and queued work; it does not roll back completed actions.
- Native notification banners depend on Windows settings. The notification API, taskbar/in-app fallback, unread routing and visible request controls were exercised; OS banner visibility/clicking was not independently observed.
- Manual requests and permission cards expire after five minutes. Unconfirmed steering delivery is retained for review, not automatically duplicated.
- Existing file/browser/runtime limits remain in README, including 500 KB direct file operations, empty-folder deletion, approved origins, protected credentials and human authentication. No sandbox restrictions were broadened.

## Use

Launch Start_Desktop_Assistant.cmd, choose your model/effort and authorized desktop/browser/file scopes, and send a task. Keep using your computer normally and send corrections whenever needed. No Pause/Resume cycle is required for ordinary activity. For a genuine manual request, follow its exact instructions and choose Done — Continue or type Done. Approve/deny file operations in chat. Use Stop or Ctrl+Alt+F12 for an intentional stop; continuing afterwards is explicit and revoked desktop scopes need re-authorization.
