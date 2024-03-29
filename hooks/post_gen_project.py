from __future__ import annotations

import copy
import json
import os
import shutil
import subprocess
import sys
import venv
from pathlib import Path
from typing import Any, Dict, List, Type, TypeVar


def str2bool(var: str) -> bool:
    """
    String to Boolean

    :param var: input string
    """
    return var.lower() in ("yes", "true", "si", "y", "s", "1")


class ExtendedEnvBuilder(venv.EnvBuilder):
    """
    EnvBuilder with dependence installation

    from: https://github.com/LP-CDF/AMi_Image_Analysis/blob/master/Setup.py
    """

    def __init__(self, *args: Any, **kwargs: Any):
        """
        Initialization

        :param requirements_files: list of file names [default: ['requirements.txt']]
        :param upgrade_pip: whether to upgrade pip [default: True]
        :param ipython_support: whether to add ipython support [default: False]
        """
        self.requirements_files = kwargs.pop("requirements_files", ["requirements.txt"])
        self.upgrade_pip = kwargs.pop("upgrade_pip", True)
        self.ipython_support = kwargs.pop("ipython_support", False)
        super().__init__(*args, **kwargs)

    def post_setup(self, context: Any) -> None:
        """
        Set up any packages which need to be pre-installed into the
        virtual environment being created.
        :param context: The information for the virtual environment
                        creation request being processed.
        """
        os.environ["VIRTUAL_ENV"] = context.env_dir

        self.install_dep(context)

    def install_dep(self, context: Any) -> None:
        """
        Install requred dependencies
        :param context: The information for the virtual environment
                        creation request being processed.
        """

        binpath = Path(context.bin_path).joinpath("python3")
        ipythonpath = Path(context.bin_path).joinpath("ipython")
        # print("PYTHONPATH: ", binpath)
        # print('WILL INSTALL packages from: ', self.requirements_files)

        # upgrade pip
        if self.upgrade_pip:
            subprocess.check_call(
                [
                    binpath,
                    "-m",
                    "pip",
                    "install",
                    "--prefix",
                    context.env_dir,
                    "--upgrade",
                    "pip",
                ]
            )

        for req in self.requirements_files:
            subprocess.check_call(
                [
                    binpath,
                    "-m",
                    "pip",
                    "install",
                    "--prefix",
                    context.env_dir,
                    "-r",
                    req,
                ]
            )

        if self.ipython_support:
            subprocess.check_call([binpath, "-m", "pip", "install", "notebook"])
            subprocess.check_call(
                [
                    ipythonpath,
                    "kernel",
                    "install",
                    "--user",
                    "--name=" + context.env_name,
                ]
            )


def venv_create(venv_home: str, **kwargs: Any) -> None:
    """
    Create requested virtualenv
    """
    builder = ExtendedEnvBuilder(with_pip=True, **kwargs)
    builder.create(venv_home)


def gitignore_config(gitignore_template: str, ignore_list: List[str]) -> None:
    """
    Configure gitignore file

    :param gitignore_template: filename for gitignore template
    :param ignore_list: list of gitignore entries

    """
    gitignore_file = ".gitignore"

    os.rename(gitignore_template, gitignore_file)

    # ignore list to .gitignore
    with open(gitignore_file, "a") as fd:
        for item in ignore_list:
            fd.write("{}\n".format(item))


class ToolConfig:
    """
    Info on tool configuration
    """

    def __init__(self) -> None:

        # path to list of config files
        self.tool_config_files: List[str] = []

        # path to file containing requirements (requirements.txt style)
        self.requirements: List[str] = []

        # dict containing tool settings
        self.vscode_settings: Dict[str, Any] = {}

    _T = TypeVar("_T", bound="ToolConfig")

    @classmethod
    def from_folder(cls: Type[_T], config_folder: str) -> _T:
        """
        Create configuration object from folder

        :param config_folder: configuration folder
        :return: configuration object

        Configuration folder must contain:
        - config_files folder: only first level files are considered
        - requirements.txt: list of requirements, adhering requirements.txt style
        - vscode_settings.json: json with configuration, .vscode/settings.json style
        """
        config = cls()

        config_files_folder = os.path.join(config_folder, "config_files")
        if os.path.isdir(config_files_folder):
            config.tool_config_files = [
                os.path.join(config_folder, "config_files", item.name)
                for item in os.scandir(os.path.join(config_folder, "config_files"))
                if item.is_file()
            ]

        with open(os.path.join(config_folder, "requirements.txt"), "r") as f:
            config.requirements.extend(f.read().split())

        try:

            vscode_settings_file = os.path.join(config_folder, "vscode_settings.json")
            with open(vscode_settings_file, "r") as f:
                config.vscode_settings = json.load(f)

        except json.JSONDecodeError:
            if os.path.getsize(vscode_settings_file) != 0:
                raise

        return config

    def __add__(self, other: ToolConfig) -> ToolConfig:
        """
        Add two configuration objects

        :param other: other configuration object
        :return: a new configuration object with merged results
        """
        new_cfg = ToolConfig()
        new_cfg = copy.deepcopy(self)
        new_cfg += other
        return new_cfg

    def __iadd__(self, other: ToolConfig) -> ToolConfig:
        """
        In place merge of configuration objects

        :param other: other configuration object
        :return: updated object with merged results
        """
        self.tool_config_files.extend(other.tool_config_files)
        self.requirements.extend(other.requirements)
        self.vscode_settings = {**self.vscode_settings, **other.vscode_settings}
        return self

    def __repr__(self) -> str:

        out = "\n\ntool_config_files:\n"
        out += self.tool_config_files.__repr__()
        out += "\n\nrequirements:\n"
        out += self.requirements.__repr__()
        out += "\n\nvscode_settings:\n"
        out += self.vscode_settings.__repr__()

        return out


def do_post_hook() -> None:

    gitignore_template = ".gitignore.template"
    vscode_settings_file = ".vscode/settings.json"
    tools_config_folder = "tools_configs"

    # Jinja values
    virtualenv_name = "{{cookiecutter.virtualenv_name}}"
    do_upgrade_pip = str2bool("{{cookiecutter.upgrade_pip}}")
    do_support_ipython = str2bool("{{cookiecutter.ipython_support}}")

    print("{}: running post-gen hook".format(__name__))
    # initialize base configuration
    master_cfg = ToolConfig()
    with open(vscode_settings_file, "r") as f:
        master_cfg.vscode_settings = json.load(f)

    print("{}: configuration".format(__name__))
    print("{}:{}".format(__name__, master_cfg))

    try:
        # CONFIGURATION FILES
        for item in master_cfg.tool_config_files:
            shutil.copy2(item, "./")

        # PREREQUISITES SETUP
        with open("requirements-test.txt", "a") as fd:
            fd.write("\n".join(master_cfg.requirements))

        # VIRTUALENV
        print("{}: create virtualenv".format(__name__))
        venv_create(
            venv_home=virtualenv_name,
            requirements_files=["requirements.txt", "requirements-test.txt"],
            upgrade_pip=do_upgrade_pip,
            ipython_support=do_support_ipython,
        )

        # GITIGNORE
        print("{}: configure gitignore".format(__name__))
        gitignore_config(gitignore_template, [virtualenv_name])

        # VSCODE CONFIGURATION
        print("{}: configure vscode".format(__name__))
        with open(vscode_settings_file, "w") as f:
            json.dump(master_cfg.vscode_settings, f, indent=4)

    except Exception as e:
        print("{}: exception caught\nexiting\n{}".format(__name__, e))
        sys.exit(-1)

    # CLEANUP
    # remove templates
    print("{}: cleanup".format(__name__))
    shutil.rmtree(tools_config_folder)


do_post_hook()
