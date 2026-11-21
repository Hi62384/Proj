"""Saved chat selections follow the one-time category move."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from portfolio_manager.integration import ManagerHost


class SelectionMigrationTests(unittest.TestCase):
    def test_removed_projects_container_keeps_exact_chat_selection(self):
        from portfolio_manager.tests.test_runner import _record
        from business_portfolio.tools.build_browser import parse_project
        with TemporaryDirectory() as temp:
            root = Path(temp); repo = root / 'repo'
            legacy = _record(repo, 'DEMO-050')
            old_folder = legacy.parent / 'demo-050'
            (old_folder / 'work').mkdir(parents=True)
            record = old_folder / 'project.md'
            legacy.rename(record)
            nested_work = old_folder / 'work/projects/tool.txt'
            nested_work.parent.mkdir()
            nested_work.write_text('Project-owned example, not a portfolio container.')
            host = ManagerHost(repo, root / 'state')
            try:
                project_chat = host.workspace('a' * 32, {'path': record.relative_to(repo).as_posix()})
                folder_chat = host.workspace('b' * 32, {'path': old_folder.parent.relative_to(repo).as_posix()})
                work_chat = host.workspace('c' * 32, {'path': nested_work.relative_to(repo).as_posix()})
                moved = old_folder.parent.parent / old_folder.name
                old_folder.rename(moved)
                old_folder.parent.rmdir()
                selection = host.get_workspace(project_chat['id'])['selection']
                self.assertEqual(selection, (moved / 'project.md').relative_to(repo).as_posix())
                self.assertEqual(host.get_workspace(folder_chat['id'])['selection'],
                                 moved.parent.relative_to(repo).as_posix())
                self.assertEqual(host.get_workspace(work_chat['id'])['selection'],
                                 (moved / 'work/projects/tool.txt').relative_to(repo).as_posix())
                context = host.context_info(host.get_workspace(project_chat['id']))
                self.assertEqual(context['project']['id'], 'DEMO-050')
                self.assertEqual(context['project']['work_folder'], (moved / 'work').relative_to(repo).as_posix())
            finally:
                host.close()

    def test_moved_project_selection_reconnects_without_changing_other_chat(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / 'repo'
            old = repo / 'business_portfolio/niches/game-development-marketplaces'
            project = old / 'projects/gdm-001-test.md'
            project.parent.mkdir(parents=True)
            project.write_text('saved project', encoding='utf-8')
            other = repo / 'other.txt'
            other.write_text('other chat', encoding='utf-8')
            host = ManagerHost(repo, root / 'state')
            try:
                first = host.workspace('a' * 32, {})
                second = host.workspace('b' * 32, {})
                host.select(first['id'], project.relative_to(repo).as_posix())
                host.select(second['id'], 'other.txt')
                new = repo / 'business_portfolio/niches/digital-products/game-development-marketplaces'
                new.parent.mkdir()
                old.rename(new)
                restored = host.get_workspace(first['id'])
                self.assertEqual(restored['selection'],
                                 'business_portfolio/niches/digital-products/game-development-marketplaces/projects/gdm-001-test.md')
                self.assertEqual(host.get_workspace(second['id'])['selection'], 'other.txt')
            finally:
                host.close()

    def test_saved_legacy_category_selection_moves_to_equivalent_niche(self):
        with TemporaryDirectory() as temp:
            root=Path(temp);repo=root/'repo'
            old=repo/'business_portfolio/niches/software';old.mkdir(parents=True)
            (repo/'business_portfolio/niches/digital-products/software-apps-and-extensions').mkdir(parents=True)
            host=ManagerHost(repo,root/'state')
            try:
                workspace=host.workspace('c'*32,{})
                host.select(workspace['id'],old.relative_to(repo).as_posix())
                old.rmdir()
                restored=host.get_workspace(workspace['id'])
                self.assertEqual(restored['selection'],
                    'business_portfolio/niches/digital-products/software-apps-and-extensions')
            finally:
                host.close()


if __name__ == '__main__':
    unittest.main()
