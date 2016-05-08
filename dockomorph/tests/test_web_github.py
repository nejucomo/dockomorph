import json

from twisted.trial import unittest
from twisted.web.server import NOT_DONE_YET
from mock import call

from dockomorph.tests.logutil import LogMockingTestCase, ArgIsLogRecord
from dockomorph.web import github


class WebhookResourceTests (LogMockingTestCase):
    secret = 'fake secret'

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

        self.pingbody = json.dumps(self.pingmessage)
        sigver = github.SignatureVerifier(self.secret)
        self.pingexpsig = sigver._calculate_hmacsha1(self.pingbody)

        self.m_handle_event = self.make_mock()
        self.m_request = self.make_mock()
        self.m_request.content.getvalue.return_value = self.pingbody

        headers = {
            'X-Github-Event': 'ping',
            'X-Github-Delivery': 'a fake unique id',
            'X-Hub-Signature': 'sha1=' + self.pingexpsig,
            }
        self.m_request.getHeader.side_effect = headers.get

        self.res = github.WebhookResource(self.secret, self.m_handle_event)

    def test_isLeaf_resource(self):
        self.assertEqual(True, github.WebhookResource.isLeaf)

    def test_render_GET(self):
        r = self.res.render_GET(self.m_request)

        self.assertEqual(NOT_DONE_YET, r)
        self.assert_calls_equal(
            self.m_handle_event,
            [])

        self.assert_calls_equal(
            self.m_request,
            [call.setResponseCode(403, 'FORBIDDEN'),
             call.finish()])

    def test_render_POST_ping(self):
        r = self.res.render_POST(self.m_request)

        self.assertEqual(NOT_DONE_YET, r)
        self.assert_calls_equal(
            self.m_request,
            [call.getHeader('X-Hub-Signature'),
             call.content.getvalue(),
             call.getHeader('X-Github-Event'),
             call.getHeader('X-Github-Delivery'),
             call.setResponseCode(200, 'OK'),
             call.finish()])

        self.assert_calls_equal(
            self.m_handle_event,
            [call('a fake unique id', 'ping', self.pingmessage)])

        self.assert_calls_equal(
            self.m_loghandler,
            [call.handle(ArgIsLogRecord(levelname='DEBUG', msg='__init__'))])

    def test_render_POST_ping_tampered(self):
        self.reset_mocks()

        tweakedmessage = self.pingmessage.copy()
        tweakedmessage['hook_id'] += 1

        self.m_request.content.getvalue.return_value = \
            json.dumps(tweakedmessage)

        r = self.res.render_POST(self.m_request)

        self.assertEqual(NOT_DONE_YET, r)
        self.assert_calls_equal(
            self.m_request,
            [call.getHeader('X-Hub-Signature'),
             call.content.getvalue(),
             call.setResponseCode(403, 'FORBIDDEN'),
             call.finish()])

        self.assert_calls_equal(
            self.m_loghandler,
            [call.handle(ArgIsLogRecord(levelname='WARNING'))])


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
