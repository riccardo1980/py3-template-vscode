import configparser
import os
import sys
import subprocess
import venv
from typing import List
from pathlib import Path

def str2bool(v):
    return v.lower() in ("yes", 'true', 'si', 'y', 's', '1')

flag_upgrade_pip = str2bool('{{cookiecutter.upgrade_pip}}')
flag_configure_version_control = str2bool('{{cookiecutter.configure_version_control}}')
flag_ipython_support = str2bool('{{cookiecutter.ipython_support}}')


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
    subprocess.check_call(['git', 'add', '.'])
    subprocess.check_call(['git', 'commit', '-m', msg])
    subprocess.check_call(['git', 'branch', '-m', branch_name])


def do_post_hook():

    LINTER_CONFIG = '.flake8'
    GITIGNORE_TEMPLATE = '.gitignore.template'
    GITIGNORE = '.gitignore'
    VENV_HOME = '{{cookiecutter.virtualenv_name}}'

    print('Running post-gen hook')

    try:
        print('{}: create virtualenv'.format(__name__))

        venv_create(venv_home=VENV_HOME,
                    requirements_files=['requirements-test.txt'],
                    upgrade_pip=flag_upgrade_pip,
                    ipython_support=flag_ipython_support)

        print('{}: configure gitignore'.format(__name__))
        gitignore_config(GITIGNORE_TEMPLATE,
                         GITIGNORE,
                         [VENV_HOME])

        # create .flake8 configuration
        # add virtualenv folder to exclude list
        print('{}: configure linter'.format(__name__))
        linter_config(linter_config_file=LINTER_CONFIG,
                      linter_ignore=[VENV_HOME])

        # activate version control
        # change branch name: master to main
        if flag_configure_version_control:
            print('{}: configure git'.format(__name__))
            configure_version_control()

    except Exception as e:
        print('{}: exception caught\nexiting\n{}'.format(__file__, e))
        sys.exit(-1)


do_post_hook()
