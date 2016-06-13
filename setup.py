import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

requires = [
    'requests',
    'thriftpy',
    'thriftpywrap',
    'xylose'
]

test_requires = []

setup(
    name='bibliometrics',
    version='0.1.0',
    description='Thrift RPC Channel and RESTFul API to retrieve bibliometric indicators',
    author='SciELO',
    author_email='scielo-dev@googlegroups.com',
    url='http://docs.scielo.org/projects/bibliometrics/en/latest/',
    packages=['bibliometrics'],
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Operating System :: POSIX :: Linux",
        "Topic :: System",
        "Topic :: Utilities",
    ],
    dependency_links=[
        "git+https://github.com/scieloorg/xylose@1.3.4#egg=xylose",
        "git+https://github.com/scieloorg/thriftpy-wrap@0.1.1#egg=thriftpywrap"
    ],
    license='BSD 2-Clause',
    keywords='SciELO Bibliometrics, RESTFul API and Thrift RPC Layer',
    include_package_data=True,
    zip_safe=False,
    setup_requires=["nose>=1.0", "coverage"],
    install_requires=requires,
    tests_require=test_requires,
    test_suite="nose.collector",
    entry_points="""\
    [console_scripts]
    bibliometrics_thriftserver = bibliometrics.thrift.server:main
    bibliometrics_load_data = processing.loaddata:main
    """,
)
