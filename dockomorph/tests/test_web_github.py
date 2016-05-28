import json

from twisted.trial import unittest
from twisted.web.server import NOT_DONE_YET
from mock import call

from dockomorph.tests.logutil import LogMockingTestCase, ArgIsLogRecord
from dockomorph.web import github


class WebhookResourceTests (LogMockingTestCase):
    secret = 'fake secret'
    fakeid = 'a fake event id'

    pingmessage = {
        u'hook': {
            u'active': True,
            u'config': {
                u'content_type': u'json',
                u'insecure_ssl': u'0',
                u'secret': secret,
                u'url': u'http://fake_hook_url/',
                },
            u'created_at': u'2014-06-26T02:47:58Z',
            u'events': [u'*'],
            u'id': 2484169,
            u'last_response': {
                u'code': None,
                u'message': None,
                u'status': u'unused',
                },
            u'name': u'web',
            u'test_url': u'/'.join([
                u'https://api.github.com',
                u'repos',
                u':FAKE_GH_ACCT:',
                u':FAKE_REPO:',
                u'hooks',
                u'2484169',
                u'test',
            ]),
            u'updated_at': u'2014-06-26T02:47:58Z',
            u'url': '/'.join([
                u'https://api.github.com',
                u'repos',
                u':FAKE_GH_ACCT:',
                u':FAKE_REPO:',
                u'hooks',
                u'2484169',
            ]),
        },
        u'hook_id': 2484169,
        u'zen': u'Keep it logically awesome.',
    }

    def setUp(self):
        LogMockingTestCase.setUp(self)

        self.sigver = github.SignatureVerifier(self.secret)

        self.m_reactor = self.make_mock()
        self.m_handle_push_tag = self.make_mock()

        self.res = github.WebhookResource(
            self.m_reactor,
            self.secret,
            self.m_handle_push_tag,
        )

        self.assert_calls_equal(
            self.m_loghandler,
            [call.handle(ArgIsLogRecord(levelname='DEBUG', msg='__init__'))])

        # Clear out m_loghandler:
        self.reset_mocks()

    def _setup_mock_request(self, eventtype, body):
        jsonbody = json.dumps(body)
        expsig = self.sigver._calculate_hmacsha1(jsonbody)

        m_request = self.make_mock()
        m_request.content.getvalue.return_value = jsonbody

        headers = {
            'X-Github-Event': eventtype,
            'X-Github-Delivery': self.fakeid,
            'X-Hub-Signature': 'sha1=' + expsig,
            }
        m_request.getHeader.side_effect = headers.get

        return m_request

    def test_isLeaf_resource(self):
        self.assertEqual(True, github.WebhookResource.isLeaf)

    def test_render_GET(self):
        m_request = self._setup_mock_request('fake request type', [])
        r = self.res.render_GET(m_request)

        self.assertEqual(NOT_DONE_YET, r)
        self.assert_calls_equal(
            self.m_handle_push_tag,
            [])

        self.assert_calls_equal(
            m_request,
            [call.setResponseCode(403, 'FORBIDDEN'),
             call.finish()])

    def test_render_POST_ping(self):
        m_request = self._setup_mock_request('ping', self.pingmessage)

        r = self.res.render_POST(m_request)

        self.assertEqual(NOT_DONE_YET, r)
        self.assert_calls_equal(
            m_request,
            [call.getHeader('X-Hub-Signature'),
             call.content.getvalue(),
             call.getHeader('X-Github-Event'),
             call.getHeader('X-Github-Delivery'),
             call.setResponseCode(200, 'OK'),
             call.finish()])

        # Pings do not reach the push handler:
        self.assert_calls_equal(
            self.m_handle_push_tag,
            [])

        self.assert_calls_equal(
            self.m_loghandler,
            [])

    def test_render_POST_ping_tampered(self):
        m_request = self._setup_mock_request('ping', self.pingmessage)

        tweakedmessage = self.pingmessage.copy()
        tweakedmessage['hook_id'] += 1

        m_request.content.getvalue.return_value = \
            json.dumps(tweakedmessage)

        r = self.res.render_POST(m_request)

        self.assertEqual(NOT_DONE_YET, r)
        self.assert_calls_equal(
            m_request,
            [call.getHeader('X-Hub-Signature'),
             call.content.getvalue(),
             call.setResponseCode(403, 'FORBIDDEN'),
             call.finish()])

        self.assert_calls_equal(
            self.m_loghandler,
            [call.handle(ArgIsLogRecord(levelname='WARNING'))])

    def test_render_POST_unhandled_event_type(self):
        m_request = self._setup_mock_request('unknown event type', [])

        r = self.res.render_POST(m_request)

        self.assertEqual(NOT_DONE_YET, r)
        self.assert_calls_equal(
            m_request,
            [call.getHeader('X-Hub-Signature'),
             call.content.getvalue(),
             call.getHeader('X-Github-Event'),
             call.getHeader('X-Github-Delivery'),
             call.setResponseCode(400, 'Event Not Supported'),
             call.finish()])

        self.assert_calls_equal(
            self.m_loghandler,
            [call.handle(
                ArgIsLogRecord(
                    levelname='INFO',
                    msg='Unhandled github %r event %r.'))])

    def test_signed_malformed_JSON(self):
        m_request = self.make_mock()

        self.res._handle_signed_message(m_request, '%@ NOT JSON @%')

        self.assert_calls_equal(
            self.m_loghandler,
            [call.handle(ArgIsLogRecord(levelname='ERROR'))])

        self.assert_calls_equal(
            m_request,
            [call.setResponseCode(400, 'MALFORMED')])

    def _test_handle_bare_event(self, retval, eventtype, msg):
        r = self.res._handle_bare_event('fake id', eventtype, msg)
        self.assertIs(retval, r)

    def test_handle_bare_event_ping(self):
        self._test_handle_bare_event(True, 'ping', 'banana')

    def test_handle_bare_event_push(self):
        self._test_handle_bare_event(True, 'push', 'banana')

        self.assert_calls_equal(
            self.m_reactor,
            [call.callLater(0, self.res._handle_push_event, 'banana')])

    def test_handle_bare_event_some_unsupported_event_type(self):
        self._test_handle_bare_event(
            False,
            '%! some unsupported event type !%',
            'banana',
        )

        self.assert_calls_equal(
            self.m_loghandler,
            [call.handle(
                 ArgIsLogRecord(
                     levelname='INFO',
                     msg='Unhandled github %r event %r.'))])

    def test_handle_push_event_not_dockomorph_tag(self):
        self.res._handle_push_event({'ref': 'refs/heads/master'})

        self.assert_calls_equal(
            self.m_loghandler,
            [call.handle(
                 ArgIsLogRecord(
                     levelname='DEBUG',
                     args=('refs/heads/master',)))])

        self.assert_calls_equal(
            self.m_handle_push_tag,
            [])

    def test_handle_push_event_dockomorph_tag(self):
        self.res._handle_push_event({
            'ref': 'refs/tags/dockomorph.0',
            'repository': {
                'name': 'ossmproj',
                'clone_url': 'fake url',
            },
        })

        self.assert_calls_equal(
            self.m_loghandler,
            [])

        self.assert_calls_equal(
            self.m_handle_push_tag,
            [call('ossmproj', 'fake url', 'dockomorph.0')])


class SignatureVerifierTests (unittest.TestCase):
    def setUp(self):
        self.sigver = github.SignatureVerifier(
            sharedsecret=XHubSignatureTestVector.sharedsecret,
            )

    def test_vector_positive(self):
        self.failUnless(
            self.sigver(
                allegedsig=XHubSignatureTestVector.expectedsig,
                message=XHubSignatureTestVector.body,
                ),
            )

    def test_vector_negative_tampered_sig(self):
        self.failIf(
            self.sigver(
                allegedsig=XHubSignatureTestVector.expectedsig[:-1] + '8',
                message=XHubSignatureTestVector.body,
                ),
            )

    def test_vector_negative_sig_wrong_len(self):
        self.failIf(
            self.sigver(
                allegedsig=XHubSignatureTestVector.expectedsig[:-1],
                message=XHubSignatureTestVector.body,
                ),
            )

    def test_vector_negative_tampered_body(self):
        self.failIf(
            self.sigver(
                allegedsig=XHubSignatureTestVector.expectedsig,
                message=XHubSignatureTestVector.body + ' ',
                ),
            )

    def test_hmac_vector(self):
        # Note: We verify this private method because we want to bypass
        # the time-invariant comparison layer (and we don't want to
        # mock here):
        sig = 'sha1=' + self.sigver._calculate_hmacsha1(
            XHubSignatureTestVector.body
        )
        self.assertEqual(XHubSignatureTestVector.expectedsig, sig)


# I did not find test vectors for the X-HUB-SIGNATURE algorithm, so I
# made this one by hand:
class XHubSignatureTestVector (object):
    # This is just a "namespace class", not to be instantiated.

    sharedsecret = 'abc'

    body = (
        '{"zen":"Keep it logically awesome.","hook":{"url":"https://' +
        'api.github.com/repos/nejucomo/leastbot/hooks/2483695","test' +
        '_url":"https://api.github.com/repos/nejucomo/leastbot/hooks' +
        '/2483695/test","id":2483695,"name":"web","active":true,"eve' +
        'nts":["*"],"config":{"secret":"abc","url":"http://con.struc' +
        '.tv:12388/foo","content_type":"json","insecure_ssl":"0"},"l' +
        'ast_response":{"code":null,"status":"unused","message":null' +
        '},"updated_at":"2014-06-26T00:34:21Z","created_at":"2014-06' +
        '-26T00:34:21Z"},"hook_id":2483695}'
    )

    expectedsig = 'sha1=91bc104310ed46d5633a249e0240dd98a37435cf'
