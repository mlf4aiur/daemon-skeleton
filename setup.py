import os
from setuptools import find_packages, setup

version = '0.9.0'
here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

install_requires = [
    # List your project dependencies here.
    # For more details, see:
    # http://packages.python.org/distribute/setuptools.html#declaring-dependencies
    'Fabric',
    'nose'
]


setup(
    name='daemon_skeleton',
    version=version,
    author='Kevin Lee',
    author_email='mlf4aiur@gmail.com',
    description='A template for building a daemon tool fast.',
    long_description=README,
    license="BSD License",
    keywords="daemon",
    install_requires=install_requires,
    packages=find_packages('daemon_skeleton'),
    package_dir={'': 'daemon_skeleton'},
    include_package_data=True,
    zip_safe=False,
    test_suite="daemon_skeleton.tests",
    platforms='any'
)
