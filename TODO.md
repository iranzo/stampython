- Mostly everything :), initial steps are there for accessing URL:
- Consider moving to web-hook for async operation
    - Now it runs in daemon mode, polling every 10 seconds (can be
      changed)
        - Move the 10 seconds to be a maximum, allowing to
         store/retrieve the number of messages in average and adapt to
         time of the day and rate
- Implement having separate karma per group-id to have privacy on the
  topics discussed on each one (no leaks because of karma)
- Initial load of karma points from older bot (possible separate script)
- Implement banning of consecutive karma changes from same user for a
  period of time
- Implement /settings to store settings per chat (be silent, timeout
  for ban, etc)
- Implement 'highlight', so when a bot is in a channel the user is,
  allow that user to get a private notification from bot highlighting
  that word to him. (This should require per-user settings and be
  limited to group chats were user is in (getChatMember and
  https://core.telegram.org/bots/api#forwardmessage)
- Improve message handling so when a user joins/parts a channel the stats 
  table is updated with that event
- Implement something similar to
  <https://supportex.net/blog/2011/09/rrd-python/> for graphing message activity