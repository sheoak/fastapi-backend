import pytest

from app.db.init_db import init_db
from app.core import config
from app.models.user import User


@pytest.mark.usefixtures('empty_db')
def test_init_db():
    init_db()
    user = User.get(email=config.FIRST_SUPERUSER)
    assert isinstance(user, User), "First superuser cannot be found"


# how to execute in test mode and check with the rollback?
# @pytest.mark.usefixtures('empty_db')
# @pytest.mark.script_launch_mode('subprocess')
# def test_initial_data_script(script_runner):
#     ret = script_runner.run('python', 'initial_data.py')
#     assert ret.success
