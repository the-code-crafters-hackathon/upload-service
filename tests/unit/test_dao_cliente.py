import pytest
from types import SimpleNamespace

from app.dao.cliente_dao import ClienteDAO


def test_criar_cliente_commits_and_refresh(monkeypatch):
    class FakeSession:
        def __init__(self):
            self.added = None
            self.committed = False
            self.refreshed = None

        def add(self, obj):
            self.added = obj

        def commit(self):
            self.committed = True

        def refresh(self, obj):
            self.refreshed = obj

    fake_session = FakeSession()
    dao = ClienteDAO(fake_session)

    cliente_in = SimpleNamespace(nome="Fulano", email="f@x.com", telefone=None, cpf="123")
    result = dao.criar_cliente(cliente_in)

    assert fake_session.added is not None
    assert fake_session.committed is True
    assert result is not None


def test_deletar_cliente_raises_when_not_found():
    dao = ClienteDAO(db_session=None)
    dao.buscar_por_id = lambda id: None

    with pytest.raises(ValueError):
        dao.deletar_cliente(999)
