# User guide

## Introduction

After reading [Readme.md](Readme.md) that contains more 'how-to-run' information, it might be interesting for you to learn about how to use it.

In short, many options are documented by sending "/help" on a channel where <https://t.me/redken_bot> is.

By default, new groups where the bot is added are just ready to start being used.

Also, while nothing is set against, you could use `/gconfig` to configure  several aspects of it like:

- `modulo` (to just report karma every `modulo` points)
- `stock` (to define the stock tickers to query when invoking `stock`)

Once you started chatting with the bot, you can also use /hilight `word` so messages containing that word will be forwarded to you as a private message.

By default karma in channels is private to that group, but also, groups can be linked.

On the channel to become `master` execute: `/admin link master` and it will generate a code (token) to link against just once.

On the channel to be linked against `master`, a.k.a. `slave`, execute: `/admin link slave <token>` where `token` is the code received as reply to the command in master channel.

Also, as per general usage:

- `word++` to add karma
- `word--` to remove karma
- reply to message with '++', '--' or '==' to add or remove karma to user of prior message or to the same words that were used
- `/quote add username text` to add a quote for given username with the following text as message
- `/quote username` to retrieve a random quote for that username.
- `/comic list` to list all knwon comic strips
- `/comic <comic>` to retrieve `comic` strip for today
- `/comic all` to retrieve all of today's comic strips
- `@all` to ping all usernames for users in a channel
- `@all++` to give karma to all usernames in a channel
- `stock <ticker>` to get trading quote for ticker in stock market
- `/espp <amount>` to get earning calculations based on stock defined and monthly rate (for 6 months)
- `/hilight <add|delete|list> <word>` Adds/deletes word or lists words that will cause a forward to notify you
- `/feed add name url` Adds a new feed form URL on channel
- `/feed delete feed` Removes feed from channel
- `/feed list` To get list of defined feeds
- `/feed feed` To get that feed updates
- `/cn` To get a random Chuck Norris fact


## Extra commands only for admin user

### Configuration

The bot, once token has been used and admin has been set, will store that information in the database, so you can control it from a chat window

- `/[g|l]config show` will list actual defined settings
- `/[g|l]config set var=value` will set one of those settings with a new value
    - As of this writing (verbosity, url for api, token, sleep timeout, owner, database, run in daemon mode)
- `/[g|l]config delete var` will delete that variable from configuration.

### Karma

- `/skarma word=value` will set specified word to the karma value provided.

### Auto-karma triggers

Bot allows to trigger auto-karma events, so when keyword is given, it will trigger an event to increase karma value for other words

- `/autok key=value` Will create a new auto-karma trigger, so each time `key` is used, it will trigger value++ event
- `/alias list [word]` Will show current defined autokarma triggers and in case a word is provided will search based on that word
- `/alias delete key=value` will delete a previously defined auto-karma so no more auto-karma events will be triggered for that pair

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

## Donations

The bot runs on my hardware which involves (HW, power, internet, etc), if you wish to collaborate, please, use <https://www.paypal.me/iranzop> for your donation.
