"""Run setuptools."""

from setuptools import find_packages, setup

from gram_core.version import __version__


def get_setup_kwargs():
    """Builds a dictionary of kwargs for the setup function"""
    kwargs = dict(
        script_name="setup.py",
        name="gram_core",
        version=__version__,
        author="PaiGramTeam",
        url="https://github.com/PaiGramTeam/GramCore",
        keywords="telegram robot base core",
        description="telegram robot base core.",
        long_description=open("README.md", "r", encoding="utf-8").read(),
        long_description_content_type="text/markdown",
        packages=find_packages(exclude=["tests*"]),
        install_requires=[],
        include_package_data=True,
        python_requires=">=3.8",
    )

    return kwargs


def main():  # skipcq: PY-D0003
    setup(**get_setup_kwargs())


if __name__ == "__main__":
    main()
