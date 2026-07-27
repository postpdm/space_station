from litestar import Controller, post, get

class Dummy_One_Page_Static_Controller(Controller):
    path = "/dops"
    #tags = ["Authentication"]

    @get("/show")
    async def show(self) -> str:
        return "Hello from dummy!"
