from .services import response_json_with_status_code
from rest_framework.decorators import api_view

from rest_framework import viewsets
from api.serializers import TournamentSerializer, MatchSerializer
from api.models import Tournament, Match, MatchStatus
from django.http import HttpResponse


class TournamentViewSet(viewsets.ModelViewSet):
    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer


class MatchViewSet(viewsets.ModelViewSet):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer


def find_active_or_scheduled_match(just_active):
    match = None

    try:
        # first find if there is an active match
        # if no active match return first scheduled
        match = Match.objects.filter(status=MatchStatus.active).order_by('id')[0]
        if just_active:
            if match:
                return match
    except:
        try:
            if not just_active:
                match = Match.objects.filter(status=MatchStatus.scheduled).order_by('id')[0]
        except:
            pass

    return match


@api_view(['GET'])
def get_next_match(request):
    match = find_active_or_scheduled_match(False)
    return response_json_with_status_code(200, str(match))


@api_view(['GET'])
def start_stop_match(request):
    match = find_active_or_scheduled_match(False)

    if match:
        if match.status == MatchStatus.scheduled:
            match.status = MatchStatus.active
            match.save()
            return response_json_with_status_code(200, (str(match) + "- started"))

        elif match.status == MatchStatus.active:
            match.status = MatchStatus.completed
            match.save()
            return response_json_with_status_code(200, (str(match) + "- ended"))

    else:
        return response_json_with_status_code(404, "no match found")


@api_view(['GET'])
def increment_decrement_score(request):
    command = request.GET.get('command', '')
    team = request.GET.get('team', '')

    if command and team:
        match = find_active_or_scheduled_match(True)
        if match:
            if command == 'inc':
                print("inc")
                if team == 'home':
                    match.home_score += 1
                    match.save()
                    return response_json_with_status_code(200, 'home inc')
                elif team == 'away':
                    match.away_score += 1
                    match.save()
                    return response_json_with_status_code(200, 'away inc')
            elif command == 'dec':
                print("dec")
                if team == 'home':
                    if match.home_score > 0:
                        match.home_score -= 1
                        match.save()
                        return response_json_with_status_code(200, 'home dec')
                    else:
                        return response_json_with_status_code(404, 'cannot dec 0')
                elif team == 'away':
                    if match.away_score > 0:
                        match.away_score -= 1
                        match.save()
                        return response_json_with_status_code(200, 'away dec')
                    else:
                        return response_json_with_status_code(404, 'cannot dec 0')
        else:
            return response_json_with_status_code(404, 'no active match')

    else:
        return response_json_with_status_code(404, 'missing parameters')
