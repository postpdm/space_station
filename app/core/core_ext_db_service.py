# connections to external db

from advanced_alchemy.config import SQLAlchemyAsyncConfig
from sqlalchemy.engine import make_url

async def check_ext_db_connection(
    arg_database_url: str,
    arg_password: str | None = None,
) -> tuple[bool, str]:
    engine = None
    try:
        url = make_url(arg_database_url)

        # URL should not contain password, only as arg_password.
        if url.password is not None:
            raise ValueError(
                "Database URL must not contain a password. "
                "Pass it via the 'arg_password' argument instead."
            )

        if arg_password is not None:
            url = url.set(password=arg_password)

        connection_string = url.render_as_string(hide_password=False)
        db_config = SQLAlchemyAsyncConfig(connection_string=connection_string)

        engine = db_config.get_engine()
        async with engine.connect() as conn:
            return True, "✅ Database connection established successfully!"

    except Exception as e:
        return False, f"❌ Connection error: {e}"
    finally:
        if engine is not None:
            await engine.dispose()