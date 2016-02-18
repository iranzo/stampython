- Mostly everything :), initial steps are there for accessing URL:

- Consider moving to web-hook for async operation
    - Now it runs in daemon mode, polling every 10 seconds
- Consider having separate karma per group-id to have privacy on the topics discussed on each one (no leaks because of karma)
- Initial load of karma points from older bot (possible separate script)
- Implement banning of consecutive karma changes from same user for a period of time
    - Implement /settings to store settings per chat [be silent, timeout for ban, etc]
- Implement deletion of old stats for users/groups to not clutter database
