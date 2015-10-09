#!/usr/bin/python
# encoding: utf-8
import os, sys
import traceback
from cookielib import debug
"""
django.cgi: Entrypoint for the Django production website

Copyright (c) 2015 - Lab A Part
Olivier <olivier@labapart.com>
Julien Meunier <julien.meunier.perso@gmail.com>

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
"""

# Set on True to enable traceback
DEBUG = False

STATIC_PATH = os.path.dirname(os.path.abspath(__file__))
WWW_PATH = STATIC_PATH
HOME_PATH = os.path.dirname(WWW_PATH)
PYTHON_PATH = os.path.join(HOME_PATH, 'lib')
DJANGO_PATH = os.path.join(HOME_PATH, 'django')

sys.path.append(PYTHON_PATH)
sys.path.append(os.path.join(PYTHON_PATH, "colorama-0.3.5"))
sys.path.append(os.path.join(PYTHON_PATH, "Django-1.6"))
sys.path.append(os.path.join(PYTHON_PATH, "django-paypal-0.2.7"))
sys.path.append(os.path.join(PYTHON_PATH, "django-simple-captcha-0.5.1"))
sys.path.append(os.path.join(PYTHON_PATH, "django_sendmail_backend"))
sys.path.append(os.path.join(PYTHON_PATH, "gitdb-0.6.4"))
sys.path.append(os.path.join(PYTHON_PATH, "GitPython-1.0.1"))
sys.path.append(os.path.join(PYTHON_PATH, "httplib2-0.9.2"))
sys.path.append(os.path.join(PYTHON_PATH, "keyring-5.7.1"))
sys.path.append(os.path.join(PYTHON_PATH, "Pillow-3.0.0"))
sys.path.append(os.path.join(PYTHON_PATH, "pyftpsync-1.0.3"))
sys.path.append(os.path.join(PYTHON_PATH, "pytz-2015.7"))
sys.path.append(os.path.join(PYTHON_PATH, "requests-2.9.0"))
sys.path.append(os.path.join(PYTHON_PATH, "setuptools-18.8.1"))
sys.path.append(os.path.join(PYTHON_PATH, "six-1.10.0"))
sys.path.append(os.path.join(PYTHON_PATH, "smmap-0.9.0"))
sys.path.append(os.path.join(PYTHON_PATH, "South-1.0.2"))
sys.path.append(DJANGO_PATH)
sys.path.append(os.path.join(DJANGO_PATH, "engine"))
sys.path.append(os.path.join(DJANGO_PATH, "relais"))

def run_with_cgi(application):
    environ = dict(os.environ.items())
    environ['wsgi.input'] = sys.stdin
    environ['wsgi.errors'] = sys.stderr
    environ['wsgi.version'] = (1, 0)
    environ['wsgi.multithread'] = False
    environ['wsgi.multiprocess'] = True
    environ['wsgi.run_once'] = True

    if environ.get('HTTPS', 'off') in ('on', '1'):
        environ['wsgi.url_scheme'] = 'https'
    else:
        environ['wsgi.url_scheme'] = 'http'

    headers_set = []
    headers_sent = []

    def write(data):
        if not headers_set:
            raise AssertionError("write() before start_response()")
        elif not headers_sent:
            # Before the first output, send the stored headers
            status, response_headers = headers_sent[:] = headers_set
            sys.stdout.write('Status: %s\r\n' % status)
            for header in response_headers:
                sys.stdout.write('%s: %s\r\n' % header)
            sys.stdout.write('\r\n')

        sys.stdout.write(data)
        sys.stdout.flush()

    def start_response(status, response_headers, exc_info=None):
        if exc_info:
            try:
                if headers_sent:
                    # Re-raise original exception if headers sent
                    raise exc_info[0], exc_info[1], exc_info[2]
            finally:
                exc_info = None     # avoid dangling circular ref
        elif headers_set:
            raise AssertionError("Headers already set!")

        headers_set[:] = [status, response_headers]
        return write

    result = application(environ, start_response)
    try:
        for data in result:
            if data:    # don't send headers until body appears
                write(data)
        if not headers_sent:
            write('')   # send headers now if body was empty
    finally:
        if hasattr(result, 'close'):
            result.close()
try:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "engine.settings.production")
    import django.core.handlers.wsgi
    run_with_cgi(django.core.handlers.wsgi.WSGIHandler())
except Exception, inst:
    print("Content-type: text/html\n\n")
    if DEBUG:
        print(inst)
        print(sys.path)
        print(traceback.format_exc())
    else:
        print('Internal server error. Please contact webmaster@relais.com')
