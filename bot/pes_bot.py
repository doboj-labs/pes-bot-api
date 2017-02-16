from slackbot.bot import Bot
from slackbot.bot import respond_to, listen_to
import re, requests
import json


@respond_to('next', re.IGNORECASE)
def check_next_match(message):
    next_match = requests.get('https://doboj-labs-pes-api.herokuapp.com/get-next-match')
    next_match.json()
    next_match = json.loads(next_match.text)
    next_match = next_match['response']['match']
    if next_match:
        message.send(':arrow_right: Next match: %s' % next_match)
    else:
        message.reply("Could not reach server!")


@respond_to('hi', re.IGNORECASE)
def hi(message):
    message.reply('Hello')


@respond_to('help', re.IGNORECASE)
def help_replay(message):
    message.reply(
        "Hi I am pes bot.\nHere is the list of commands:\n`next` to find out who plays next\n`table` to check the current ranking\n`my turn` to check when you play next\n`schedule` to check your schedule till the end of the tournament")


@respond_to('table', re.IGNORECASE)
def table(message):
    table = requests.get('https://doboj-labs-pes-api.herokuapp.com/table-api')
    table = table.json()
    table = table['response']

    if table:
        bot_response = ""
        counter = 1
        for profile in table:
            bot_response += "%d | %s (%d)" % (counter, profile['slack_name'], profile['points'])
            bot_response += "\n"
            counter += 1
        bot_response += "For more detailed table, visit https://doboj-labs-pes-api.herokuapp.com/table"
        message.send(bot_response)
    else:
        message.reply("Could not reach server!")


@respond_to('my turn', re.IGNORECASE)
def next_me(message):
    matches=get_matches()

    if matches:
        username = message.channel._client.users[message.body['user']][u'name']
        counter = 0
        first_active = matches[0]['status'] == "active"
        number_icons = [':zero:', ':one:', ':two:', ':three:', ':four:', ':five:', ':six:', ':seven:', ':eight:',
                        ':nine:', ':keycap_ten:']
        match_queue = ""

        for match in matches:
            if match['slack_name_home'] == username or match['slack_name_away'] == username:
                opponent = match['slack_name_away'] if match['slack_name_home'] == username else match[
                    'slack_name_home']
                break
            else:
                match_queue += "\n"
                match_queue += match['slack_name_home']
                match_queue += " - "
                match_queue += match['slack_name_away']
                counter += 1

        if counter == 0 and first_active:
            message.reply("You are actually playing at the moment. Why are you asking me this?")
        elif counter == 0 and not first_active:
            message.reply(":arrow_right: You are next, what are you waiting??? Your opponent is %s." % (opponent))
        elif counter == 1 and first_active:
            message.reply(":soon: Guys will finish current game soon, prepare for a match with %s." % (opponent))
        else:
            if counter > len(number_icons):
                message.reply("%d match(es) before you:%s\nYou play against *%s*\nFor more details visit https://doboj-labs-pes-api.herokuapp.com/matches" % (counter, match_queue, opponent))
            else:
                message.reply("%s match(es) before you:%s\nYou play against *%s*\nFor more details visit https://doboj-labs-pes-api.herokuapp.com/matches" % (number_icons[counter], match_queue,opponent))
    else:
        message.reply("No matches!")

@respond_to('schedule', re.IGNORECASE)
def my_opponents(message):
    matches=get_matches()

    if matches:
        username = message.channel._client.users[message.body['user']][u'name']
        opponents_queue = ""

        for match in matches:
            if match['slack_name_home'] == username or match['slack_name_away'] == username:
                opponents_queue+=match['slack_name_away'] if match['slack_name_home'] == username else match[
                    'slack_name_home']
                opponents_queue+="\n"
        
        message.reply(":crossed_swords: Your schedule:\n%s" %(opponents_queue))
           
    else:
        message.reply("No matches!")


def get_matches():
    matches = requests.get('https://doboj-labs-pes-api.herokuapp.com/next-matches-api')
    matches = matches.json()
    matches = matches['response']
    return matches

def main():
    bot = Bot()
    bot.run()


if __name__ == "__main__":
    main()
