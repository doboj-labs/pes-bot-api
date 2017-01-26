from .services import response_json_with_status_code
from rest_framework.decorators import api_view

from rest_framework import viewsets
from api.serializers import TournamentSerializer, MatchSerializer
from api.models import Tournament, Match, MatchStatus

from slackclient import SlackClient
import os
from random import randint

slack_token = os.environ["SLACK_API_TOKEN"]
sc = SlackClient(slack_token)

channel = os.environ['SLACK_CHANEL']
delimeter = '\n-------------------------------------------------' \
            '----------------------------------------------------' \
            '----------------------------------------------------\n'


def send_score_message(match):
    sc.api_call(
        "chat.postMessage",
        channel=channel,
        text="%sCurrent score is:\n %s%s" % (delimeter, match.get_score(), delimeter)
    )


def start_stop_match_message(match, activity):
    if activity == 'started':
        message = "%s%s%s:soccer: Match: %s has %s%s" % (
            delimeter, delimeter, delimeter, match.get_match_names(), activity, delimeter)
    elif activity == 'ended':
        message = "%s:sports_medal: Match: %s has %s with score:\n %s%s%s%s" % (delimeter,
                                                                                match.get_match_names(), activity,
                                                                                match.get_score(), delimeter, delimeter,
                                                                                delimeter)
    sc.api_call(
        "chat.postMessage",
        channel=channel,
        text=message
    )


def send_goal_message(goal_getter, match):
    if (goal_getter == 'home'):
        goal_getter = match.home
        goal_receiver = match.away
    elif (goal_getter == 'away'):
        goal_getter = match.away
        goal_receiver = match.home

    random_messages = [
        "%s:tada: %s scored a goal against %s :tada:%s" % (delimeter, goal_getter, goal_receiver, delimeter),
        "%s:tada: Euro goal scored from %s to %s!!! :tada:%s" % (delimeter, goal_getter, goal_receiver, delimeter)
    ]

    sc.api_call(
        "chat.postMessage",
        channel=channel,
        text=random_messages[randint(0, len(random_messages) - 1)]
    )

    send_score_message(match)


def send_goal_cancel_message(goal_getter, match):
    if (goal_getter == 'home'):
        goal_getter = match.home
        goal_receiver = match.away
    elif (goal_getter == 'away'):
        goal_getter = match.away
        goal_receiver = match.home

    random_messages = [
        "%s:confused: %s last goal against %s was canceled..%s" % (delimeter, goal_getter, goal_receiver, delimeter),
    ]

    sc.api_call(
        "chat.postMessage",
        channel=channel,
        text=random_messages[randint(0, len(random_messages) - 1)]
    )
    send_score_message(match)


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
    if match:
        data = {}
        data['match'] = '%s vs %s' % (match.home.team.slug, match.away.team.slug)
        data['match_status'] = match.status
        data['home'] = match.home_score
        data['away'] = match.away_score
        return response_json_with_status_code(200, data)
    else:
        return response_json_with_status_code(404, 'no match')


@api_view(['GET'])
def start_stop_match(request):
    match = find_active_or_scheduled_match(False)

    if match:
        if match.status == MatchStatus.scheduled:
            match.status = MatchStatus.active
            match.save()
            start_stop_match_message(match, 'started')

            return response_json_with_status_code(200, (str(match) + "- started"))

        elif match.status == MatchStatus.active:
            match.status = MatchStatus.completed
            match.save()
            start_stop_match_message(match, 'ended')

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
                if team == 'home':
                    match.home_score += 1
                    match.save()
                    # send a random goal message
                    send_goal_message('home', match)

                    return response_json_with_status_code(200, 'home inc')
                elif team == 'away':
                    match.away_score += 1
                    match.save()
                    # send a random goal message
                    send_goal_message('away', match)

                    return response_json_with_status_code(200, 'away inc')
            elif command == 'dec':
                if team == 'home':
                    if match.home_score > 0:
                        match.home_score -= 1
                        match.save()
                        # send a random goal cancel message
                        send_goal_cancel_message('home', match)

                        return response_json_with_status_code(200, 'home dec')
                    else:
                        return response_json_with_status_code(404, 'cannot dec 0')
                elif team == 'away':
                    if match.away_score > 0:
                        match.away_score -= 1
                        match.save()
                        # send a random goal cancel message
                        send_goal_cancel_message('away', match)

                        return response_json_with_status_code(200, 'away dec')
                    else:
                        return response_json_with_status_code(404, 'cannot dec 0')
        else:
            return response_json_with_status_code(404, 'no active match')

    else:
        return response_json_with_status_code(404, 'missing parameters')
