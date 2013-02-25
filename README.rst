Daemon Skeleton
================

Daemon Skeleton is a template for building  project with daemon fast.

Quick start
-----------

Follow next guide to setup your development environment.

- Clone the git repo::

    git clone https://github.com/mlf4aiur/daemon-skeleton.git

- Use virtualenv to create isolated Python environments::

    sudo pip install virtualenv
    virtualenv .venv
    . .venv/bin/activate
    pip install -r requirements.txt
    rm -rf .git

Benefits
--------

- Create your own requirements.txt::

    pip freeze | awk -F = '{print $1}' > requirements.txt

- Upgrade packages to latest version::

    pip install -U -r requirements.txt

- Testing code::

    # nose
    nosetests
    # Fabric
    fab test
    # setuptools
    python setup.py test

- create a new source distribution as tarball::

    python setup.py sdist --formats=gztar
    # Fabric
    fab pack

- Deploying your code::

    fab pack deploy

Credits
-------

This python daemon library is a fork of the `python-daemon <https://github.com/serverdensity/python-daemon>`_.
