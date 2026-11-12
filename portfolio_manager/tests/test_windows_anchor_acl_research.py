"""One-directory DACL research; all security changes are inside disposable folders."""
import os
from pathlib import Path
import tempfile
import unittest
import subprocess


@unittest.skipUnless(os.name == 'nt', 'Windows security descriptors are required')
class AnchorAclResearchTests(unittest.TestCase):
    def setUp(self):
        import win32api, win32con, win32security
        self.security = win32security
        self.temp = tempfile.TemporaryDirectory(prefix='portfolio-anchor-acl-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'anchor'
        self.root.mkdir()
        token = win32security.OpenProcessToken(win32api.GetCurrentProcess(), win32con.TOKEN_QUERY)
        try: self.user = win32security.GetTokenInformation(token, win32security.TokenUser)[0]
        finally: token.Close()
        self.system = win32security.ConvertStringSidToSid('S-1-5-18')
        self.everyone = win32security.ConvertStringSidToSid('S-1-1-0')
        self.owner = win32security.ConvertSidToStringSid(self.user)
        self.set_acl(False)

    def set_acl(self, broad, path=None):
        s = self.security
        acl = s.ACL()
        for sid in (self.user, self.system):
            acl.AddAccessAllowedAce(s.ACL_REVISION, 0x1f01ff, sid)
        if broad:
            acl.AddAccessAllowedAce(s.ACL_REVISION, 0x1200a9, self.everyone)
        s.SetNamedSecurityInfo(str(path or self.root), s.SE_FILE_OBJECT,
                               s.DACL_SECURITY_INFORMATION | s.PROTECTED_DACL_SECURITY_INFORMATION,
                               None, None, acl, None)

    def test_expected_owner_identity_and_explicit_acl_pass(self):
        from portfolio_manager.tests.windows_path_research import DirectoryHandle
        from portfolio_manager.tests.windows_anchor_acl_research import audit_open_anchor
        with DirectoryHandle(self.root, reject_final_reparse=True, read_security=True) as anchor:
            result = audit_open_anchor(anchor, expected_identity=anchor.identity, expected_owner=self.owner,
                                       allowed_masks={self.owner: 0x1f01ff, 'S-1-5-18': 0x1f01ff},
                                       required_masks={self.owner: 0x1f01ff, 'S-1-5-18': 0x1f01ff})
            self.assertEqual(result['ace_count'], 2)
            with self.assertRaises(ValueError):
                audit_open_anchor(anchor, expected_identity=(0, 0, 0), expected_owner=self.owner,
                                  allowed_masks={self.owner: 0x1f01ff, 'S-1-5-18': 0x1f01ff}, required_masks={})
            with self.assertRaises(ValueError):
                audit_open_anchor(anchor, expected_identity=anchor.identity, expected_owner=self.owner,
                                  allowed_masks={self.owner: 0x1f01ff, 'S-1-5-18': 0x1f01ff},
                                  required_masks={'S-1-1-0': 1})
            with self.assertRaises(ValueError):
                audit_open_anchor(anchor, expected_identity=anchor.identity, expected_owner=self.owner,
                                  allowed_masks={self.owner: 0x1200a9, 'S-1-5-18': 0x1f01ff}, required_masks={})

    def test_broad_access_entry_is_rejected(self):
        from portfolio_manager.tests.windows_path_research import DirectoryHandle
        from portfolio_manager.tests.windows_anchor_acl_research import audit_open_anchor
        self.set_acl(True)
        with DirectoryHandle(self.root, reject_final_reparse=True, read_security=True) as anchor:
            with self.assertRaises(ValueError):
                audit_open_anchor(anchor, expected_identity=anchor.identity, expected_owner=self.owner,
                                  allowed_masks={self.owner: 0x1f01ff, 'S-1-5-18': 0x1f01ff}, required_masks={})

    def test_handle_relative_chain_rejects_child_acl_tampering(self):
        from portfolio_manager.tests.windows_path_research import DirectoryHandle
        from portfolio_manager.tests.windows_anchor_acl_research import audit_open_chain
        child = self.root / 'child'; child.mkdir()
        self.set_acl(False, child)
        with DirectoryHandle(child, reject_final_reparse=True) as known:
            child_identity = known.identity
        with DirectoryHandle(self.root, reject_final_reparse=True, read_security=True) as anchor:
            shared = {'owner': self.owner, 'allowed_masks': {self.owner: 0x1f01ff, 'S-1-5-18': 0x1f01ff},
                      'required_masks': {self.owner: 0x1f01ff}}
            policies = [dict(shared, identity=anchor.identity), dict(shared, name='child', identity=child_identity)]
            self.assertEqual(len(audit_open_chain(anchor, policies)), 2)
            self.set_acl(True, child)
            with self.assertRaises(ValueError):
                audit_open_chain(anchor, policies)

    def test_chain_rejects_junction_even_with_target_identity(self):
        from portfolio_manager.tests.windows_path_research import DirectoryHandle
        from portfolio_manager.tests.windows_anchor_acl_research import audit_open_chain
        target = Path(self.temp.name) / 'outside'; target.mkdir(); self.set_acl(False, target)
        link = self.root / 'escape'
        result = subprocess.run([os.environ.get('COMSPEC', r'C:\Windows\System32\cmd.exe'),
                                 '/d', '/c', 'mklink', '/J', str(link), str(target)],
                                capture_output=True, timeout=10)
        if result.returncode:
            self.skipTest('Disposable junction creation unavailable')
        self.addCleanup(lambda: link.rmdir() if link.exists() else None)
        with DirectoryHandle(target, reject_final_reparse=True) as known:
            target_identity = known.identity
        with DirectoryHandle(self.root, reject_final_reparse=True, read_security=True) as anchor:
            shared = {'owner': self.owner, 'allowed_masks': {self.owner: 0x1f01ff, 'S-1-5-18': 0x1f01ff},
                      'required_masks': {self.owner: 0x1f01ff}}
            policies = [dict(shared, identity=anchor.identity), dict(shared, name='escape', identity=target_identity)]
            with self.assertRaises(OSError):
                audit_open_chain(anchor, policies)
