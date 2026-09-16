# connections to external db

from advanced_alchemy.config import SQLAlchemyAsyncConfig

# test connection
async def check_ext_db_connection( arg_database_url : str ) -> tuple[bool, str]:
    db_config = SQLAlchemyAsyncConfig( connection_string = arg_database_url )
    engine = None
    
    try:
        # Retrieve the SQLAlchemy AsyncEngine from the Advanced Alchemy config
        engine = db_config.get_engine()
        async with engine.connect() as conn:
            return True, "✅ Database connection established successfully!"
    except Exception as e:
        return False, f"❌ Connection error: {e}"
    finally:
        if engine is not None:
            await engine.dispose()
