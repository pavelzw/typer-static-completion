# Generated - do not edit.
function __tsc_2a97516c354b6884
    set -l tokens (commandline -xpc)
    set -l node 0
    set -l position 0
    set -l pending 0
    set -l ended 0
    for word in $tokens[2..-1]
        if test $pending -eq 1
            set pending 0
            continue
        end
        if test "$word" = --; and test $ended -eq 0
            set ended 1
            continue
        end
        if string match -qr '^-.+' -- "$word"; and test $ended -eq 0
            set -l flag (string split -m 1 = -- "$word")[1]
            set -l takes -1
if test "$node:$flag" = '0:--profile'; set takes 1; end
if test "$node:$flag" = '0:--verbose'; set takes 0; end
if test "$node:$flag" = '0:--no-verbose'; set takes 0; end
if test "$node:$flag" = '0:--help'; set takes 0; end
if test "$node:$flag" = '1:--color'; set takes 1; end
if test "$node:$flag" = '1:-c'; set takes 1; end
if test "$node:$flag" = '1:--config'; set takes 1; end
if test "$node:$flag" = '1:--directory'; set takes 1; end
if test "$node:$flag" = '1:--cache'; set takes 0; end
if test "$node:$flag" = '1:--no-cache'; set takes 0; end
if test "$node:$flag" = '1:--help'; set takes 0; end
if test "$node:$flag" = '2:--help'; set takes 0; end
if test "$node:$flag" = '3:--help'; set takes 0; end
if test "$node:$flag" = '4:--help'; set takes 0; end
if test "$node:$flag" = '5:--help'; set takes 0; end
if test "$node:$flag" = '6:--help'; set takes 0; end
            if test $takes -ge 0
                if test $takes -eq 1; and not string match -q '*=*' -- "$word"
                    set pending 1
                end
                continue
            end
            if not string match -q -- '--*' "$word"
                set -l rest (string sub -s 2 -- "$word")
                while test -n "$rest"
                    set flag -(string sub -l 1 -- "$rest")
                    set rest (string sub -s 2 -- "$rest")
                    set takes -1
if test "$node:$flag" = '0:--profile'; set takes 1; end
if test "$node:$flag" = '0:--verbose'; set takes 0; end
if test "$node:$flag" = '0:--no-verbose'; set takes 0; end
if test "$node:$flag" = '0:--help'; set takes 0; end
if test "$node:$flag" = '1:--color'; set takes 1; end
if test "$node:$flag" = '1:-c'; set takes 1; end
if test "$node:$flag" = '1:--config'; set takes 1; end
if test "$node:$flag" = '1:--directory'; set takes 1; end
if test "$node:$flag" = '1:--cache'; set takes 0; end
if test "$node:$flag" = '1:--no-cache'; set takes 0; end
if test "$node:$flag" = '1:--help'; set takes 0; end
if test "$node:$flag" = '2:--help'; set takes 0; end
if test "$node:$flag" = '3:--help'; set takes 0; end
if test "$node:$flag" = '4:--help'; set takes 0; end
if test "$node:$flag" = '5:--help'; set takes 0; end
if test "$node:$flag" = '6:--help'; set takes 0; end
                    if test $takes -lt 0
                        return 1
                    end
                    if test $takes -eq 1
                        if test -z "$rest"
                            set pending 1
                        end
                        break
                    end
                end
                continue
            end
            return 1
        end
if test "$node:$word" = '0:deploy'; set node 1; set position 0; set ended 0; continue; end
if test "$node:$word" = '0:tasks'; set node 2; set position 0; set ended 0; continue; end
if test "$node:$word" = '0:tags'; set node 3; set position 0; set ended 0; continue; end
if test "$node:$word" = '0:remote'; set node 4; set position 0; set ended 0; continue; end
if test "$node:$word" = '4:add'; set node 5; set position 0; set ended 0; continue; end
if test "$node:$word" = '4:remove'; set node 6; set position 0; set ended 0; continue; end
        set position (math $position + 1)
    end
    test $node -eq $argv[1]; or return 1
    if test "$argv[2]" = option
        test $ended -eq 0
    else if test $pending -eq 1
        return 1
    else if test "$argv[2]" = command
        test $position -eq 0
    else if test "$argv[2]" = variadic
        test $position -ge $argv[3]
    else
        test $position -eq $argv[2]
    end
end
complete -c 'demo' -f
complete -c 'demo' -n '__tsc_2a97516c354b6884 0 option' -l 'profile' -r -f
complete -c 'demo' -n '__tsc_2a97516c354b6884 0 option' -l 'verbose' -f
complete -c 'demo' -n '__tsc_2a97516c354b6884 0 option' -l 'no-verbose' -f
complete -c 'demo' -n '__tsc_2a97516c354b6884 0 option' -l 'help' -f -d 'Show this message and exit.'
complete -c 'demo' -n '__tsc_2a97516c354b6884 0 command' -f -a '\'deploy\'' -d 'Deploy an application.'
complete -c 'demo' -n '__tsc_2a97516c354b6884 0 command' -f -a '\'tasks\'' -d 'List tasks.'
complete -c 'demo' -n '__tsc_2a97516c354b6884 0 command' -f -a '\'tags\'' -d 'List tags.'
complete -c 'demo' -n '__tsc_2a97516c354b6884 0 command' -f -a '\'remote\''
complete -c 'demo' -n '__tsc_2a97516c354b6884 1 option' -l 'color' -r -f -a '\'red\' \'rose\' \'blue\' \'two words\' \'quote\\\'s\''
complete -c 'demo' -n '__tsc_2a97516c354b6884 1 option' -s 'c' -r -f -a '\'red\' \'rose\' \'blue\' \'two words\' \'quote\\\'s\''
complete -c 'demo' -n '__tsc_2a97516c354b6884 1 option' -l 'config' -r -F
complete -c 'demo' -n '__tsc_2a97516c354b6884 1 option' -l 'directory' -r -f -a '(__fish_complete_directories)'
complete -c 'demo' -n '__tsc_2a97516c354b6884 1 option' -l 'cache' -f
complete -c 'demo' -n '__tsc_2a97516c354b6884 1 option' -l 'no-cache' -f
complete -c 'demo' -n '__tsc_2a97516c354b6884 1 option' -l 'help' -f -d 'Show this message and exit.'
complete -c 'demo' -n '__tsc_2a97516c354b6884 2 option' -l 'help' -f -d 'Show this message and exit.'
complete -c 'demo' -n '__tsc_2a97516c354b6884 3 option' -l 'help' -f -d 'Show this message and exit.'
complete -c 'demo' -n '__tsc_2a97516c354b6884 4 option' -l 'help' -f -d 'Show this message and exit.'
complete -c 'demo' -n '__tsc_2a97516c354b6884 4 command' -f -a '\'add\'' -d 'Add a remote.'
complete -c 'demo' -n '__tsc_2a97516c354b6884 4 command' -f -a '\'remove\'' -d 'Remove a remote.'
complete -c 'demo' -n '__tsc_2a97516c354b6884 5 0 0' -f
complete -c 'demo' -n '__tsc_2a97516c354b6884 5 option' -l 'help' -f -d 'Show this message and exit.'
complete -c 'demo' -n '__tsc_2a97516c354b6884 6 0 0' -f
complete -c 'demo' -n '__tsc_2a97516c354b6884 6 option' -l 'help' -f -d 'Show this message and exit.'
