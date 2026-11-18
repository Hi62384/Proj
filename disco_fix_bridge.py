from pathlib import Path

path = Path(r'C:\Users\User1\Documents\Downloads\Disco\disco_desktop\bridge.py')
source = path.read_text(encoding='utf-8')
old = '        link.evaluate("element => element.click()")\n\n    def server(self, identity):'
new = '''        link.evaluate("element => element.click()")
        try:
            self.page.wait_for_function("target => location.pathname === target", arg=path, timeout=10000)
        except PlaywrightTimeout:
            raise BridgeError("Discord did not open the requested chat. Retry navigation.") from None

    def server(self, identity):'''
if old not in source:
    raise SystemExit('Expected navigation code was not found; no changes made.')
path.write_text(source.replace(old, new, 1), encoding='utf-8')
