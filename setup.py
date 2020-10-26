from setuptools import setup, find_packages


def parse_requirements(requirement_file):
    with open(requirement_file) as f:
        return f.readlines()

version = {}
with open("hopper/__version__.py") as fp:
    exec(fp.read(), version)

setup(
    name='hopper',
    version=version['__version__'],
    packages=find_packages(exclude=['tests*']),
    license='MIT',
    description='A Python package to inspect an eml message received from headers from mail messages',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    install_requires=parse_requirements('requirements.txt'),
    keywords=['eml', 'hop', 'received from', 'email'],
    url='https://github.com/msadministrator/hopper',
    author='MSAdministrator',
    author_email='rickardja@live.com',
    python_requires='>=2.6, !=3.0.*, !=3.1.*, !=3.2.*, <4',
    entry_points={
          'console_scripts': [
              'hopper = hopper.__main__:main'
          ]
    }
)
