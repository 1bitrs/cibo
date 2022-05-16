from setuptools import setup

# Metadata goes in setup.cfg. These are here for GitHub's dependency graph.
setup(
    name="cibo",
    install_requires=[
        "flask >= 1.1.2",
        "pydantic >= 1.6.2",
        "apispec >= 4.2.0'",
        "typing-extensions; python_version < '3.8'",
    ],
    tests_require=[
        "openapi-spec-validator",
    ],
    extras_require={
        "dotenv": ["python-dotenv"],
        "yaml": ["pyyaml"],
        "async": ["asgiref >= 3.2"],
    },
)
