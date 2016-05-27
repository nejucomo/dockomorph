from mock import ANY, sentinel, call

from dockomorph.tests.logutil import LogMockingTestCase
from dockomorph.orchestrator import Orchestrator


class OchestratorTests (LogMockingTestCase):
    def test_update_repository(self):
        S = sentinel
        orc = Orchestrator(S.FAKE_REACTOR)

        # Mock surgery:
        orc._repoman = self.make_mock()
        orc._dockherd = self.make_mock()

        result = orc.update_repository(S.NAME, S.REPOURL, S.TAG)

        m_def = orc._repoman.update_repository.return_value

        self.assertIs(result, m_def)

        self.assert_calls_equal(
            orc._repoman,
            [call.update_repository(S.NAME, S.REPOURL, S.TAG),
             call.update_repository().addCallback(ANY)])

        # Snag the callback out of the mock deferred:
        [m_def_call] = m_def.mock_calls
        (_, args, _) = m_def_call
        (cb,) = args

        result2 = cb((S.FAKE_ARG1, S.FAKE_ARG2))

        self.assertIs(result2, orc._dockherd.build_and_deploy.return_value)

        self.assert_calls_equal(
            orc._dockherd,
            [call.build_and_deploy(S.FAKE_ARG1, S.FAKE_ARG2)])
