from fabric.api import local

DB_NAME = "golfstats"


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


def test(app=None):
    args = _get_args()

    if app:
        args.append(app)

    res = local(" ".join(args), False)

    if res.return_code == 0:
        flake8()


def smalltest():
    args = _get_args()
    args.append("--attr=smalltest")

    local(" ".join(args), False)


def coverage():
    args = _get_args() + [
        '--with-coverage',
        '--cover-package=smac',
    ]
    local(" ".join(args), False)


def flake8():
    local("find . -name '*.py' -exec flake8 {} \;", False)


def dropdb():
    sql_statements = [
        "DROP DATABASE IF EXISTS %s" % (DB_NAME),
        "CREATE DATABASE %s CHARSET utf8" % (DB_NAME),
    ]
    local('mysql -e"%s"' % ("; ".join(sql_statements)), False)


def syncdb():
    local("python manage.py syncdb --noinput", False)


def freshdb():
    dropdb()
    syncdb()
