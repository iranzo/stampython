### web hook
    - Mostly everything :), initial steps are there for accessing URL:
    - Consider moving to web-hook for async operation
        - Now it runs in daemon mode, polling every 10 seconds (can be
          changed)
            - Move the 10 seconds to be a maximum, allowing to
             store/retrieve the number of messages in average and adapt to
             time of the day and rate

### Private group support
  - TODO:
    - Define basic/default configuration to be applied to all new channels 
    and versioning, so once a new default is required, if missing, define
     it or inherit from global config
    - Define config preference between user/chat/general
    - Review whole config usage to separate between master admin and channel
      admin and determine operations valid for one or both

    - Create settings to store chat-specific values in a consistent way
        - Limit settings that can be defined (keys) for group admins
            - common
                - language: en (TODO)
                - currency: EUR (DONE)
                - modulo (to just show karma every X points)
                    - Set to '0' to just show stampy  (DONE)
                - stock (DONE)
                - espp (DONE
            - chats
                - isolated: False, if true, allow link
                    - link: Empty, if defined, use the target gid for karma, alias, admin, etc
                - admin: ''
                    - Allow group without 'admin' to get owned
                    - If user with 'alias' no longer in group, moved to 
                    unadmin
                - link
                    - create commands for link, ack link, unlink, show links (DONE)
                  - Allow prior admin of channel to 'unlink' while  
                  duplicating karma/alias, etc
            - users
                - highlight
    
    - Define behavior when two channels are
        - linked
            - Merge karma, quote, alias, autok or ignore from slave?
        - unlinked
            - Copy karma, quote, alias, autok from master or start clean
        - operations
            - unlink: prior admin or admin from group
            - if admin is no longer listed, autoremove
    - Modify karma commands and database for group operation
    - Modify quote commands and database for group operation
    - Modify alias commands and database for group operation
    - Modify autok commands and database for group operation
      
### Other
    - Initial load of karma points from older bot (possible separate script)
    - Implement banning of consecutive karma changes from same user for a
      period of time
    - Implement 'highlight', so when a bot is in a channel the user is,
      allow that user to get a private notification from bot highlighting
      that word to him. (This should require per-user settings and be
      limited to group chats were user is in (getChatMember and
      https://core.telegram.org/bots/api#forwardmessage)
        - Doesn't work to send messages directly to users if they haven't 
          started a chat with the bot previously
    - Implement something similar to
      <https://supportex.net/blog/2011/09/rrd-python/> for graphing message
      activity
    - Implement cron to provide users messages based on schedule
    - Create a Business Bingo plugin that allows to define words that
      participate into the Bingo, keep track of the ones mentioned already
      and announce bingo Winner (last word completed) and clear the status
      to start a new round
    - Implement forward conditions so just some messages based on sender, or
      text are sent
    - Implement i18n to the project to allow users to write strings for the 
      bot and use the channel-configured language (or default to en) for 
      messages.
      - Mostly i18n done, failed to change the language dynamically so far
    - Fix ESPP so it might have several periods or stocks
    - Fix ESPP so it might have several discounts
