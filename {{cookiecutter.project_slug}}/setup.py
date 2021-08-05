from setuptools import find_packages, setup

setup(name='{{cookiecutter.package_name}}',
    packages=find_packages(
        include=['{{cookiecutter.package_name}}', '{{cookiecutter.package_name}}.*']
    )
)