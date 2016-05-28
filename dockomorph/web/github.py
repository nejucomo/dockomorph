import json
import hmac
import hashlib

from twisted.web import resource
from twisted.web.server import NOT_DONE_YET

from dockomorph.reactive import ReactiveMixin


class WebhookResource (ReactiveMixin, resource.Resource):
    isLeaf = True

    def __init__(self, reactor, sharedsecret, handle_push_tag):
        resource.Resource.__init__(self)
        ReactiveMixin.__init__(self, reactor)

        self._verify_signature = SignatureVerifier(sharedsecret)
        self._handle_push_tag = handle_push_tag

    def render_GET(self, request):
        request.setResponseCode(403, 'FORBIDDEN')
        request.finish()
        return NOT_DONE_YET

    def render_POST(self, request):
        allegedsig = request.getHeader('X-Hub-Signature')
        body = request.content.getvalue()

        if self._verify_signature(allegedsig, body):
            self._handle_signed_message(request, body)
        else:
            self._log.warn(
                'render_POST 403: signature mismatch - allegedsig %r; body %r',
                allegedsig,
                body)
            request.setResponseCode(403, 'FORBIDDEN')
        request.finish()
        return NOT_DONE_YET

    def _handle_signed_message(self, request, body):
        try:
            message = json.loads(body)
        except ValueError:
            self._log.error(
                "Received a signature-verified malformed JSON POST. " +
                "There may be a bug in our signature verification, " +
                "the standard python JSON parser, or github's emitter. "
            )
            request.setResponseCode(400, 'MALFORMED')
        else:
            eventname = request.getHeader('X-Github-Event')
            eventid = request.getHeader('X-Github-Delivery')
            if self._handle_bare_event(eventid, eventname, message):
                request.setResponseCode(200, 'OK')
            else:
                request.setResponseCode(400, 'Event Not Supported')

    def _handle_bare_event(self, eventid, eventname, message):
        if eventname == 'ping':
            return True
        elif eventname == 'push':
            # There's no ability for the app logic to affect the HTTP
            # response now, so put off further processing into a later
            # reactor turn:
            self._reactor.callLater(0, self._handle_push_event, message)
            return True
        else:
            self._log.info(
                'Unhandled github %r event %r.',
                eventname,
                eventid,
            )
            return False

    def _handle_push_event(self, message):
        ref = message['ref']
        if not ref.startswith('refs/tags/dockomorph.'):
            self._log.debug('Ignoring non-dockomorph tag push to %r', ref)
            return

        tag = ref[len('refs/tags/'):]

        repo = message['repository']
        reponame = repo['name']
        repourl = repo['clone_url']

        self._handle_push_tag(reponame, repourl, tag)


class SignatureVerifier (object):
    def __init__(self, sharedsecret):
        self._sharedsecret = sharedsecret

    def __call__(self, allegedsig, message):
        expectedsig = 'sha1=' + self._calculate_hmacsha1(message)
        return constant_time_compare(allegedsig, expectedsig)

    def _calculate_hmacsha1(self, body):
        m = hmac.HMAC(key=self._sharedsecret, msg=body, digestmod=hashlib.sha1)
        return m.hexdigest()


def constant_time_compare(a, b):
    # Use Nate Lawson's constant time compare:
    # http://rdist.root.org/2010/01/07/timing-independent-array-comparison/

    if len(a) != len(b):
        return False

    result = 0
    for (x, y) in zip(a, b):
        result |= ord(x) ^ ord(y)
    return result == 0
