import nox

@nox.session
def lint(session):
    session.install('ruff')
    session.run('ruff', 'check', '.')

@nox.session
def tests(session):
    session.install('-r', 'requirements.txt')
    session.install('pytest')
    session.run('pytest', '-q', '-m', 'not slow and not production')

@nox.session
def types(session):
    session.install('mypy')
    session.run('mypy', 'src/reactor', 'scripts', 'tests')
