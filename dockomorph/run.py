from twisted.internet import utils

from dockomorph.reactive import ReactiveMixin
from dockomorph.templex import TemplatizedException


class ProcessErrorExit (TemplatizedException):
    Template = 'exit {exittype!s} {exitval!r}'


class ShellExecutorMixin (ReactiveMixin):
    def run(self, executable, args=(), env={}, path=None):
        """
        Like ``ShellExecutorMixin.run_catch``, except:

        1. If the process exit status is non-0, or the process exited
           due to a signal, then propagate a Failure.
        2. Otherwise, the deferred is fired with (out, err)
        """
        d = self.run_catch(executable, args, env, path)

        @d.addCallback
        def handle_results((out, err, exittype, exitval)):
            if (exittype, exitval) == ('code', 0):
                return (out, err)
            else:
                raise ProcessErrorExit(
                    exittype=exittype,
                    exitval=exitval,
                    stdout=out,
                    stderr=err,
                )

        return d

    def run_catch(self, executable, args=(), env={}, path=None):
        self._log.info(
            'Running %r %r env %r in %r.',
            executable,
            args,
            env,
            path,
        )

        d = utils.getProcessOutputAndValue(
            executable,
            args,
            env,
            path,
            self._reactor,
            errortoo=True,
        )

        d.addCallbacks(
            callback=lambda (out, err, signal): (out, err, 'signal', signal),
            errback=lambda (out, err, code): (out, err, 'code', code),
            )

        @d.addCallback
        def log_results((out, err, exittype, exitval)):
            self._log.info(
                '\n'.join([
                    'Command %r completed:',
                    '=== stdout ==='
                    '%s'
                    '=== stderr ==='
                    '%s'
                    '=== exit %s %r ===',
                ]),
                executable,
                out,
                err,
                exittype,
                exitval,
            )
            return (out, err, exittype, exitval)

        return d
