import time
from datetime import datetime
from random import choice, randint
from typing import Annotated
from uuid import uuid4

from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine, select

from .models import Task, User
from ..auth.common import hash_password

engine = create_engine("sqlite:///database.db")


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


_USER_SEED_NAMES = ['RogerF', 'RafaelN', 'AndyM', 'SerenaW', 'EmmaR', 'MariaS', 'NovacD', 'MadisonK', 'IgaSw', 'GaelM']
_TASK_SEED_TITLES = [
    'Put all eggs into one basket',
    'Count chickens before they hatch',
    'Put the cart before the horse',
    'Wake the sleeping dog',
    'Cross the bridge before getting to it',
    'Make a mountain out of a molehill',
    'Lambast the ocean',
    'Throw stones from a glass house',
    'Commit great acts of tomfoolery',
    'Judge a book by its cover',
    'Leap without looking'
]


def random_choice_excluding(choices: list, exceptions: list):
    return choice([c for c in choices if c not in exceptions])


def seed_data():
    with Session(engine) as session:
        users = list(session.exec(select(User)).all())
        while len(users) < 10:
            user = User(
                username=random_choice_excluding(_USER_SEED_NAMES, [u.username for u in users]),
                id=uuid4(),
                password=hash_password(''.join(chr(randint(0, 256)) for i in range(20))),
                admin=randint(0, 1) == 0,  # Randomly assign admin status
            )
            session.add(user)
            users.append(user)

        # Testing purposes only: seed 2 standard users with set credentials for the sake of assessor
        if not session.exec(select(User).where(User.username == 'admin')).one_or_none():
            session.add(User(
                username='admin',
                id=uuid4(),
                # use simple password for testing purposes, not for real life usage
                password=hash_password('admin123'),
                admin=True
            ))
        if not session.exec(select(User).where(User.username == 'user1')).one_or_none():
            session.add(User(
                username='user1',
                id=uuid4(),
                # use simple password for testing purposes, not for real life usage
                password=hash_password('user123'),
                admin=False
            ))

        tasks = list(session.exec(select(Task)).all())
        while len(tasks) < 10:
            random_number = randint(1, 1_000_000)
            task_title = random_choice_excluding(_TASK_SEED_TITLES, [t.title for t in tasks])
            task = Task(
                title=task_title,
                id=uuid4(),
                description=f'Need to {task_title}',
                assigned_to=choice(users).id,
                created_by=choice(users).id,
                completed=random_number % 2 == 0,
                due=datetime.fromtimestamp(time.time() + random_number),
            )
            session.add(task)
            tasks.append(task)

        session.commit()


def get_session():
    with Session(engine) as session:
        yield session


def startup():
    create_db_and_tables()
    seed_data()


DBSessionDep = Annotated[Session, Depends(get_session)]
