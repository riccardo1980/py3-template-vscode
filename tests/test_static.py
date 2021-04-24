import pathlib
import pytest
from cookiecutter.main import cookiecutter

TEMPLATE_DIRECTORY = str(pathlib.Path(__file__).parent.parent)


@pytest.fixture()
def create_cookie(scope='module'):
    """
        cookiecutter run
    """

    cookiedir = 'TESTDIR'
    # cookiedir = str(tmpdir_factory.mktemp('cookie'))
    cookiecutter(
        template=TEMPLATE_DIRECTORY,
        output_dir=cookiedir,
        no_input=True,
    )

    yield cookiedir


def test_folder_structure(create_cookie):
    """
        project structure
    """
    pass


def test_venv_valid(create_cookie):
    """
    """
    pass


def test_venv_ignored_in_linter(create_cookie):
    """
        virtualenv in flake8 file
    """
    pass


def test_venv_ignored_in_git(create_cookie):
    """
        virtualenv in .gitignore file
    """
    pass
