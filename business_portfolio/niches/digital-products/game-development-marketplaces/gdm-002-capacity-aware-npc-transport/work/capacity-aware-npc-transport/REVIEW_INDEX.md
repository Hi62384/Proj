# Local review snapshots

These are unpublished development snapshots. They are not licensed or approved for distribution.

- `review-candidate-2026-11-18k/` is the latest snapshot, including the game-owned controller bridge, corrected HUD, compatibility guide and restore fixtures. It updates the documentation from `18j` and retains the same executable source. It remains unlicensed and unpublished.
- `review-candidate-2026-11-18j/` is the prior 80-file snapshot. Its complete 47-script suite passed on Godot 4.4.1, 4.5.1 and 4.7.2; staged install and editor smoke checks also passed.
- `review-candidate-2026-11-18i/` is the prior 67-file snapshot, including the staggered 20-agent, capacity-three two-platform collision transfer. Agent-to-agent collision is disabled.
- `review-candidate-2026-11-18h/` is the prior 66-file snapshot, including the six-agent staggered transfer.
- `review-candidate-2026-11-18g/` is the prior 65-file snapshot, including a scripted 20-agent two-platform collision transfer.
- `review-candidate-2026-11-18f/` is the prior 63-file snapshot, including a 20-agent single-platform collision fixture.
- `review-candidate-2026-11-18e/` is the prior 62-file snapshot, including the finite FIFO liveness fixture.
- `review-candidate-2026-11-18d/` is the prior 61-file snapshot, including the 20-agent navigation-link fixture.
- `review-candidate-2026-11-18c/` is the prior snapshot. Its 60-file manifest, full 33-script test suite, headless demo startup, install/reinstall smoke checks and headless editor marker checks passed on Godot 4.5.1.
- `review-candidate-2026-11-18b/` is an intermediate snapshot retained for traceability. Its installation probe failed to compile due to an ambiguous local variable type; that probe was corrected before snapshot `18c`.
- `review-candidate-2026-11-18/` is an earlier snapshot without the later continuity audit.

Each snapshot has its own `REVIEW_ONLY.txt` and `REVIEW_MANIFEST.json`. A snapshot captures source at staging time; later changes require a new snapshot. These directories are local review artifacts, not public portfolio results or authorization to publish.
