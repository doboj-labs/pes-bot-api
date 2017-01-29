# pes-bot-api

## About

This app is for managing and live streaming(commenting as a bot in our pes chanel) or pes tournaments.<br>
It is controlled by our [arduino device](https://github.com/doboj-labs/pes-arduino)

## Usage
Use django admin panel to insert all the match games our tournament has.<br>
After starting the match on pes4 players start the arduino device and push start the game button.<br>
Bot notifies us all in a channel that the game has started.<br>
Every time some one scores a goal he has to press the score goal button on arduino and our bot notifies<br>
us about the score in our pes chanel<br>
When the match is finished press stop button on arduino and bot will notify us that the match is over<br>
and tag slack users that are supposed to play the next match.
It is possible to correct the score by canceling a goal using arduino cancel goal button.

Live stream example example:
![Live stream example](/static/comment_example.png)

