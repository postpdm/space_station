

Public methods (exclude_from_auth=True)

/users/login

/users/login_form

/users/fake_user

and `/favicon.ico` :)


Auth routing

1 User get the url
2 If no active session, app try to authorise a users depend of `.env` settings

AM_I_USER_URL = url to authorisation service

Authorisation service is your intranet SSO server, it should return current user login (system name) and common name fields, in json.

AM_I_USER_LOGIN_FIELD = user system login
AM_I_USER_NAME_FIELD = user common name


If AM_I_USER_SERVER_REQUEST = True, that mean your Space Station server should has an access to SSO directly. Thus should logon user transparrrantly. This option is more secure.

If AM_I_USER_SERVER_REQUEST = False, that mean your Space Station server have not direct access to SSO. In this case user get the /users/login and /users/login_form routing to confirm hir/her SSO authorisation proceed correctly. User should not enter some name/password, only accept the logon. This option is less secure than previous.

/users/fake_usesr is SSO fantom, for testing purposes only.

Internal user id created in Space Station DB for data linking. User login and name stores in Space Station DB as SSO was return, and should not change.

Browser sessions store in server side, in `session_data` folder and could be deleted at any time.