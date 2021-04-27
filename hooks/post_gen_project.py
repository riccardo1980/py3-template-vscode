import configparser
import os
import sys
import subprocess
import venv
from typing import List
from pathlib import Path


class ExtendedEnvBuilder(venv.EnvBuilder):
    """
        from: https://github.com/LP-CDF/AMi_Image_Analysis/blob/master/Setup.py
    """
    def __init__(self, *args, **kwargs):
        self.requirements_files = kwargs.pop('requirements_files',
                                             ['requirements.txt'])
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

        # print('WILL INSTALL packages from: ', self.requirements_files)

        binpath = Path(context.bin_path).joinpath("python3")
        # print("PYTHONPATH: ", binpath)

        for req in self.requirements_files:
            subprocess.check_call(
                [binpath, '-m', 'pip', 'install', "--prefix",
                 context.env_dir, '-r', req]
            )


def venv_create(venv_home: str, requirements_files: List[str]):
    """
        create virtualenv
    """
    builder = ExtendedEnvBuilder(
        with_pip=True,
        requirements_files=requirements_files
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
                  linter_ignore: List[str]):

    config = configparser.ConfigParser()
    config['flake8'] = {
        'exclude': ','.join(linter_ignore)
    }
    with open(linter_config_file, 'w') as configfile:
        config.write(configfile)


def configure_version_control(branch_name='main',
                              msg='first commit'):
    subprocess.check_call(['git', 'init'])
    subprocess.check_call(['git', 'add'])
    subprocess.check_call(['git', 'commit', '-m', msg])
    subprocess.check_call(['git', 'branch', '-m', branch_name])


def runme():

    LINTER_CONFIG = '.flake8'
    GITIGNORE_TEMPLATE = '.gitignore.template'
    GITIGNORE = '.gitignore'
    VENV_HOME = '{{cookiecutter.virtualenv_name}}'

    print('Running post-gen hook')

    try:
        print('{}: create virtualenv'.format(__file__))

        venv_create(venv_home=VENV_HOME,
                    requirements_files=['requirements-test.txt'])

        gitignore_config(GITIGNORE_TEMPLATE,
                         GITIGNORE,
                         [VENV_HOME])

        # create .flake8 configuration
        # add virtualenv folder to exclude list
        linter_config(linter_config_file=LINTER_CONFIG,
                      linter_ignore=[VENV_HOME])

        # activate version control
        # change branch name: master to main
        configure_version_control()

    except Exception as e:
        print('{}: exception caught\nexiting\n{}'.format(__file__, e))
        sys.exit(-1)


runme()
