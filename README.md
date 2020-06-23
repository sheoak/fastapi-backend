# fastapi-backend

An API Backend using [Fastapi][1].

This backend was initially started as a fork of [full-stack-fastapi-postgresql][3].
Due to too many modifications it's now detached from the initial project.

Code source should follow [12 factors principle][2] for cloud deployment (heroku,
clevercloud…).


## Differences with full-stack-fastapi-postgresql repository

- Include advanced unitary and functional testing
- Uses pytest-BDD for functional testing
- Model classes have been refactored using [sqlalchemy_mixins][5].
- Special cases have been removed as much as possible to simplify the source code
- Include heroku configuration files samples
- Include github action configuration


## Installation

Create a virtualenv and activate it. Install the requirements:

    pip install -r requirements.txt

Install npm packages for commit linting:

    npm install

Set your .env file with your local settings. Never commit the .env file!
See `.env.sample` for an example.

Run the migrations if your database is empty.
Note that it will create an admin user based on your local configuration.

    alembic upgrade head
    python initial_data.py

The settings use python-dotenv. Your .env file will be merged with the
default settings. All secrets should be in the .env file. This follow the
[12-factor rules][2].


## Run

    web: uvicorn app.main:app

## Running tests

Tests will be run:
- On commit for unitary tests
- On push for integrations tests (slow)

See pytest.ini for default options.

Coverage can be configure via .coveragerc file.

    # activate your virtualenv first…
    # unitary tests (uses markers)
    pytest -m unitary
    # integration tests
    pytest -m integration
    # all tests
    pytest
    # only staged files with pytest-picked
    pytest --picked
    # with coverage
    pytest --cov --cov-report term-missing
    # details with Left/Right errors with pytest-clarity
    pytest --vv

See app/tests/conftest.py for fixtures.
See app/tests/utils/ for the base class for unitary and integration tests.

Note that integration tests use a test database that is rollback for everytest,
which make them slow but independent and predicibles. Test data can be found in
app/tests/data/.

### Pytest tips

#### Run pdb

Add a trace in a test and run pdb

    …
    pytest.set_trace()
    …
    $ pytest --pdb



## Coding

Please request coding guide before starting

[1]: https://fastapi.tiangolo.com/
[2]: https://12factor.net/
[3]: https://github.com/tiangolo/full-stack-fastapi-postgresql
[4]: https://github.com/semantic-release/semantic-release
[5]: https://github.com/absent1706/sqlalchemy-mixins


## License

This project is licensed under the terms of the MIT license.
