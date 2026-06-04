from dataclasses import dataclass


class MockSessionOrTable:
    def exec(self, query):
        return self

    def where(self, *kwargs):
        return self

    def one_or_none(self):
        return None

    def get(self, model, id):
        return None

    def delete(self, item):
        return self

    def commit(self):
        return None

    def add(self, item):
        return None

    def refresh(self, item):
        return None


@dataclass
class MockCredentials:
    username: str
    password: str
