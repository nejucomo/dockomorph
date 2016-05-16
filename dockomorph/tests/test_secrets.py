import os
import errno

from mock import call

from dockomorph import secrets
from dockomorph.tests.logutil import LogMockingTestCase, ArgIsLogRecord


class create_or_load_secrets_tests (LogMockingTestCase):
    def test_successful_load(self):
        m_FilePath = self.patch('twisted.python.filepath.FilePath')
        m_getLogger = self.patch('logging.getLogger')
        m_urandom = self.patch('os.urandom')

        m_secretsdir = m_FilePath.return_value
        m_secretsdir.makedirs.side_effect = os.error(
            errno.EEXIST,
            'fake-dir-already-exists',
        )

        result = secrets.create_or_load_secret('banana')

        m_path = m_secretsdir.child.return_value
        m_file = m_path.open.return_value
        m_file_ctx = m_file.__enter__.return_value

        self.assertIs(result, m_file_ctx.read.return_value)

        # Bug: This is over-specified and brittle:
        self.assert_calls_equal(
            m_FilePath,
            [call(secrets._SecretsDir),
             call().makedirs(),
             call().child('banana'),
             call().child().open('r'),
             call().child().open().__enter__(),
             call().child().open().__enter__().read(),
             call().child().open().__exit__(None, None, None)])

        # No urandom or logging in this case:
        self.assert_calls_equal(
            m_urandom,
            [])

        self.assert_calls_equal(
            m_getLogger,
            [])

    def test_no_preexisting_secrets_file(self):
        m_FilePath = self.patch('twisted.python.filepath.FilePath')
        m_urandom = self.patch('os.urandom')

        m_secretsdir = m_FilePath.return_value
        m_path = m_secretsdir.child.return_value

        m_write_file = self.make_mock()

        def m_path_open(mode):
            if mode == 'r':
                raise IOError(errno.ENOENT, 'fake-no-entry')
            else:
                assert mode == 'w', repr(mode)
                return m_write_file

        m_path.open.side_effect = m_path_open

        # Exercise target code:
        result = secrets.create_or_load_secret('banana')

        # Verify results:
        self.assertIs(result, m_urandom.return_value.encode.return_value)

        self.assert_calls_equal(
            m_FilePath,
            [call(secrets._SecretsDir),
             call().makedirs(),
             call().child('banana'),
             call().child().open('r'),
             call().child().open('w'),
             ])

        self.assert_calls_equal(
            m_urandom,
            [call(secrets._SecretByteSize),
             call().encode('hex')])

        self.assert_calls_equal(
            self.m_loghandler,
            [call.handle(
                ArgIsLogRecord(
                    levelname='INFO',
                    msg='Initialized secret %r to: %s'))])

    def test_makedirs_error(self):
        m_FilePath = self.patch('twisted.python.filepath.FilePath')

        m_secretsdir = m_FilePath.return_value
        m_secretsdir.makedirs.side_effect = os.error(
            errno.EACCES,
            'fake-access-error',
        )

        self.assertRaises(os.error, secrets.create_or_load_secret, 'banana')

    def test_read_error(self):
        m_FilePath = self.patch('twisted.python.filepath.FilePath')

        m_secretsdir = m_FilePath.return_value
        m_path = m_secretsdir.child.return_value
        m_path.open.side_effect = IOError(
            errno.ENODEV,
            'fake-no-dev-error',
        )

        self.assertRaises(IOError, secrets.create_or_load_secret, 'banana')
