from .services import response_json_with_status_code
from rest_framework.decorators import api_view
from django.shortcuts import render
from rest_framework import viewsets
from api.serializers import TournamentSerializer, MatchSerializer
from api.models import Tournament, Match, MatchStatus

from slackclient import SlackClient
import os
from random import randint

slack_token = os.environ["SLACK_API_TOKEN"]
sc = SlackClient(slack_token)
channel = os.environ['SLACK_CHANNEL']


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


def send_goal_message(goal_getter, match):
    # find out who scored home or away
    if (goal_getter == 'home'):
        goal_getter = match.home
        goal_receiver = match.away
    elif (goal_getter == 'away'):
        goal_getter = match.away
        goal_receiver = match.home

    # currently only one message showing only goal getter
    random_messages = [
        ":soccer: Goal! *%s* scored! Score: `%s`" % (goal_getter, match.get_score_only_nums())
    ]

    sc.api_call(
        "chat.postMessage",
        channel=channel,
        text=random_messages[randint(0, len(random_messages) - 1)]
    )


def send_goal_cancel_message(goal_getter, match):
    # find out who scored home or away
    if (goal_getter == 'home'):
        goal_getter = match.home
        goal_receiver = match.away
    elif (goal_getter == 'away'):
        goal_getter = match.away
        goal_receiver = match.home

    # currently only one message not even showing who canceled the goal
    random_messages = [
        ":bangbang: Goal canceled. Score: `%s`" % (
            match.get_score_only_nums())
    ]

    sc.api_call(
        "chat.postMessage",
        channel=channel,
        text=random_messages[randint(0, len(random_messages) - 1)]
    )


class TournamentViewSet(viewsets.ModelViewSet):
    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer


class MatchViewSet(viewsets.ModelViewSet):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer


# if just_active true method will return only active match not scheduled
def find_active_or_scheduled_match(just_active):
    match = None

    # try finding active match
    try:
        match = Match.objects.filter(status=MatchStatus.active).order_by('id')[0]
        # if just active wonted return here and do not search for scheduled
        if just_active:
            if match:
                return match
    # if no active match find scheduled
    except:
        try:
            if not just_active:
                match = Match.objects.filter(status=MatchStatus.scheduled).order_by('id')[0]
        except:
            pass

    return match


# Find next match if exists
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


# start new match if no active found and there are scheduled matches
# stop match if there is active match
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


# increment and decrement scores of an active match
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


def main_web(request):
    next_match = find_active_or_scheduled_match(False)

    return render(request, 'base.html', {"next_match": next_match})


def show_all_matches(request):
    matches = Match.objects.all().order_by('id')
    print(matches)
    return render(request, 'matches.html', {"matches": matches})
