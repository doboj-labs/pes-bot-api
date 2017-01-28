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


def send_score_message(match):
    sc.api_call(
        "chat.postMessage",
        channel=channel,
        text="Current score is: %s" % (match.get_score())
    )


def start_stop_match_message(match, activity):
    if activity == 'started':
        message = ':loudspeaker: Match has %s! \t*%s* vs *%s*' % (activity, str(match.home), str(match.away))

    elif activity == 'ended':
        message = ':loudspeaker: Match has %s! \t*%s*' % (activity, str(match.get_score()))

    sc.api_call(
        "chat.postMessage",
        channel=channel,
        text=message
    )

    # if its end send next match message
    if activity == 'ended':
        introduce_next_match()


def send_goal_message(goal_getter, match):
    if (goal_getter == 'home'):
        goal_getter = match.home
        goal_receiver = match.away
    elif (goal_getter == 'away'):
        goal_getter = match.away
        goal_receiver = match.home

    random_messages = [
        ":soccer: Goal! *%s* scored! Score: `%s`" % (goal_getter, match.get_score_only_nums())
    ]

    sc.api_call(
        "chat.postMessage",
        channel=channel,
        text=random_messages[randint(0, len(random_messages) - 1)]
    )


def send_goal_cancel_message(goal_getter, match):
    # currently not used!
    if (goal_getter == 'home'):
        goal_getter = match.home
        goal_receiver = match.away
    elif (goal_getter == 'away'):
        goal_getter = match.away
        goal_receiver = match.home

    random_messages = [
        ":bangbang: Goal canceled. Score: `%s`" % (
            match.get_score_only_nums())
    ]

    sc.api_call(
        "chat.postMessage",
        channel=channel,
        text=random_messages[randint(0, len(random_messages) - 1)]
    )


def introduce_next_match():
    next_match = find_active_or_scheduled_match(False)
    message = "No next match!"

    if next_match:
        message = ":fast_forward: Next match: @%s vs @%s" % (next_match.home.slack_name, next_match.away.slack_name)

    sc.api_call(
        "chat.postMessage",
        link_names=1,
        channel=channel,
        text=message
    )


class TournamentViewSet(viewsets.ModelViewSet):
    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer


class MatchViewSet(viewsets.ModelViewSet):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer


# if just_active true will return only active match not scheduled
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
