#!/usr/bin/env python
"""Tests for `md2quip` package."""

import unittest

from click.testing import CliRunner

from md2quip import cli
from md2quip.md2quip import md2quip

"""
TODO: Could this be replaced by a real python Mock object that has a side_effect
call back to allow us to fake the resposes from the Quip API?
"""


class MockQuip(object):
    def __init__(self) -> None:
        self._folder_cache = {
            'DVRAOArKRoo': {
                'children': [{'folder_id': 'TdIAOAZPeNB'}],
                'folder': {
                    'color': 'manila',
                    'created_usec': 1640957080538001,
                    'creator_id': 'MTVAEAAR5hw',
                    'folder_type': 'shared',
                    'id': 'DVRAOArKRoo',
                    'inherit_mode': 'inherit',
                    'link': 'https://mccartney.quip.com/DVRAOArKRoo',
                    'parent_id': 'LUBAOAbA72T',
                    'title': 'simonmcc',
                    'updated_usec': 1651407995611654,
                },
                'member_ids': [],
            },
            'LUBAOAbA72T': {
                'children': [{'thread_id': 'FHcAAAgmJDW'}, {'folder_id': 'DVRAOArKRoo'}],
                'folder': {
                    'created_usec': 1640198655207040,
                    'creator_id': 'MTVAEAAR5hw',
                    'folder_type': 'shared',
                    'id': 'LUBAOAbA72T',
                    'inherit_mode': 'inherit',
                    'link': 'https://mccartney.quip.com/folder/mccartney',
                    'title': 'Mccartney',
                    'updated_usec': 1650889973865258,
                },
                'member_ids': ['MTVAEAAR5hw'],
            },
            'TdIAOAZPeNB': {
                'children': [{'thread_id': 'aHTAAARyd1D'}, {'thread_id': 'IYCAAAcDu8x'}],
                'folder': {
                    'color': 'manila',
                    'created_usec': 1641121436075173,
                    'creator_id': 'MTVAEAAR5hw',
                    'folder_type': 'shared',
                    'id': 'TdIAOAZPeNB',
                    'inherit_mode': 'inherit',
                    'link': 'https://mccartney.quip.com/TdIAOAZPeNB',
                    'parent_id': 'DVRAOArKRoo',
                    'title': 'md2quip',
                    'updated_usec': 1651210481294550,
                },
                'member_ids': [],
            },
        }

        self._thread_cache = {
            'FHcAAAgmJDW': {
                'access_levels': {'MTVAEAAR5hw': {'access_level': 'OWN'}},
                'expanded_user_ids': ['MTVAEAAR5hw'],
                'html': "<h1 id='FHcACAsMaEC'>.md2quip metadata</h1>\n"
                '\n'
                "<p id='FHcACAYoQVw' class='line'>README.md - thread_id_1</p>\n"
                '\n'
                "<p id='FHcACAMpIEn' class='line'>\u200b</p>\n"
                '\n'
                "<p id='FHcACAHlGTo' class='line'>CHANGELOG.md</p>\n"
                '\n',
                'invited_user_emails': [],
                'shared_folder_ids': ['LUBAOAbA72T'],
                'thread': {
                    'author_id': 'MTVAEAAR5hw',
                    'created_usec': 1650706741714383,
                    'document_id': 'FHcABA9sbmR',
                    'id': 'FHcAAAgmJDW',
                    'is_deleted': False,
                    'is_template': False,
                    'link': 'https://mccartney.quip.com/S32JAzuw28h7',
                    'owning_company_id': 'WBJAcAuh3TV',
                    'thread_class': 'document',
                    'title': '.md2quip metadata',
                    'type': 'document',
                    'updated_usec': 1650706742303332,
                },
                'user_ids': [],
            },
            'aHTAAARyd1D': {
                'access_levels': {'MTVAEAAR5hw': {'access_level': 'OWN'}},
                'expanded_user_ids': ['MTVAEAAR5hw'],
                'html': "<h1 id='temp:C:aHTf239fdb0665944c0bcf7b8f5c'>README.md</h1>\n"
                '\n'
                "<p id='temp:C:aHT8b15a895678d467fa8033fb34' class='line'>Hmmm, title "
                '&amp; filename mismatch might be a pain</p>\n'
                '\n',
                'invited_user_emails': [],
                'shared_folder_ids': ['TdIAOAZPeNB'],
                'thread': {
                    'author_id': 'MTVAEAAR5hw',
                    'created_usec': 1650704764831020,
                    'document_id': 'aHTABAEC6MW',
                    'id': 'aHTAAARyd1D',
                    'is_deleted': False,
                    'is_template': False,
                    'link': 'https://mccartney.quip.com/0ArJAd410vTy',
                    'owning_company_id': 'WBJAcAuh3TV',
                    'thread_class': 'document',
                    'title': 'README.md',
                    'type': 'document',
                    'updated_usec': 1650704805930940,
                },
                'user_ids': [],
            },
            'IYCAAAcDu8x': {
                'access_levels': {'MTVAEAAR5hw': {'access_level': 'OWN'}},
                'expanded_user_ids': ['MTVAEAAR5hw'],
                'html': "<h1 id='temp:C:IYC0d7d1fee67781971cb0f8267a'>md2quip</h1>\n"
                '\n'
                "<p id='temp:C:IYCb2050653a910404db6f17b8c6' class='line'>\u200b</p>\n"
                '\n'
                "<p id='temp:C:IYC799be3cb091f45de9413899ff' class='line'>\u200b</p>\n"
                '\n'
                "<p id='temp:C:IYC96aed9bfbe9dff025f93f22f8' class='line'>this was "
                'created in Quip</p>\n'
                '\n'
                "<p id='temp:C:IYCc5eb2aad67f8848b78d4143c6' class='line'>\u200b</p>\n"
                '\n',
                'invited_user_emails': [],
                'shared_folder_ids': ['TdIAOAZPeNB'],
                'thread': {
                    'author_id': 'MTVAEAAR5hw',
                    'created_usec': 1641142276180646,
                    'document_id': 'IYCABAnBMf9',
                    'id': 'IYCAAAcDu8x',
                    'is_deleted': False,
                    'is_template': False,
                    'link': 'https://mccartney.quip.com/GPgpAu5DASKC',
                    'owning_company_id': 'WBJAcAuh3TV',
                    'thread_class': 'document',
                    'title': 'md2quip',
                    'type': 'document',
                    'updated_usec': 1649705490970091,
                },
                'user_ids': [],
            },
        }
        return

    def get_root_url(self):
        return 'https://mccartney.quip.com/JGMmOeQyhKz7/Mccartney'

    def get_folder(self, id):
        # fake the secret_path lookup for the 1 folder we're interested in
        if id == 'JGMmOeQyhKz7':
            return self._folder_cache['LUBAOAbA72T']
        else:
            return self._folder_cache.get(id)

    def get_thread(self, id):
        return self._thread_cache.get(id)
        return

    # def new_document(content, format='markdown', member_ids=[root_folder_id]):
    def new_document(content, format='markdown', member_ids=[]):
        return


class TestMd2Quip(unittest.TestCase):
    def test_command_line_interface(self):
        """Test the CLI."""
        runner = CliRunner()

        # This should error out on lack of Quip API token
        result = runner.invoke(cli.cli)
        self.assertEqual(result.exit_code, 2)
        self.assertIn('Error: Missing option \'--quip-api-access-token\'.', result.output)

    def test_find_folders(self):
        q = MockQuip()
        m = md2quip(q.get_root_url(), quip_client=q)
        m.show_folders()


if __name__ == '__main__':
    unittest.main()
