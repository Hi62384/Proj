# Installation and first steps

This is an unpublished, unlicensed local review, not an approved distribution. Use it only for local evaluation.

1. In a Godot 4 project, copy this review's `addons/transit_coordinator` folder into the project's `addons` folder. The scripts can be used directly; the editor plugin is optional for the runtime coordinator.
2. For the optional stop-marker gizmo, open Project Settings → Plugins and enable **Transit Coordinator Tools**. Add a `Node3D` to a 3D scene, attach `res://addons/transit_coordinator/editor/stop_marker.gd`, and set its `Stop Id` in the Inspector.
3. Add the same stop ID to the coordinator configuration used by your game. The marker is a visual authoring aid only: it does not create a graph stop, supply a location to the coordinator, or check physical vehicle or passenger positions. Your game must map IDs to real scene locations and verify safety before acknowledging movement.
4. Copy the `examples` folder into your project to try the two included examples. Run the logical quickstart with `godot --headless --path <project> --script res://examples/quickstart.gd`, or the scripted collision-platform transfer with `godot --headless --path <project> --script res://examples/physical_transfer.gd`. The quickstart acknowledges simulated actions; the physical example is a small fixed scene, not a complete game controller.
5. Read `API.md` for the tick sequence, event tokens, adapter/controller responsibilities, recovery and trusted-save requirements. Test your own scene, controller and configuration; the example scenes are not a general performance or compatibility guarantee.

To remove the optional editor tool, disable **Transit Coordinator Tools** in Project Settings → Plugins before removing the copied add-on folder. Removing the add-on also removes the runtime scripts; back up and migrate any scenes and code that reference them first.
