# Contributing to python-healthchecklib

Thank you for considering contributing to python-healthchecklib! This document outlines the guidelines for contributing to this project.

## Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/0/code_of_conduct/). By participating, you are expected to uphold this code. Please report unacceptable behavior to contact@hathor.network.

## Before You Start 

1. Make sure you open an issue to discuss the changes you want to make before you start working on them. This will help you get feedback on your ideas and avoid wasting time on something that might not be merged.

## How to Contribute

1. Fork the repository and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code lints.
6. Submit a pull request.

## Code Style

This project uses `black` and `isort` to format the code. You can run them with:
- `poetry run black .`.
- `poetry run isort .`.

We also use `flake8` to lint the code and `mypy` to type check it. You can run them with:
- `poetry run flake8 .`.
- `poetry run mypy .`.

## License

By contributing to python-healthchecklib, you agree that your contributions will be licensed under the [MIT License](https://opensource.org/licenses/MIT).

