from ninja import NinjaAPI

from members.api import router as members_router

api = NinjaAPI()

api.add_router("/members", members_router)
