/* Owned import-cycle fixture. Never call this function: it recurses forever. */
__declspec(dllimport) int root_value(void);
__declspec(dllexport) int middle_value(void) { return root_value(); }
