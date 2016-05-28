from twisted.python import filepath


StateDir = filepath.FilePath('/var/lib/dockomorph')
GitsDir = StateDir.child('gits')
GitExec = filepath.FilePath('git')  # FIXME: Make this absolute
