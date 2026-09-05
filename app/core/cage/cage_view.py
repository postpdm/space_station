from litestar import Controller, Litestar, Request, delete, get, patch, post # we don't like "put"

class CageController(Controller):
    path = "/cage"

    @get('/fake_user', exclude_from_auth=True)
    async def get_fake_user(self) -> dict[str, str]:
        """Fake method for local testing purposes"""
        # Litestar automatically converts this dict to a JSON response
        return { "id": "123", "userLogin": "fake_domain\\fake_user", "userName": "Mr. Fake User jr.", 'some_key' : 'some_string' }
