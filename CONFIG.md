### Administrator configuration

- owner: owner of bot
- daemon: Run as daemon or one shoot
- cleanup: cleanup tasks periodicity
- sleep: delay between two telegram server checks for messages
- token: auth token against telegram server
- stock: list of stock to check when invoking 'stock'
- verbosity: log level verbosity
- url: URL for telegram server bot api entry point

### User/chat configuration

- common
    - language: en|es
    - currency: EUR
    - modulo: 1 (to just show karma every X/modulo points, 0 to disable)
    - stock: stock tickers to check
    - espp: offering price at start of period for ESPP
- chat
    - isolated: False, if true, allow link, all karma, etc is tied to GID
    - link: empty, if defined, channel is slave to a mater
    - admin: List of admins of channels, default empty: everyone
    - maxage: chats older than this will be removed
    - silent: makes stampy not to output messages to that chat
    - welcome: outputs the text when a new user joins the chat, replacing "$username" by user name

## Donations

The bot runs on my hardware which involves (HW, power, internet, etc), if
you wish to collaborate, please, use <https://www.paypal.me/iranzop> for
your donation.
