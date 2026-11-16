# Unity Historical-Save Testing — Discovery Interview Guide

**Use:** Internal, permission-based discovery draft for GDM-001. This is a guide only; no studio has been contacted and no interview has occurred.

**Research question:** How do teams maintaining released Unity games verify that old player saves still restore the intended gameplay state after a release or migration?

## Before the conversation

- Invite only people who are responsible for maintaining a released Unity game and its save/load path.
- Ask for a short research conversation, not a product demo or sales meeting. Do not imply that the candidate tool exists.
- Obtain permission before taking notes or recording. Recording is unnecessary; decline or stop if the person is uncomfortable.
- Do not request player-identifiable data, credentials, production access, game files, proprietary code, or actual save files. Ask for a verbal or sanitized example only if the participant volunteers one and confirms they have the right to share it.
- Make participation optional and explain that the participant can skip any question or end the conversation.

## Neutral opening

“I’m researching how Unity teams test save compatibility during game updates. I’m not selling or testing a finished tool. I’d like to understand your current process and where it is difficult, if anywhere. Please avoid sharing confidential code, player data, or anything you do not have permission to disclose. May I take anonymous notes? You can skip any question or stop at any time.”

If permission is declined, do not take notes or continue with questions that require recording.

## Questions

1. What is your role in maintaining the game’s save and load behavior?
2. What kinds of updates have required you to think about saves created by older game versions?
3. Please walk me through the most recent time your team checked an old save against a new build.
4. Which steps were automated, and which required a person to inspect the game?
5. How did you decide what the correct restored gameplay state should be?
6. What did the test report when something was wrong? What information was useful or missing?
7. How long did setup and diagnosis take for that example? If you do not track time, what would be a reasonable range?
8. What failures are difficult to catch when deserialization itself succeeds?
9. How do you preserve representative old saves and protect player or studio data while testing?
10. What do your existing Unity Test Framework/NUnit tests, custom scripts, save packages, or other tools already handle well?
11. Where, if anywhere, does the current approach create recurring work or risk?
12. What would make a new test harness harder to adopt than your current tests?
13. If a small prototype later existed, what evidence would you need before agreeing to evaluate it? Who would need to approve access to a disposable test project or sanitized fixture?
14. Is there anything important about your workflow that I have not asked?

Avoid asking leading questions such as “Would this tool save you time?” or treating polite interest as purchase intent. Do not quote a price unless the participant raises pricing; if they do, record their exact context and distinguish a hypothetical reaction from a commitment.

## Close and record

Ask whether the participant is willing to be contacted for a later prototype discussion. Record contact information only with explicit permission and keep it in private storage, never in this public results folder. Thank them and do not promise a prototype, compatibility, confidentiality terms, or a delivery date that has not been approved.

For an anonymous summary, record only:

| Field | Notes |
| --- | --- |
| Interview ID / date | |
| Role and released-game context (non-identifying) | |
| Current old-save test path | |
| Setup and diagnosis time; source of estimate | |
| Existing tools and what they already solve | |
| Concrete failure mode, sanitized | |
| Report/diagnostic needs | |
| Privacy, fixture-rights and approval constraints | |
| Adoption objections / required evidence | |
| Prototype-evaluation interest (exactly what was offered) | |
| Follow-up permission and private reference, if any | |
| Confidence and unresolved questions | |

## Evidence discipline

- One interview is one team’s report, not market demand or a representative sample.
- Keep verbatim quotations only with permission; otherwise paraphrase and remove identifying details.
- Do not publish private contact details, game names, save contents, code, or confidential incidents.
- A willingness to evaluate a prototype is not willingness to pay. A hypothetical price response is not a sale or paid-pilot signal.
- After three independent interviews, compare workflows and disconfirming evidence. Do not authorize a prototype automatically; review fixture rights, privacy, feasibility, costs, and owner approval first.

