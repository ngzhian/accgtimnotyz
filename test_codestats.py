import os
import codestats
import unittest
import tempfile

class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, codestats.app.config['DATABASE'] = tempfile.mkstemp()
        codestats.app.config['TESTING'] = True
        self.app = codestats.app.test_client()
        # codestats.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(codestats.app.config['DATABASE'])

    def test_home_page(self):
        rv = self.app.get('/')
        self.assertIn(b'<form', rv.data)

    def test_analyse_snippet(self):
        rv = self.app.post('/s', data=dict(
            snippet='var x;'
        ))
        self.assertIn(b'', rv.data)

if __name__ == '__main__':
    unittest.main()
