# coding=utf-8
#
# pyb_init - pybuilder project initialization
#
# Copyright (C) 2013 Maximilien Riehl <maximilien.riehl@gmail.com>
#
#        DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#                    Version 2, December 2004
#
# Everyone is permitted to copy and distribute verbatim or modified
# copies of this license document, and changing it is allowed as long
# as the name is changed.
#
#            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#   TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION
#
#  0. You just DO WHAT THE FUCK YOU WANT TO.

from __future__ import absolute_import
import unittest
from mockito import when, verify, any as any_value, unstub, mock

import pyb_init
from pyb_init import entry_point
from pyb_init.configuration import configuration


class PybInitTests(unittest.TestCase):

    def tearDown(self):
        unstub()

    def setUp(self):
        self.set_up_no_op_reactor()

    def set_up_no_op_reactor(self):
        mock_reactor = mock()
        when(mock_reactor).get_tasks().thenReturn([])
        when(pyb_init.reactor).for_local_initialization().thenReturn(
            mock_reactor)
        when(pyb_init.reactor).for_github_clone(
            user=any_value(), project=any_value()).thenReturn(mock_reactor)
        when(pyb_init.reactor).for_git_clone(
            git_url=any_value()).thenReturn(mock_reactor)
        when(pyb_init.reactor).for_svn_checkout(
            svn_url=any_value()).thenReturn(mock_reactor)

    def test_should_invoke_docopt_with_version_and_docstring(self):
        when(
            pyb_init).docopt(
                doc=any_value(
                ), version=any_value()).thenReturn({'local': True,
                                                    'github': False,
                                                    'git': False,
                                                    'svn': False,
                                                    '--virtualenv': 'virtualenv'})

        entry_point()

        verify(pyb_init).docopt(doc=pyb_init.__doc__, version='${version}')

    def test_should_run_local_initialization_when_argument_is_given(self):
        when(
            pyb_init).docopt(
                doc=any_value(
                ), version=any_value()).thenReturn({'local': True,
                                                    'github': False,
                                                    'git': False,
                                                    'svn': False,
                                                    '--virtualenv': 'virtualenv'})

        entry_point()

        verify(pyb_init.reactor).for_local_initialization()

    def test_should_run_github_initialization_when_argument_is_given(self):
        when(
            pyb_init).docopt(
                doc=any_value(
                ), version=any_value()).thenReturn({'local': False,
                                                    'git': False,
                                                    'github': True,
                                                    'svn': False,
                                                    '<user>': 'coder1234',
                                                    '<project>': 'committer',
                                                    '--virtualenv': 'virtualenv'})

        entry_point()

        verify(pyb_init.reactor).for_github_clone(
            user='coder1234', project='committer')

    def test_should_run_git_initialization_when_argument_is_given(self):
        when(
            pyb_init).docopt(
                doc=any_value(
                ), version=any_value()).thenReturn({'local': False,
                                                    'github': False,
                                                    'git': True,
                                                    'svn': False,
                                                    '<git_url>': 'foo',
                                                    '--virtualenv': 'virtualenv'})

        entry_point()

        verify(pyb_init.reactor).for_git_clone(git_url='foo')

    def test_should_run_all_tasks_until_finished(self):
        when(
            pyb_init).docopt(
                doc=any_value(
                ), version=any_value()).thenReturn({'local': True,
                                                    'github': False,
                                                    'git': False,
                                                    'svn': False,
                                                    '--virtualenv': 'virtualenv'})
        mock_reactor = mock()
        mock_task_1 = mock()
        mock_task_2 = mock()
        when(pyb_init.reactor).for_local_initialization().thenReturn(
            mock_reactor)
        when(mock_reactor).get_tasks().thenReturn([mock_task_1, mock_task_2])

        entry_point()

        verify(mock_task_1).execute()
        verify(mock_task_2).execute()

    def test_should_configure_virtualenv_name(self):
        when(
            pyb_init).docopt(
                doc=any_value(
                ), version=any_value()).thenReturn({'local': True,
                                                    'github': False,
                                                    'git': False,
                                                    'svn': False,
                                                    '--virtualenv': 'foobar'})

        entry_point()

        self.assertEqual(configuration['virtualenv_name'], 'foobar')

    def test_should_configure_system_site_packages_when_option_is_provided(self):
        when(
            pyb_init).docopt(
                doc=any_value(
                ), version=any_value()).thenReturn({'local': True,
                                                    'github': False,
                                                    'git': False,
                                                    'svn': False,
                                                    '--system-site-packages': True,
                                                    '--virtualenv': 'venv'})

        entry_point()

        self.assertTrue(configuration['virtualenv_use_system_site_packages'])

    def test_should_not_configure_system_site_packages_when_option_is_not_provided(self):
        when(
            pyb_init).docopt(
                doc=any_value(
                ), version=any_value()).thenReturn({'local': True,
                                                    'github': False,
                                                    'git': False,
                                                    'svn': False,
                                                    '-s': False,
                                                    '--virtualenv': 'venv'})

        entry_point()

        self.assertFalse(configuration['virtualenv_use_system_site_packages'])

    def test_should_eat_exceptions_and_output_error_message_instead(self):
        when(
            pyb_init).docopt(
                doc=any_value(
                ), version=any_value()).thenReturn({'local': True,
                                                    'github': False,
                                                    'git': False,
                                                    'svn': False,
                                                    '--virtualenv': 'foobar'})
        when(pyb_init.reactor).for_local_initialization().thenRaise(
            RuntimeError('too fat to fly'))
        when(pyb_init.logger).error(any_value()).thenReturn(None)

        entry_point()

        verify(pyb_init.logger).error('too fat to fly')

    def test_should_run_svn_checkout_when_argument_is_given(self):
        when(
            pyb_init).docopt(
                doc=any_value(
                ), version=any_value()).thenReturn({'local': False,
                                                    'git': False,
                                                    'github': False,
                                                    'svn': True,
                                                    '<svn_url>': 'http://code/foo/bar',
                                                    '--virtualenv': 'virtualenv'})

        entry_point()

        verify(pyb_init.reactor).for_svn_checkout(
            svn_url='http://code/foo/bar')
