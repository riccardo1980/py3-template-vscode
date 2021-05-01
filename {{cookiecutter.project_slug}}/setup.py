from setuptools import setup, find_packages

setup(name='{{cookiecutter.package_name}}',
    packages=find_packages(
        include=['{{cookiecutter.package_name}}', '{{cookiecutter.package_name}}.*']
    )
)