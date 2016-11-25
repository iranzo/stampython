# Plugin requirements

Each plugin requires to define a 'run' a 'help' and an 'init' function.

Each one of those will be executed on main program start, on the regular
executions (via loop at the moment) or when '/help' is requested as command.
