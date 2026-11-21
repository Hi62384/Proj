# Storefront and demo notes — unpublished draft

These notes are for local review. No listing, price, distribution channel or publication is approved.

**Working title:** NPC Transit Coordinator for Godot 4

**Draft description:** Coordinate scheduled passenger journeys across finite-capacity vehicles and transfers. The prototype provides a timetable graph, FIFO seat claims, movement acknowledgment, disruption recovery and versioned local snapshots. A small 3D example and an optional navigation movement bridge illustrate integration with a game's own NPC and vehicle controllers.

**Explicit scope:** The component does not supply a complete pathfinding system, vehicle physics, multiplayer synchronization or automatic verification that vehicles are physically at their scheduled stops. Routing does not predict future seat capacity. Compatibility, licensing and production readiness remain under review. Current tests are local on Godot 4.5.1 and do not establish a performance guarantee or a measured advantage over alternatives.

**Possible demo sequence after final QA:** Show twenty passengers and the transfer; pause to show queue and capacity; disable a service and show the actual recovery; demonstrate save and restore using a verified recording. Capture the real running software, identify any scripted motion, and remove any claim the final tests do not support.

**Before any listing:** Complete the local release checklist, verify current platform rules and fees, choose and review rights/license terms, establish support and refund terms as applicable, review truthful final copy, and obtain the owner's separate publication approval. No prices or performance claims are authorized by this document.
