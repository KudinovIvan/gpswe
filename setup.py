#!/user/bin/env python

from io import open
from setuptools import setup

"""

:authors: Ivan Kudinov
:license: see LICENSE file
:copyright: (c) 2023 Ivan Kudinov
"""

version = "0.0.1"

long_description = '''Python library for parse, save and work 
                    with Wialon and EGTS data'''

setup(
    name="gpswe",
    version=version,

    author="Ivan Kudinov",
    author_email="marvel.2012@mail.ru",

    description=(
        u'Python library for parse, save and work ' 
        u'with Wialon and EGTS data'
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",

    url="https://"
)