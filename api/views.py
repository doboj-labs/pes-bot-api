from .services import response_json_with_status_code
from rest_framework.decorators import api_view

from rest_framework import viewsets
from api.serializers import TournamentSerializer, MatchSerializer
from api.models import Tournament, Match, MatchStatus


class TournamentViewSet(viewsets.ModelViewSet):
    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer


class MatchViewSet(viewsets.ModelViewSet):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer


@api_view(['GET'])
def get_next_match(request):
    match = None

    try:
        # first find if there is an active match
        # if no active match return first scheudled
        match = Match.objects.filter(status=MatchStatus.active).order_by('id')[0]
    except:
        try:
            match = Match.objects.filter(status=MatchStatus.scheduled).order_by('id')[0]
        except:
            pass

    return response_json_with_status_code(200, match)
