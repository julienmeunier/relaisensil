#!/usr/bin/python
# encoding: utf-8

import os, sys
import traceback
"""
deploy.cgi: Script to deploy Django website on the web hosting solution

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
try:
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

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "engine.settings.production")
    print("Content-type: text/html\n\n")
    from django.core.management import call_command
    call_command('syncdb', interactive=False)
    call_command('collectstatic', interactive=False)
except Exception, inst:
    print("Content-type: text/html\n\n")
    print(inst)
    print(traceback.format_exc())
