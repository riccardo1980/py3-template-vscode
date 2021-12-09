from {{cookiecutter.package_name}} import base


def test_base() -> int:
    return 0


def test_run() -> None:
    assert base.runme() == 1
