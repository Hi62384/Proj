# Owned fixture inputs

`fixture.c` is a synthetic native DLL source. `fixture.gdextension` is a path-testing descriptor; the DLL is not a functioning Godot extension and must not be presented as an exportable example. For a local architecture check in an x64 MSVC developer prompt, run `cl /LD /TC fixture.c` followed by `dumpbin /headers fixture.dll`. The comparison still requires a real GDExtension and actual engine exports.
