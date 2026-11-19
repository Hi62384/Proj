__declspec(dllimport) int leaf_value(void);
__declspec(dllexport) int middle_value(void) { return leaf_value(); }
