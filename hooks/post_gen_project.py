import os
import json
import sys
import subprocess
import shutil
import venv
import copy
from typing import List, Type, TypeVar
from pathlib import Path

def str2bool(var: str):
    """
    String to Boolean

    :param var: input string
    """
    return var.lower() in ("yes", 'true', 'si', 'y', 's', '1')


class ExtendedEnvBuilder(venv.EnvBuilder):
    """
    EnvBuilder with dependence installation

    from: https://github.com/LP-CDF/AMi_Image_Analysis/blob/master/Setup.py
    """
    def __init__(self, *args, **kwargs):
        """
        Initialization

        :param requirements_files: list of file names [default: ['requirements.txt']]
        :param upgrade_pip: whether to upgrade pip [default: True]
        :param ipython_support: whether to add ipython support [default: False]
        """
        self.requirements_files = kwargs.pop('requirements_files',
                                             ['requirements.txt'])
        self.upgrade_pip = kwargs.pop('upgrade_pip', True)
        self.ipython_support = kwargs.pop('ipython_support', False)
        super().__init__(*args, **kwargs)

    def post_setup(self, context):
        """
        Set up any packages which need to be pre-installed into the
        virtual environment being created.
        :param context: The information for the virtual environment
                        creation request being processed.
        """
        os.environ['VIRTUAL_ENV'] = context.env_dir

        self.install_dep(context)

    def install_dep(self, context):
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
                [binpath, '-m', 'pip', 'install', "--prefix",
                    context.env_dir, '--upgrade', 'pip']
            )

        for req in self.requirements_files:
            subprocess.check_call(
                [binpath, '-m', 'pip', 'install', "--prefix",
                 context.env_dir, '-r', req]
            )

        if self.ipython_support:
            subprocess.check_call(
                [binpath, '-m', 'pip', 'install', 'notebook']
            )
            subprocess.check_call(
                [ipythonpath, 'kernel', 'install',
                '--user', '--name='+context.env_name]
            )


def venv_create(venv_home: str, **kwargs):
    """
    Create requested virtualenv
    """
    builder = ExtendedEnvBuilder(with_pip=True, **kwargs)
    builder.create(venv_home)


def gitignore_config(gitignore_template: str,
                     ignore_list: List[str]):
    """
    Configure gitignore file

    :param gitignore_template: filename for gitignore template
    :param ignore_list: list of gitignore entries

    """
    gitignore_file = '.gitignore'

    os.rename(gitignore_template,
              gitignore_file)

    # ignore list to .gitignore
    with open(gitignore_file, 'a') as fd:
        for item in ignore_list:
            fd.write('{}\n'.format(item))


def configure_version_control(branch_name='main',
                              msg='first commit'):
    """
        Configure git version control

        :param branch_name: name for the branch [default: main]
        :param msg: message for first commit [default "first commit"]

        Initialize git, add files, commit on requested branch
    """
    subprocess.check_call(['git', 'init'])
    subprocess.check_call(['git', 'add', '.'])
    subprocess.check_call(['git', 'commit', '-m', msg])
    subprocess.check_call(['git', 'branch', '-m', branch_name])


class ToolConfig:
    """
    Info on tool configuration
    """

    def __init__(self):

        # path to list of config files
        self.tool_config_files: List[str] = []

        # path to file containing requirements (requirements.txt style)
        self.requirements: List[str] = []

        # dict containing tool settings
        self.vscode_config: dict = {}


    _T = TypeVar("_T")
    @classmethod
    def from_folder(cls: Type[_T], config_folder) -> _T:
        """
        Create configuration object from folder

        :param config_folder: configuration folder
        :return: configuration object

        Configuration folder must contain:
        - config_files folder: only first level files are considered
        - requirements.txt: list of requirements, adhering requirements.txt style
        - vscode_config.json: json with configuration, .vscode/config.json style
        """
        config = cls()

        config.tool_config_files = [
            os.path.join(config_folder, 'config_files', item.name)
            for item in os.scandir(os.path.join(config_folder, 'config_files')) if item.is_file()
        ]
    
        with open(os.path.join(config_folder,'requirements.txt'), "r") as f:
            config.requirements.extend(f.read().split())

        try:

            vscode_config_file = os.path.join(config_folder, 'vscode_config.json')
            with open(vscode_config_file, "r") as f:
                config.vscode_config = json.load(f)
        
        except json.JSONDecodeError:
            if os.path.getsize(vscode_config_file) != 0:
                raise
    
        return config

    def __add__(self, other):
        """
        Add two configuration objects

        :param other: other configuration object
        :return: a new configuration object with merged results
        """
        new_cfg = ToolConfig()
        new_cfg = copy.deepcopy(self)
        new_cfg += other
        return new_cfg

    def __iadd__(self, other):
        """
        In place merge of configuration objects

        :param other: other configuration object
        :return: updated object with merged results
        """
        self.tool_config_files.extend(other.tool_config_files)
        self.requirements.extend(other.requirements)
        self.vscode_config = {**self.vscode_config, **other.vscode_config}
        return self

    def __repr__(self) -> str:

        out = '\n\ntool_config_files:\n'
        out += self.tool_config_files.__repr__()
        out += '\n\nrequirements:\n'
        out += self.requirements.__repr__()
        out += '\n\nvscode_config:\n'
        out += self.vscode_config.__repr__()

        return out

def do_post_hook():

    gitignore_template = '.gitignore.template'
    vscode_config_file = '.vscode/settings.json'
    tools_config_folder = 'tools_configs'

    # Jinja values
    virtualenv_name = '{{cookiecutter.virtualenv_name}}'
    do_configure_git = str2bool('{{cookiecutter.configure_version_control}}')
    do_upgrade_pip = str2bool('{{cookiecutter.upgrade_pip}}')
    do_support_ipython = str2bool('{{cookiecutter.ipython_support}}')
    chosen_linter = '{{cookiecutter.linter}}'
    chosen_formatter = '{{cookiecutter.formatter}}'

    supported_tools = [
        item.name for item in os.scandir(tools_config_folder) if item.is_dir()
    ]

    tools_list = [chosen_linter, chosen_formatter]
    tools_list = list(filter(lambda x: x.lower() not in ['', 'no'], tools_list))

    print('Running post-gen hook')
    # initialize base configuration
    master_cfg = ToolConfig()
    with open(vscode_config_file, "r") as f:
        master_cfg.vscode_config = json.load(f)

    # collect configurations from tools
    try:
        print('{}: configuration tools collection'.format(__name__))

        for tool in tools_list:
            print('{}: configure {}'.format(__name__, tool))

            if tool not in supported_tools:
                raise Exception('{} tool not supported'.format(tool))

            # get configuration
            cfg = ToolConfig.from_folder(os.path.join(tools_config_folder, tool))

            master_cfg += cfg

    except Exception as e:
        print('{}: exception caught\nexiting\n{}'.format(__name__, e))
        sys.exit(-1)

    print('{}: configuration'.format(__name__))
    print('{}:{}'.format(__name__, master_cfg))

    try:
        ### CONFIGURATION FILES
        for item in master_cfg.tool_config_files:
            shutil.copy2(item, './')

        ### PREREQUISITES SETUP
        with open('requirements-test.txt', 'a') as fd:
            fd.write('\n'.join(master_cfg.requirements))

        ### VIRTUALENV
        print('{}: create virtualenv'.format(__name__))
        venv_create(venv_home=virtualenv_name,
                    requirements_files=[
                        'requirements.txt','requirements-test.txt'
                    ],
                    upgrade_pip=do_upgrade_pip,
                    ipython_support=do_support_ipython)
        
        ### GITIGNORE
        print('{}: configure gitignore'.format(__name__))
        gitignore_config(gitignore_template, [virtualenv_name])

        ### VSCODE CONFIGURATION
        print('{}: configure vscode'.format(__name__))
        with open(vscode_config_file, 'w') as f:
            json.dump(master_cfg.vscode_config, f, indent=4)

        # ### VERSION CONTROL SETTINGS
        if do_configure_git:
            print('{}: configure git'.format(__name__))
            configure_version_control()

    except Exception as e:
        print('{}: exception caught\nexiting\n{}'.format(__name__, e))
        sys.exit(-1)


do_post_hook()
