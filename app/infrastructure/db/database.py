import os
import json
from urllib.parse import quote_plus
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

def _build_db_url() -> str:
    direct = os.getenv("DATABASE_URL") or os.getenv("SQLALCHEMY_DATABASE_URL")

    if direct:
        return direct

    injected_secret = os.getenv("DB_SECRET")
    if injected_secret:
        try:
            # Permite também passar a URL direta via DB_SECRET.
            if "://" in injected_secret:
                return injected_secret

            data = json.loads(injected_secret)

            host = data.get("host")
            port = data.get("port", 5432)
            user = data.get("username") or data.get("user")
            pwd = data.get("password")
            dbname = data.get("dbname") or data.get("database")

            if not all([host, user, pwd, dbname]):
                raise ValueError("DB_SECRET missing required fields")

            return f"postgresql://{quote_plus(str(user))}:{quote_plus(str(pwd))}@{host}:{port}/{dbname}"
        except Exception as e:
            raise RuntimeError(
                "Database configuration error: could not build DB URL from DB_SECRET. "
                "Set DATABASE_URL/SQLALCHEMY_DATABASE_URL, or provide a valid DB_SECRET (json with host/port/username/password/dbname), "
                "or set DB_SECRET_NAME to fetch from Secrets Manager."
            ) from e
    
    secret_name = os.getenv("DB_SECRET_NAME")
    if secret_name:
        try:
            import boto3

            region = os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION") or "us-east-1"
            sm = boto3.client("secretsmanager", region_name=region)
            sec = sm.get_secret_value(SecretId=secret_name)["SecretString"]
            data = json.loads(sec)

            host = data.get("host")
            port = data.get("port", 5432)
            user = data.get("username") or data.get("user")
            pwd = data.get("password")
            dbname = data.get("dbname") or data.get("database")

            if not all([host, user, pwd, dbname]):
                raise ValueError(f"Secret {secret_name} missing required fields")

            return f"postgresql://{quote_plus(str(user))}:{quote_plus(str(pwd))}@{host}:{port}/{dbname}"
        except Exception as e:

            raise RuntimeError(
                "Database configuration error: could not build DB URL from environment or Secrets Manager. "
                "Set DATABASE_URL/SQLALCHEMY_DATABASE_URL, or provide DB_SECRET, or ensure DB_SECRET_NAME is readable and has host/port/username/password/dbname."
            ) from e

    raise RuntimeError(
        "Database configuration error: DATABASE_URL/SQLALCHEMY_DATABASE_URL not set and neither DB_SECRET nor DB_SECRET_NAME were provided."
    )

engine = create_engine(_build_db_url())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def init_schema() -> None:
    if engine.dialect.name == "postgresql":
        create_video_table_sql = """
        CREATE TABLE IF NOT EXISTS video(
            id INT GENERATED ALWAYS AS IDENTITY,
            user_id INT NULL,
            title VARCHAR(255) NULL,
            file_path VARCHAR(255) NULL,
            status SMALLINT NULL,
            PRIMARY KEY(id)
        );
        """

        with engine.begin() as connection:
            connection.execute(text(create_video_table_sql))
        return

    from app.models.video import Video

    Base.metadata.create_all(bind=engine, tables=[Video.__table__])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()