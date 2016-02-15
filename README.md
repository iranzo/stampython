## Introduction
Attempt to create a python script that monitors a telegram bot URL and replies to commands for adding/removing karma.

Check more information about [Telegram Bots](https://core.telegram.org/bots/).

## Important
- The bot will need to have access to all of your messages in order to find the words with "++" or "--"

## Notes
- On first execution it will create database and start filling values

## Test
- I've a copy running on <openshift.redhat.com> at <http://stampy-iranzo.rhcloud.com/> with the name `@redken_bot`. Invite it to your channels if you want to give it a try or click <https://telegram.me/redken_bot>.

## Usage
- `word++` to add karma
- `word--` to remove karma
- `/quote add username text` to add a quote for given username with the following text as message
- `/quote username` to retrieve a random quote for that username.


## Extra commands only for owner user
### Configuration
The bot, once token has been used and owner set via commandline, will store that information in the database, so you can control it from a chat window

- `/config show` will list actual defined settings
- `/config set var=value` will set one of those settings with a new value
    - As of this writing (verbosity, url for api, token, sleep timeout, owner, database, run in daemon mode)

### Stats
The bot stores stats on users/chats, remembering the chat/user name and last time seen so it can be later used for purging data not being accessed in a while
- `/stats show (user|chat)` will list the list of users/chats and time of last update

### Alias
Bot allows to setup alias, so when karma is given to a word, it will instead add it to a different one (and report that one)
- `/alias key=value` Will create a new alias, so each time `key++` is used, it will instead do value++
    - This operation, sums the previous karma of `key` and `value` and stores it in value so no karma is lost
    - Recursive aliases can be defined, so doing:
        - `/alias lettuce=vegetable`
        - `/alias vegetable=food`
        - `lettuce++` will give karma to `food`.
- `/alias list` Will show current defined aliases
- `/alias delete key` will delete a previously defined alias so each word gets karma on its own

### quote
- `/quote del id` to remove a specific quote id from database
