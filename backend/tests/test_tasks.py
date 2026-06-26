from uuid import uuid4
from fastapi import HTTPException
import pytest
from pytest_mock import MockerFixture
# import auth first to get around circular import issue
import src.auth  # noqa: F401
from src.db.models import Task, User
from src.tasks import api
from mocks import MockSessionOrTable

def test_only_owners_or_admin_can_update_task(mocker: MockerFixture):
    session = MockSessionOrTable()
    task = Task(title='', description=None, created_by=uuid4(), assigned_to=uuid4(), id=uuid4())
    mocker.patch.object(session, 'get', return_value=task)
    user = User(id=uuid4(), username='', password='')

    with pytest.raises(HTTPException):
        api.update_task(task.id, task_details=task, session=session, user=user)


def test_only_admin_can_delete_task(mocker: MockerFixture):
    session = MockSessionOrTable()
    task = Task(title='', description=None, created_by=uuid4(), assigned_to=uuid4(), id=uuid4())
    mocker.patch.object(session, 'get', return_value=task)
    user = User(id=task.id, username='', password='')

    with pytest.raises(HTTPException):
        api.delete_task(task.id, session=session, user=user)

    user.admin = True
    api.delete_task(task.id, session, user)


def test_raises_404_if_task_not_found(mocker: MockerFixture):
    session = MockSessionOrTable()
    mocker.patch.object(session, 'get', return_value=None)
    user = User(id=uuid4(), username='', password='')

    with pytest.raises(HTTPException):
        api.read_task(uuid4(), session=session)

    with pytest.raises(HTTPException):
        api.update_task(uuid4(), task_details=Task(title='', description=None), session=session, user=user)

    with pytest.raises(HTTPException):
        api.delete_task(uuid4(), session=session, user=user)
