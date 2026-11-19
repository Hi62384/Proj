# Work folder for GDM-002

This directory is the canonical location for new source, tests, assets, builds, packaging, release drafts and marketing files related to this project.

## Existing work handoff

Legacy implementation is in products/game-tools/capacity-aware-npc-transport and a supporting gdm-002-transit-proof folder. Preserve both during a staged migration; relocate maintained source to work/ and update test paths before removing legacy copies.

Do not relocate or delete existing verified artifacts until their consumers and tests have been updated and verified. All new project-specific changes should happen inside work/.
