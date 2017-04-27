# Stampython: A Telegram bot for karma accounting

[![Build Status](https://travis-ci.org/iranzo/stampython.svg?branch=master)](https://travis-ci.org/iranzo/stampython)
[![Code Climate](https://codeclimate.com/github/iranzo/stampython/badges/gpa.svg)](https://codeclimate.com/github/iranzo/stampython)
[![Pypi](http://img.shields.io/pypi/v/stampython.svg)](https://pypi.python.org/pypi/stampython/)

## Introduction
Attempt to create a python script that monitors a telegram bot URL and replies to commands for adding/removing karma.

Check more information about [Telegram Bots](https://core.telegram.org/bots/).

News about the program, new features, etc at <https://telegram.me/stampynews>.

## Important
- The bot will need to have access to all of your messages in order to find the words with "++" or "--"

## Notes
- On first execution it will create database and start filling values

## Test
- I've a copy running the name `@redken_bot`. Invite it to your channels if you want to give it a try or click <https://telegram.me/redken_bot>.

## Usage
- `word++` to add karma
- `word--` to remove karma
- `/quote add username text` to add a quote for given username with the following text as message
- `/quote username` to retrieve a random quote for that username.
- `/dilbert <date>` to retrieve Dilbert's strip for today or supplied date (today if error parsing)
- `/mel <date>` to retrieve Mel's strip for today or supplied date (today 
  or prior days as data is obtained from RSS feed)
- `/obichero <date>` to retrieve O bichero's strip for today or supplied date 
  (today or prior days as data is obtained from RSS feed)  
- `/quico <date>` to retrieve Quico Jubilata's strip for today or supplied
  date
- `/xkcd <date>` to retrieve XKCD's strip for today or supplied
  date
- `/jueves <date>` to retrieve El Jueves strip for today or supplied  date
  
- `@all` to ping all usernames for users in a channel
- `@all++` to give karma to all usernames in a channel
- `stock <ticker>` to get trading quote for ticker in stock market
- `/espp <amount>` to get earning calculations based on stock defined and monthly rate (for 6 months)
- `/hilight <add|delete|list> <word>` Adds/deletes word or lists words that will cause a forward to notify you

## Extra commands only for admin user
### Configuration
The bot, once token has been used and admin has been set, will store that information in the database, so you can control it from a chat window

- `/gconfig show` will list actual defined settings
- `/gconfig set var=value` will set one of those settings with a new value
    - As of this writing (verbosity, url for api, token, sleep timeout, owner, database, run in daemon mode)
- `/gconfig delete var` will delete that variable from configuration.


## Extra commands only for owner user
### Configuration
The bot, once token has been used and owner set via commandline, will store that information in the database, so you can control it from a chat window

- `/config show` will list actual defined settings
- `/config set var=value` will set one of those settings with a new value
    - As of this writing (verbosity, url for api, token, sleep timeout, owner, database, run in daemon mode)
- `/config delete var` will delete that variable from configuration.

### Stats
The bot stores stats on users/chats, remembering the chat/user name and last time seen so it can be later used for purging data not being accessed in a while
- `/stats show (user|chat)` will list the list of users/chats and time of last update

### Karma
- `/skarma word=value` will set specified word to the karma value provided.

### Auto-karma triggers
Bot allows to trigger auto-karma events, so when keyword is given, it will trigger an event to increase karma value for other words
- `/autok key=value` Will create a new auto-karma trigger, so each time `key` is used, it will trigger value++ event
- `/alias list [word]` Will show current defined autokarma triggers and in case a word is provided will search based on that word
- `/alias delete key=value` will delete a previously defined auto-karma so no more auto-karma events will be triggered for that pair


### Forward
- `/forward source_id=target_id` Forwards messages from source to target
- `/forward delete source_id=target_id` Stops forwarding messages from source to target
- `/forward list` To get list of defined forwards

### Alias
Bot allows to setup alias, so when karma is given to a word, it will instead add it to a different one (and report that one)
- `/alias key=value` Will create a new alias, so each time `key++` is used, it will instead do value++
    - This operation, sums the previous karma of `key` and `value` and stores it in value so no karma is lost
    - Recursive aliases can be defined, so doing:
        - `/alias lettuce=vegetable`
        - `/alias vegetable=food`
        - `lettuce++` will give karma to `food`.
    - Alias can be defined to groups of words so, it can be defined to have:
        - `/alias friday=tgif tfsmif`
        - `friday++` will increase karma on `tgif` and `tfsmif`.
- `/alias list` Will show current defined aliases
- `/alias delete key` will delete a previously defined alias so each word gets karma on its own

### quote
- `/quote del id` to remove a specific quote id from database


### quit
- `/quit` will exit daemon mode


## Donations

The bot runs on my hardware which involves (HW, power, internet, etc), if
you wish to collaborate, please, use <https://www.paypal.me/iranzop> for
your donation.
