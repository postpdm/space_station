# Architecture

* ASGI web host
* web application on python
* SQLAlchemy supported database
* static storage


# For system administrators and dev ops

Application is a standart ASGI Python web application with Litestar framework core.

Central database is SQLAlchemy supported database with Config .env files or DATABASE_URL environment string.

Solution's databases is specific for each, see the plugins docs.

Becourse of 'enterprise kind of project' you should provide the user authorisation and role-based rules by your side. Best options is a `x-remote-user` headers [https://nginx.org/en/docs/http/ngx_http_proxy_module.html](see NGINX for example) or [https://docs.nginx.com/nginx/deployment-guides/single-sign-on/](SSO), provided from you web-server with SSO integration, or `i'm a USER` authorisation URL. Solution developers should know nothing about your Auth or AD infrastructure.

# For core developers

Space station core provide the central functions without business logic: 

* Users
* User notifications and communications
* Reg and unreg of plugins and solutions
* Manage the internal and external API KEYs

Core web contain several blocks
* core REST API
* admin panel (for system administators)
* user front-end (for users who want to browse the list of avalable solutions).

In typical situations users of solutions would not see any part of Space Station interface (only if curiuous).

# For solution developers

Solutions could be several types

* CMS/Forum/blog style (user frontend and admin/editor section)
* Static site
* Static (SPA) with REST API functionality
* Lambda-style calculators
* Full stack ASGI plugins

# API Keys

Solution developers of static sites with access to core API or another solutions API should manage the API KEY. 

Full stack plugins may publish it's own API with API KEY only.
