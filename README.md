# pyteal-playground

## Development Setup

This repo requires Python 3.10 or higher. We recommend you use a Python virtual environment to install
the required dependencies.

Installing Python:
- 	use `pyenv` to install + manage your global python version (use >3.10)

Set up venv aka virtual environment (one time):

-   `python -m venv venv`

Active venv (VSCode does this automatically if you open the project root):

-   `. venv/bin/activate` (if your shell is bash/zsh)
-   `. venv/bin/activate.fish` (if your shell is fish)

Install dependencies:

-   `pip install -r requirements.txt`

## Compile PyTeal -> TEAL

once in python env...

1. `cd pyteal/00_intro`
2. `python3 contract.py`
