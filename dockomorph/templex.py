class TemplatizedException (Exception):
    def __init__(self, **params):
        self.text = self.Template.format(**params)
        Exception.__init__(self, params)

    def __str__(self):
        return '{}: {}'.format(type(self).__name__, self.text)
