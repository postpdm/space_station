from contextvars import ContextVar

# container for key. 
# https://docs.python.org/3/library/contextvars.html

db_encryption_key: ContextVar[str] = ContextVar("db_encryption_key")
