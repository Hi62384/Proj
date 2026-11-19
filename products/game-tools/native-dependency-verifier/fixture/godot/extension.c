/* Minimal owned extension for export experiments. Requires the Godot C API header. */
#include "gdextension_interface.h"
__declspec(dllimport) int root_value(void);
static void initialize(void *userdata, GDExtensionInitializationLevel level) {
    (void)userdata; (void)level;
    (void)root_value();
}
static void deinitialize(void *userdata, GDExtensionInitializationLevel level) {
    (void)userdata; (void)level;
}
__declspec(dllexport) GDExtensionBool fixture_init(
    GDExtensionInterfaceGetProcAddress get_proc, GDExtensionClassLibraryPtr library,
    GDExtensionInitialization *initialization) {
    (void)get_proc; (void)library;
    initialization->minimum_initialization_level = GDEXTENSION_INITIALIZATION_SCENE;
    initialization->userdata = 0;
    initialization->initialize = initialize;
    initialization->deinitialize = deinitialize;
    return 1;
}
