
# adapted from http://flask.pocoo.org/snippets/65/

class Middleware(object):
    """
      Create a callable object that will update the environment SCRIPT_NAME to
      the URL that the app was installed on, if that URL is not '/'
    """
    def __init__(self, app):
        self.app = app
    def __call__(self, environ, start_response):
        app_url = '@APP_URL@'

        if app_url != '/':
            environ['SCRIPT_NAME'] = app_url
        return self.app(environ, start_response)

