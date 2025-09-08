from rules.contrib.rest_framework import AutoPermissionViewSetMixin


class AutoListPermissionViewSetMixin(AutoPermissionViewSetMixin):
    permission_type_map = {
        **AutoPermissionViewSetMixin.permission_type_map,
        "list": "view",
        "metadata": "view",
    }
