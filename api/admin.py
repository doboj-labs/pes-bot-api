from django.contrib import admin
from .models import Tournament, Match, Profile, Team

admin.site.register(Tournament)
admin.site.register(Match)
admin.site.register(Profile)
admin.site.register(Team)
