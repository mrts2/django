# -*- coding: utf-8 -*-
# Unit and doctests for specific database backends.
import unittest
from django.db import connection
from django.db.backends.signals import connection_created
from django.conf import settings

class Callproc(unittest.TestCase):

    def test_dbms_session(self):
        # If the backend is Oracle, test that we can call a standard
        # stored procedure through our cursor wrapper.
        if settings.DATABASE_ENGINE == 'oracle':
            cursor = connection.cursor()
            cursor.callproc('DBMS_SESSION.SET_IDENTIFIER',
                            ['_django_testing!',])
            return True
        else:
            return True

def connection_created_test(sender, **kwargs):
    print 'connection_created signal'

__test__ = {'API_TESTS': ''}

# Unfortunately with sqlite3 the in-memory test database cannot be
# closed, and so it cannot be re-opened during testing, and so we
# sadly disable this test for now.
if settings.DATABASE_ENGINE != 'sqlite3':
    __test__['API_TESTS'] += """
>>> connection_created.connect(connection_created_test)
>>> connection.close() # Ensure the connection is closed
>>> cursor = connection.cursor()
connection_created signal
>>> connection_created.disconnect(connection_created_test)
>>> cursor = connection.cursor()
"""

if __name__ == '__main__':
    unittest.main()
