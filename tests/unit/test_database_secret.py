import importlib
import json


def test_build_db_url_with_secret(monkeypatch):
    # Simula o secrets manager retornando credenciais
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("SQLALCHEMY_DATABASE_URL", raising=False)
    monkeypatch.setenv("DB_SECRET_NAME", "mysecret")

    class FakeSM:
        def __init__(self, **kwargs):
            pass

        def get_secret_value(self, SecretId):
            return {"SecretString": json.dumps({
                "host": "db.local",
                "port": 5432,
                "username": "user",
                "password": "pass",
                "dbname": "mydb"
            })}

    def fake_boto3_client(name, region_name=None):
        return FakeSM()

    monkeypatch.setenv("AWS_REGION", "us-east-1")

    import importlib, sys, types

    # Save originals to restore later
    orig_boto3 = sys.modules.get("boto3")
    orig_sqlalchemy = sys.modules.get("sqlalchemy")
    orig_sqlalchemy_orm = sys.modules.get("sqlalchemy.orm")

    try:
        # Inject fake boto3 and fake sqlalchemy into sys.modules before importing the module
        fake_boto3 = types.ModuleType("boto3")
        fake_boto3.client = lambda service, region_name=None: FakeSM()
        sys.modules["boto3"] = fake_boto3

        # Provide a minimal fake sqlalchemy and sqlalchemy.orm to avoid real engine creation
        fake_sqlalchemy = types.ModuleType("sqlalchemy")
        fake_sqlalchemy.create_engine = lambda url: None
        sys.modules["sqlalchemy"] = fake_sqlalchemy

        fake_sqlalchemy_orm = types.ModuleType("sqlalchemy.orm")
        fake_sqlalchemy_orm.sessionmaker = lambda **kwargs: lambda: None
        fake_sqlalchemy_orm.declarative_base = lambda: object
        sys.modules["sqlalchemy.orm"] = fake_sqlalchemy_orm

        mod = importlib.import_module("app.infrastructure.db.database")

        # call only the function we want to test
        url = mod._build_db_url()
        assert url.startswith("postgresql://")
        assert "user" in url and "pass" in url and "mydb" in url
    finally:
        # restore originals
        if orig_boto3 is not None:
            sys.modules["boto3"] = orig_boto3
        else:
            sys.modules.pop("boto3", None)
        if orig_sqlalchemy is not None:
            sys.modules["sqlalchemy"] = orig_sqlalchemy
        else:
            sys.modules.pop("sqlalchemy", None)
        if orig_sqlalchemy_orm is not None:
            sys.modules["sqlalchemy.orm"] = orig_sqlalchemy_orm
        else:
            sys.modules.pop("sqlalchemy.orm", None)


def test_build_db_url_secret_missing_fields(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("SQLALCHEMY_DATABASE_URL", raising=False)
    monkeypatch.setenv("DB_SECRET_NAME", "mysecret")

    class FakeSMBad:
        def get_secret_value(self, SecretId):
            return {"SecretString": json.dumps({"host": "db.local"})}

    def fake_boto3_client(name, region_name=None):
        return FakeSMBad()

    import importlib, sys, types

    # Save originals to restore later
    orig_boto3 = sys.modules.get("boto3")
    orig_sqlalchemy = sys.modules.get("sqlalchemy")
    orig_sqlalchemy_orm = sys.modules.get("sqlalchemy.orm")

    try:
        # Inject fake boto3 and fake sqlalchemy into sys.modules before importing the module
        fake_boto3 = types.ModuleType("boto3")
        fake_boto3.client = lambda service, region_name=None: FakeSMBad()
        sys.modules["boto3"] = fake_boto3

        fake_sqlalchemy = types.ModuleType("sqlalchemy")
        fake_sqlalchemy.create_engine = lambda url: None
        sys.modules["sqlalchemy"] = fake_sqlalchemy

        fake_sqlalchemy_orm = types.ModuleType("sqlalchemy.orm")
        fake_sqlalchemy_orm.sessionmaker = lambda **kwargs: lambda: None
        fake_sqlalchemy_orm.declarative_base = lambda: object
        sys.modules["sqlalchemy.orm"] = fake_sqlalchemy_orm

        mod = importlib.import_module("app.infrastructure.db.database")

        try:
            mod._build_db_url()
            assert False, "Expected RuntimeError"
        except RuntimeError:
            assert True
    finally:
        # restore originals
        if orig_boto3 is not None:
            sys.modules["boto3"] = orig_boto3
        else:
            sys.modules.pop("boto3", None)
        if orig_sqlalchemy is not None:
            sys.modules["sqlalchemy"] = orig_sqlalchemy
        else:
            sys.modules.pop("sqlalchemy", None)
        if orig_sqlalchemy_orm is not None:
            sys.modules["sqlalchemy.orm"] = orig_sqlalchemy_orm
        else:
            sys.modules.pop("sqlalchemy.orm", None)
