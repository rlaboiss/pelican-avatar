"""Unit testing suite for the Avatar Plugin"""
from __future__ import print_function

## Copyright (C) 2015, 2021  Rafael Laboissière <rafael@laboissiere.net>
##
## This program is free software: you can redistribute it and/or modify it
## under the terms of the GNU General Affero Public License as published by
## the Free Software Foundation, either version 3 of the License, or (at
## your option) any later version.
##
## This program is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## Affero General Public License for more details.
##
## You should have received a copy of the GNU Affero General Public License
## along with this program.  If not, see http://www.gnu.org/licenses/.

import os
import re
import unittest
from tempfile import mkdtemp
from shutil import rmtree

from . import avatar
from pelican import Pelican
from pelican.settings import read_settings


AUTHOR_EMAIL = 'bart.simpson@example.com'
LIBRAVATAR_BASE_URL = 'http://cdn.libravatar.org/avatar/'


class TestAvatarURL (unittest.TestCase):
    """Class for testing the URL output of the Avatar plugin"""

    def setUp (self, override = None):
        self.output_path = mkdtemp (prefix = 'pelicantests.')
        self.content_path = mkdtemp (prefix = 'pelicantests.')
        with open (os.path.join(self.content_path, "article_infos.html"), "w") as article_infos_file:
            article_infos_file.write('''
<footer class="post-info">
        <div align="center">
                <img src="{{ article.author_avatar }}">
        </div>
</footer>
''')

        settings = {
            'PATH': self.content_path,
            'THEME_TEMPLATES_OVERRIDES': [self.content_path],
            'OUTPUT_PATH': self.output_path,
            'PLUGINS': [avatar],
            'CACHE_CONTENT': False
        }
        if override:
            settings.update (override)

        with open (os.path.join (self.content_path, 'test.md'), 'w') as test_md_file:
            test_md_file.write ('Title: Test\nDate: 2019-09-05\nEmail: ' + AUTHOR_EMAIL + '\n\n')

        self.settings = read_settings (override = settings)
        pelican = Pelican (settings = self.settings)
        pelican.run ()

    def tearDown (self):
        rmtree (self.output_path)
        rmtree (self.content_path)

    def test_url (self, options = ''):
        with open (os.path.join (self.output_path, 'test.html'), 'r') as test_html_file:
            found = False
            for line in test_html_file.readlines ():
                if re.search (LIBRAVATAR_BASE_URL + "[0-9a-f]+" + options, line):
                    found = True
                    break
            assert found

class TestAvatarMissing (TestAvatarURL):
    """Class for testing the "missing picture" option"""

    def setUp (self, override = None):
        self.library = 'wavatar'
        TestAvatarURL.setUp (self,
                             override = {'AVATAR_MISSING': self.library})

    def test_url (self):
        TestAvatarURL.test_url (self, r'\?d=' + self.library)


class TestAvatarSize (TestAvatarURL):
    """Class for testing the size option"""

    def setUp (self, override = None):
        self.size = 100
        TestAvatarURL.setUp (self,
                             override = {'AVATAR_SIZE': self.size})

    def test_url (self):
        TestAvatarURL.test_url (self, r'\?s=' + str (self.size))
