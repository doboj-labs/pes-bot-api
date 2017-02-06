from slackbot.bot import Bot
from slackbot.bot import respond_to, listen_to
import re
from api.views import find_active_or_scheduled_match


@respond_to('next match', re.IGNORECASE)
def check_toilet_status(message):
    next_match = find_active_or_scheduled_match(False)
    if next_match:
        message.reply("%s vs %s" % (next_match.home, next_match.away))
    message.reply("Dude some shit happened could not reach the server!")


@respond_to('hi', re.IGNORECASE)
def hi(message):
    message.reply('Hello')


@respond_to('help', re.IGNORECASE)
def help_replay(message):
    message.reply("Hi I am pes bot.")
    message.reply("To check for next match type `next match` to me or tag me at channel with that message.")


def main():
    bot = Bot()
    bot.run()


if __name__ == "__main__":
    main()
