# Architecture

# For system administrators and dev ops

Aplication is a standart ASGI Python web application with Litestar framework core.

Central database is SQLAlchemy supported database with Config .env files or DATABASE_URL environment string.


Becourse of 'enterprise kind' you should provide the user authorisation and role-based rules by your side. Best options is a `x-remote-user` headers, provided from you web-server with SSO integration, or `i'm a USER` authorisation URL.

# For core developers

# For solition developers
