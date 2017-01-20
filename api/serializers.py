from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import Tournament, Match, Profile


class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'


class TournamentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tournament
        fields = '__all__'


class MatchSerializer(serializers.HyperlinkedModelSerializer):
    home = ProfileSerializer()
    away = ProfileSerializer()

    class Meta:
        model = Match
        fields = ('__all__')
