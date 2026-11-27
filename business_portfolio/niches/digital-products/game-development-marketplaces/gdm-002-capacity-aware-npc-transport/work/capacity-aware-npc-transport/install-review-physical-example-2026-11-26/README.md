# Local add-on install review

Copy `addons/transit_coordinator` into a Godot 4 project's `addons` folder. See `API.md` for configuration, movement callbacks and trusted snapshot handling.

To try a logical-only example, also copy `examples/quickstart.gd` into your project and run `godot --headless --path <project> --script res://examples/quickstart.gd`. It simulates acknowledgments and moves no bodies; a real game must verify physical boarding and exit.

A scripted physical transfer example is also included. After copying `examples/`, run `godot --headless --path <project> --script res://examples/physical_transfer.gd`. It uses one game-owned passenger, two collision platforms and fixed targets; adapt movement and safety checks to your game.

This local review omits the full development demo, broader tests, engine and research. References to them in copied guides describe the broader development project. Support and provenance documents are drafts. This review copy has no approved license and is not authorized for distribution.
