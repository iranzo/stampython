### Administrator configuration

- owner: owner of bot
- daemon: Run as daemon or one shoot
- maxage: chats older than this will be removed
- cleanup: cleanup tasks periodicity
- sleep: delay between two telegram server checks for messages
- token: auth token against telegram server
- stock: list of stock to check when invoking 'stock'
- verbosity: log level verbosity
- url: URL for telegram server bot api entry point

### User/chat configuration

- common
    - language: en (TODO)
    - currency: EUR
    - modulo: 1 (to just show karma every X/modulo points, 0 to disable)
    - stock: stock tickers to check
    - espp: offering price at start of period for ESPP
- user
    - highlight: set the words in messages that causes the message to be forwarded to you
- chat
    - isolated: False, if true, allow link, all karma, etc is tied to GID
    - link: empty, if defined, channel is slave to a mater
    - admin: List of admins of channels, default empty: everyone

## Donations

The bot runs on my hardware which involves (HW, power, internet, etc), if
you wish to collaborate, please, use <https://www.paypal.me/iranzop> for
your donation.
