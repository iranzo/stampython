# Plugin requirements

Each plugin requires to define a 'run' a 'help' and an 'init' function.

Each one of those will be executed on main program start, on the regular
executions (via loop at the moment) or when '/help' is requested as command.

Init returns the list of triggers, so if a trigger is found as the first word
in a line, that plugin will be executed, otherwise, ignored.
  
Returning "*" makes plugin to execute on all messages.