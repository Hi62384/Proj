"""Fail-closed launch-contract research; never connected to the real worker.

Expected identities must be produced by an independent trusted provisioner.
This demonstrates handle lifetime and mismatch handling, not trusted provisioning,
ACL validation, network isolation, or a safe Windows process launch.
"""
from contextlib import ExitStack
from dataclasses import dataclass

from portfolio_manager.tests.windows_path_research import DirectoryHandle


@dataclass(frozen=True)
class ExpectedLayout:
    parent: tuple[int, int, int]
    home: tuple[int, int, int]
    workspace: tuple[int, int, int]


class ResearchLaunchPlan:
    """Own verified handles without exposing paths to an unverified launcher."""
    def __init__(self, parent_path, layout):
        self._handles = ExitStack()
        try:
            # This rejects a reparse point at the final component only; callers
            # must still establish trust in every ancestor and its permissions.
            parent = self._handles.enter_context(DirectoryHandle(parent_path, reject_final_reparse=True))
            if parent.identity != layout.parent:
                raise OSError('Parent identity mismatch')
            self._home = self._handles.enter_context(parent.probe_open_verified_child('home', layout.home))
            self._workspace = self._handles.enter_context(parent.probe_open_verified_child('workspace', layout.workspace))
            if self._home.identity == self._workspace.identity:
                raise OSError('Home and workspace must be distinct')
        except BaseException:
            self._handles.close()
            raise
        self._closed = False

    def read_workspace_fixture(self, name, identity, limit):
        if self._closed:
            raise ValueError('Launch plan is closed')
        return self._workspace.probe_read_verified_file(name, identity, limit)

    def launch(self):
        # CreateProcessW takes path strings; identity/ACL continuity and Codex
        # startup canonicalization are unresolved. Never silently downgrade.
        raise NotImplementedError('Protected process launch has not been verified')

    def close(self):
        self._handles.close()
        self._closed = True

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        self.close()
