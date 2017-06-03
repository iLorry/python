# -*- coding: utf-8 -*-
'''
#=============================================================================
#     FileName: demo_test.py
#         Desc:
#       Author: Lorry
#        Email: cclorry@gmail.com
#     HomePage:
#      Version: 0.0.1
#   LastChange: 2017-05-17 18:00:17
#      History:
#=============================================================================

'''

import sys
import unittest2 as unittest

import demo


class Case(unittest.TestCase):
    @classmethod
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_sum(self):
        self.assertEqual(demo.sum(32, 1), 33, 'Test sum() fail!')

    def test_string(self):
        string = 'hello'
        demo.string(string)

        if not hasattr(sys.stdout, 'getvalue'):
            self.fail('Need to run in buffered mode.')

        self.assertEqual(sys.stdout.getvalue().strip(), string,
                         'Test string() fail!')

    def test_true(self):
        self.assertTrue(demo.true(), 'Test true() fail!')


if __name__ == '__main__':
    unittest.main(module=__name__, buffer=True, verbosity=2, exit=False)

# vim: noai:ts=4:sw=4
