from litestar import Controller, post, get

class Dummy_One_Page_Static_Controller(Controller):
    path = "/dops"
    #tags = ["Authentication"]

    @get("/")
    async def user_homepahe(self) -> str:
        return "Hello from dummy!"
    
    @get("/admin_panel")
    async def admin_panel(self) -> str:
        return "Hello dummy admin panel!"
