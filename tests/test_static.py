import json
import os
import pathlib
from typing import Any, Dict, List

import pytest
from cookiecutter.main import cookiecutter

TEMPLATE_DIRECTORY = str(pathlib.Path(__file__).parent.parent)
GITIGNORE = ".gitignore"


@pytest.fixture(scope="session")
def default_values() -> Any:
    with open("cookiecutter.json") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def create_cookie(tmpdir_factory: Any) -> str:
    """
    cookiecutter run
    """

    cookiedir = str(tmpdir_factory.mktemp("cookie"))
    cookiecutter(
        template=TEMPLATE_DIRECTORY,
        output_dir=cookiedir,
        no_input=True,
    )

    return cookiedir


@pytest.fixture(scope="session")
def content_list(create_cookie: str) -> List[str]:
    def remove_cookie_dir(text: str, prefix: str) -> str:
        out = text
        if text.startswith(prefix):
            out = text[len(prefix) :]
        return out

    content = []
    for dirpath, dirnames, filenames in os.walk(
        create_cookie, topdown=False, followlinks=True
    ):
        for name in filenames:
            fullname = os.path.join(dirpath, name)
            content.append(fullname)
        for name in dirnames:
            fullname = os.path.join(dirpath, name)
            content.append(fullname)

    # remove leading cookie_dir
    cookie_dir = os.path.join(create_cookie, "")
    content = [f for f in map(lambda x: remove_cookie_dir(x, cookie_dir), content)]

    return content


def test_default_root_folder(
    content_list: List[str], default_values: Dict[str, Any]
) -> None:
    assert default_values["project_slug"] in content_list


def test_default_package_folder(
    content_list: List[str], default_values: Dict[str, Any]
) -> None:
    assert (
        os.path.join(default_values["project_slug"], default_values["package_name"])
        in content_list
    )


def test_default_pip_in_venv_folder(
    content_list: List[str], default_values: Dict[str, Any]
) -> None:
    interpreters = [
        os.path.join(
            default_values["project_slug"],
            default_values["virtualenv_name"],
            "bin",
            ii,
        )
        for ii in ["pip", "pip3"]
    ]

    for item in interpreters:
        assert item in content_list


def test_default_interpreter_in_venv_folder(
    content_list: List[str], default_values: Dict[str, Any]
) -> None:
    interpreters = [
        os.path.join(
            default_values["project_slug"],
            default_values["virtualenv_name"],
            "bin",
            ii,
        )
        for ii in ["python", "python3"]
    ]

    for item in interpreters:
        assert item in content_list


def test_default_test_tools_in_venv_folder(
    content_list: List[str], default_values: Dict[str, Any]
) -> None:
    interpreters = [
        os.path.join(
            default_values["project_slug"],
            default_values["virtualenv_name"],
            "bin",
            ii,
        )
        for ii in ["pytest"]
    ]

    for item in interpreters:
        assert item in content_list


# LINTER_CONFIG = '.flake8'
# def test_venv_ignored_in_linter(create_cookie, default_values):
#     config = configparser.ConfigParser()
#     config.read(os.path.join(create_cookie,
#                              default_values['project_slug'],
#                              LINTER_CONFIG))

#     assert default_values['virtualenv_name'] in config['flake8']['exclude']


def test_venv_ignored_in_gitignore(
    create_cookie: str, default_values: Dict[str, Any]
) -> None:
    with open(
        os.path.join(create_cookie, default_values["project_slug"], GITIGNORE)
    ) as f:
        lines = f.read().split("\n")
    assert default_values["virtualenv_name"] in lines
