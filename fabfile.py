#! /usr/bin/env python

from fabric.api import local


def _get_args():
    return [
        'python',
        'manage.py',
        'test',
        #'-v 2'
        #'--noinput',
        '--nocapture',
        #'--with-xunit',

        #'--pdb',
        #'--pdb-failures',

        '--failfast',
    ]


def test():
    args = _get_args()
    res = local(" ".join(args), False)

    # Requires higher version of fabric then
    # is carried in Debian Squeeze
    #if res.succeeded:
    #    flake8()


def coverage():
    args = _get_args() + [
        '--with-coverage',
        '--cover-package=smac',
    ]
    local(" ".join(args), False)


def flake8():
    local("find . -name '*.py' -exec flake8 {} \;", False)
