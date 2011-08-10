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

    if res.return_code == 0:
        flake8()


def coverage():
    args = _get_args() + [
        '--with-coverage',
        '--cover-package=smac',
    ]
    local(" ".join(args), False)


def flake8():
    local("find . -name '*.py' -exec flake8 {} \;", False)
