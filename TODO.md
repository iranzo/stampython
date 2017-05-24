# TODO

- Initial load of karma points from older bot (possible separate script)
- Implement banning of consecutive karma changes from same user for a period of time
- Implement something similar to <https://supportex.net/blog/2011/09/rrd-python/> for graphing message activity
- Implement cron to provide users messages based on schedule
- Create a Business Bingo plugin that allows to define words that participate into the Bingo, keep track of the ones mentioned already and announce bingo Winner (last word completed) and clear the status to start a new round
- Implement i18n to the project to allow users to write strings for the bot and use the channel-configured language (or default to en) for messages.
    - Mostly i18n done, failed to change the language dynamically so far
- Implement autoban so when a certain word is used:
    - kick user out of the channel https://core.telegram.org/bots/api#kickchatmember
    - and unban it (in case of superchannels) so he can join again (or not) https://core.telegram.org/bots/api#unbanchatmember
    - Delete the offending message: https://core.telegram.org/bots/api#deletemessage

## Donations

The bot runs on my hardware which involves (HW, power, internet, etc), if
you wish to collaborate, please, use <https://www.paypal.me/iranzop> for
your donation.
