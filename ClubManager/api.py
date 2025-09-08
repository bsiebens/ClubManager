from rest_framework import routers

from members.api import MembersViewSet

router = routers.DefaultRouter()
router.register(r"members", MembersViewSet)
