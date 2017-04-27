### web hook
    - Mostly everything :), initial steps are there for accessing URL:
    - Consider moving to web-hook for async operation
        - Now it runs in daemon mode, polling every 10 seconds (can be
          changed)
            - Move the 10 seconds to be a maximum, allowing to
             store/retrieve the number of messages in average and adapt to
             time of the day and rate

### Other
    - Initial load of karma points from older bot (possible separate script)
    - Implement banning of consecutive karma changes from same user for a
      period of time
    - Implement something similar to
      <https://supportex.net/blog/2011/09/rrd-python/> for graphing message
      activity
    - Implement cron to provide users messages based on schedule
    - Create a Business Bingo plugin that allows to define words that
      participate into the Bingo, keep track of the ones mentioned already
      and announce bingo Winner (last word completed) and clear the status
      to start a new round
    - Implement i18n to the project to allow users to write strings for the
      bot and use the channel-configured language (or default to en) for 
      messages.
      - Mostly i18n done, failed to change the language dynamically so far