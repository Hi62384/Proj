__declspec(dllimport) int middle_value(void);
__declspec(dllexport) int root_value(void) { return middle_value(); }
