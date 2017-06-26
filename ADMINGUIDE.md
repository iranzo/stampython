# Owner guide

Some of the following commands  are available for admins of a group or set of groups. Check [USERGUIDE.md](USERGUIDE.md) for commands available to all users.

## Configuration

The bot, once token has been used and owner set via commandline, will store that information in the database, so you can control it from a chat window

- `/config show` will list actual defined settings
- `/config set var=value` will set one of those settings with a new value
    - As of this writing (verbosity, url for api, token, sleep timeout, owner, database, run in daemon mode)
- `/config delete var` will delete that variable from configuration.

## Stats

The bot stores stats on users/chats, remembering the chat/user name and last time seen so it can be later used for purging data not being accessed in a while

- `/stats show (user|chat)` will list the list of users/chats and time of last update


## Feed

- `/feed add name url` Adds a new feed form URL on channel
- `/feed delete feed` Removes feed from channel
- `/feed list` To get list of defined feeds
- `/feed feed` To get that feed updates

## Forward

- `/forward source_id=target_id` Forwards messages from source to target
- `/forward delete source_id=target_id` Stops forwarding messages from source to target
- `/forward list` To get list of defined forwards

## Sudo
- `/sudo gid=<gid>` sets gid to act as, allows later to run:
- `/sudo <command>` where <command> might be like for example `/hilight list`

## quit

- `/quit` will exit daemon mode

## Donations

The bot runs on my hardware which involves (HW, power, internet, etc), if
you wish to collaborate, please, use <https://www.paypal.me/iranzop> for
your donation.
