/* A deliberately unobservable static import: no test invokes this function. */
#include <windows.h>
__declspec(dllexport) HMODULE dynamic_fixture(void) {
    return LoadLibraryW(L"optional-runtime.dll");
}
