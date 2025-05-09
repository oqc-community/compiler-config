import os


def format_code():
    os.system("poetry run ruff check --fix")
    os.system("poetry run ruff format")
