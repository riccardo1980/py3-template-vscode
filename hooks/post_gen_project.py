import os
import sys
import subprocess
import venv
from typing import List
from pathlib import Path

def str2bool(v):
    return v.lower() in ("yes", 'true', 'si', 'y', 's', '1')

FLAG_UPGRADE_PIP = str2bool('{{cookiecutter.upgrade_pip}}')
FLAG_CONFIGURE_VERSION_CONTROL = str2bool('{{cookiecutter.configure_version_control}}')
FLAG_IPYTHON_SUPPORT = str2bool('{{cookiecutter.ipython_support}}')
CHOSEN_LINTER = '{{cookiecutter.linter}}'


class ExtendedEnvBuilder(venv.EnvBuilder):
    """
        from: https://github.com/LP-CDF/AMi_Image_Analysis/blob/master/Setup.py
    """
    def __init__(self, *args, **kwargs):
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
        create virtualenv
    """
    builder = ExtendedEnvBuilder(
        with_pip=True,
        **kwargs
        )
    builder.create(venv_home)


def gitignore_config(gitignore_template: str,
                     gitignore_file: str,
                     ignore_list: List[str]):

    os.rename(gitignore_template,
              gitignore_file)

    # ignore list to .gitignore
    with open(gitignore_file, 'a') as f:
        for item in ignore_list:
            f.write('{}\n'.format(item))


def linter_config(linter_config_file: str,
                  linter_config_string: str):

    with open(linter_config_file, 'w') as f:
        f.write(linter_config_string)


def configure_version_control(branch_name='main',
                              msg='first commit'):
    subprocess.check_call(['git', 'init'])
    subprocess.check_call(['git', 'add', '.'])
    subprocess.check_call(['git', 'commit', '-m', msg])
    subprocess.check_call(['git', 'branch', '-m', branch_name])


def do_post_hook():

    GITIGNORE_TEMPLATE = '.gitignore.template'
    GITIGNORE = '.gitignore'
    VENV_HOME = '{{cookiecutter.virtualenv_name}}'

    LINTER_SETTINGS = {
        'pylint': {
            'prerequisites': ['pylint==2.9.3'],
            'config_filename': '.pylintrc',
            'config_content': '\n'.join(
                [
                    '[master]',
                    'extension-pkg-whitelist=pydantic'
                ]
            ),
            'vscode-config': {
                    "python.linting.enabled": True,
                    "python.linting.pylintEnabled": True,
                    "python.linting.pylintArgs": [
                        "--rcfile=${workspaceFolder}/.pylintrc",
                        "--init-hook",
                        "import sys; sys.path.insert(0, '${workspaceFolder}')"
                    ]
                }
        },
        'flake8' : {
            'prerequisites': ['flake8==3.9.0'],
            'config_filename': '.flake8',
            'config_content': '\n'.join(
                [
                'ignore: {{cookiecutter.virtualenv_name}}'
                ]
            ),
            'vscode-config': {
                "python.linting.enabled": True,
                "python.linting.flake8Enabled": True
            }
        }
    }


    print('Running post-gen hook')

    try:
        if CHOSEN_LINTER not in ['pylint', 'flake8']:
            raise Exception('linter not supported')

        ### PREREQUISITES SETUP
        with open('requirements-test.txt', 'a') as f:
            for item in LINTER_SETTINGS[CHOSEN_LINTER]['prerequisites']:
                f.write(item)

        ### VIRTUALENV
        print('{}: create virtualenv'.format(__name__))

        venv_create(venv_home=VENV_HOME,
                    requirements_files=['requirements-test.txt'],
                    upgrade_pip=FLAG_UPGRADE_PIP,
                    ipython_support=FLAG_IPYTHON_SUPPORT)

        print('{}: configure gitignore'.format(__name__))
        gitignore_config(GITIGNORE_TEMPLATE,
                         GITIGNORE,
                         [VENV_HOME])

        ### LINTER CONFIGURATION
        # create linter configuration
        # add virtualenv folder to exclude list
        print('{}: configure linter'.format(__name__))
        linter_config(
            LINTER_SETTINGS[CHOSEN_LINTER]['config_filename'],
            linter_config_string=LINTER_SETTINGS[CHOSEN_LINTER]['config_content']
         )

        ### VSCODE CONFIGURATION
        print('{}: configure vscode'.format(__name__))
        import json
        VSCODE_CONFIG_FILE='.vscode/settings.json'

        with open(VSCODE_CONFIG_FILE, "r") as f:
            vscode_minimal_config = json.load(f)

        vscode_config = { **vscode_minimal_config, **LINTER_SETTINGS[CHOSEN_LINTER]['vscode-config']}

        with open(VSCODE_CONFIG_FILE, 'w') as f:
            json.dump(vscode_config, f, indent=4)

        # ### VERSION CONTROL SETTINGS
        # activate version control
        # change branch name: master to main
        if FLAG_CONFIGURE_VERSION_CONTROL:
            print('{}: configure git'.format(__name__))
            configure_version_control()

    except Exception as e:
        print('{}: exception caught\nexiting\n{}'.format(__file__, e))
        sys.exit(-1)


do_post_hook()
