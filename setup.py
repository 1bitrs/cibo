from setuptools import setup

# Metadata goes in setup.cfg. These are here for GitHub's dependency graph.
setup(
    name="cibo",
    install_requires=[
        "Flask==1.1.1",
        "pydantic==1.6.2",
        "apispec==5.0.0",
        "typing-extensions==3.10.0.2"
    ],
    extras_require={
    },
)
