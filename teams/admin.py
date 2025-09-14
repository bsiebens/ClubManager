from django.contrib import admin

from .models import Season, TeamRole, Team, TeamMembership, TeamPicture

admin.site.register(Season)
admin.site.register(TeamRole)
admin.site.register(Team)
admin.site.register(TeamMembership)
admin.site.register(TeamPicture)
