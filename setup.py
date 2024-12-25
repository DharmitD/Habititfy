from setuptools import setup, find_packages

setup(
    name="habitify",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "transformers>=4.0.0",  # Hugging Face Transformers for GPT-2
        "click>=8.0.0",         # CLI interactions
    ],
    entry_points={
        "console_scripts": [
            "habitify=cli.cli_tool:cli",  # Optional: Create a global CLI command
        ],
    },
)
