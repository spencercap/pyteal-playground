# pyteal-playground

## Development Setup

This repo requires Python 3.6 or higher. We recommend you use a Python virtual environment to install
the required dependencies.

Set up venv (one time):

-   `python3 -m venv venv`

Active venv:

-   `. venv/bin/activate` (if your shell is bash/zsh)
-   `. venv/bin/activate.fish` (if your shell is fish)

Install dependencies:

-   `pip install -r requirements.txt`

## Compile PyTeal -> TEAL

once in python env...

1. `cd pyteal/00_intro`
2. `python3 contract.py`
