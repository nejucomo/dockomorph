from dockomorph import paths
from dockomorph.run import ShellExecutorMixin, ProcessErrorExit
from dockomorph.templex import TemplatizedException


class AuthorizationFailure (TemplatizedException):
    pass


class InvalidSignature (AuthorizationFailure):
    Template = '{details!s}'


class UnknownSigner (AuthorizationFailure):
    Template = 'signer id {signerid!r}; known ids: {authset!r}'


class UnknownAuthorizationFailure (AuthorizationFailure):
    Template = 'GPG output: {gpgoutput!s}'


class GitGpgAuthorizer (ShellExecutorMixin):
    """I take an authset and can verify git tag signatures against it."""

    def __init__(self, reactor, authset):
        """authset is a set of GPG fingerprints."""
        ShellExecutorMixin.__init__(self, reactor)
        self._authset = authset

    def check_tag_signature(self, repodir, tag):
        d = self.run_catch(
            paths.GitExec,
            ['verify-tag', '--raw', tag],
            path=repodir,
        )

        @d.addErrback
        def handle_verification_failure(f):
            if f.check(ProcessErrorExit):
                raise InvalidSignature(str(f.value))
            else:
                # Something else we don't understand:
                return f

        @d.addCallback
        def handle_verify_output(verifyoutput):
            """
            Find the fingerprint suffix of the raw tag signature
            verification output, then ensure it's in the authorized list.

            An example output line prefix with a signature is:

            [GNUPG:] GOODSIG 26EA3D7EBE0C9FC2 ...
            """
            for line in verifyoutput.splitlines():
                if line.startswith('[GNUPG:] GOODSIG '):
                    [_, _, fpsuffix, _] = line.split(' ', 3)
                    if fpsuffix in self._authset:
                        self._log.info(
                            'Authorized signature: %s',
                            line.strip(),
                        )
                        return None
                    else:
                        raise UnknownSigner(
                            signerid=fpsuffix,
                            authset=self._authset,
                        )

            raise UnknownAuthorizationFailure(gpgoutput=verifyoutput)

        return d
