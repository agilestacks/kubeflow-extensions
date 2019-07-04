import setuptools

try: # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError: # for pip <= 9.0.3
    from pip.req import parse_requirements

# from distutils.core import setup
# from setuptools import setup, find_packages
from os import path
from io import open


_version_major = 0
_version_minor = 0
_version_micro = 1

# Construct full version string from these.
_ver = [_version_major, _version_minor]
if _version_micro:
    _ver.append(_version_micro)

__version__ = '.'.join(map(str, _ver))

long_description = 'a very long description'

# with open('./README.rst') as f:
#     long_description = f.read()

cwd = path.abspath(path.dirname(__file__))
req_path = path.join(cwd, 'requirements.txt')

reqs = [ir for ir in parse_requirements(req_path, session=False)]
install_requires = [str(r.req) for r in reqs if r.req != None]
dependency_links = [str(r.link) for r in reqs if r.req != None]

kwargs = {
    'name': 'extensions',
    'description': "IPython notebook extensions specific to current application",
    'long_description': long_description,
    'author': 'Antons Kranga',
    'author_email': 'anton@agilestacks.com',
    'py_modules': ['extensions'],
    'packages': setuptools.find_packages(),
    'version': __version__,
    'license': 'Agile Stacks',
    'url': 'http://agilestacks.com',
    'download_url': 'http://controlplane.agilestacks.io',
    'classifiers': [
        'Topic :: Utilities',
        'Framework :: IPython',
        'Intended Audience :: Developers',
        'Topic :: Desktop Environment :: File Managers',
    ],
    'keywords': ['PYTHONPATH', 'utility', 'IPython'],
    'install_requires': install_requires,
    'dependency_links': dependency_links,
    # 'entry_points': {'console_scripts': ['pypath = extensions.cli:main']},
}

# setup(
#     name='agilestacks',
#     version=__version__,
#     author='Antons Kranga',
#     author_email='anton@agilestacks.com',
#     py_modules=['ipython_pytest'],
#     url='https://github.com/akaihola/ipython_pytest',
#     classifiers=["Programming Language :: Python",
#                  "Topic :: Scientific/Engineering"],
#     license='README.md',
#     description='Collection of Jupyter Notebook extensions to encapsulate engineering effort',
#     long_description=long_description,
# )

if __name__ == '__main__':
    setuptools.setup(**kwargs)
