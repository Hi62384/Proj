"""Independent action/scope rules. Local UI is the only rule writer."""
from pathlib import Path
from .permissions import Denied

ACTIONS=('read','write','create','delete')
DECISIONS=('ask','allow','deny')


class FilePolicy:
    def __init__(self, rules=()):
        self.rules=list(rules)
        self.session=[]

    @staticmethod
    def rule(path, scope, decisions):
        if scope not in ('file','folder','recursive'):raise ValueError('Unknown scope')
        if any(a not in ACTIONS or d not in DECISIONS for a,d in decisions.items()):raise ValueError('Invalid rule')
        return {'path':str(Path(path).resolve()),'scope':scope,'decisions':dict(decisions)}

    def decision(self,path,action):
        if action not in ACTIONS:raise Denied('Unknown file operation')
        path=Path(path).resolve();matches=[]
        for index,rule in enumerate(self.rules+self.session):
            root=Path(rule['path']);scope=rule['scope']
            match=(path==root if scope=='file' else path==root or (path.parent==root if scope=='folder' else path.is_relative_to(root)))
            if match and action in rule['decisions']:
                matches.append((len(root.parts),scope=='file',index,rule['decisions'][action]))
        # An explicit deny anywhere in the matching scopes always wins.
        if any(x[3]=='deny' for x in matches):return 'deny'
        return max(matches)[3] if matches else 'ask'
