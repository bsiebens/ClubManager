from django.contrib import admin

from .models import Season, TeamRole, NumberPool, Team, TeamMembership

admin.site.register(Season)
admin.site.register(TeamRole)
admin.site.register(NumberPool)
admin.site.register(Team)
admin.site.register(TeamMembership)
