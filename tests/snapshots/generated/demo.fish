# Generated - do not edit.
function __tsc_2a97516c354b6884_option
if test "$argv[1]:$argv[2]" = '0:--profile'; printf "%s\n" 0 1; return; end
if test "$argv[1]:$argv[2]" = '0:--verbose'; printf "%s\n" 1 0; return; end
if test "$argv[1]:$argv[2]" = '0:--no-verbose'; printf "%s\n" 1 0; return; end
if test "$argv[1]:$argv[2]" = '0:--help'; printf "%s\n" 2 0; return; end
if test "$argv[1]:$argv[2]" = '1:--color'; printf "%s\n" 3 1; return; end
if test "$argv[1]:$argv[2]" = '1:-c'; printf "%s\n" 3 1; return; end
if test "$argv[1]:$argv[2]" = '1:--config'; printf "%s\n" 4 1; return; end
if test "$argv[1]:$argv[2]" = '1:--directory'; printf "%s\n" 5 1; return; end
if test "$argv[1]:$argv[2]" = '1:--cache'; printf "%s\n" 6 0; return; end
if test "$argv[1]:$argv[2]" = '1:--no-cache'; printf "%s\n" 6 0; return; end
if test "$argv[1]:$argv[2]" = '1:--help'; printf "%s\n" 7 0; return; end
if test "$argv[1]:$argv[2]" = '2:--help'; printf "%s\n" 8 0; return; end
if test "$argv[1]:$argv[2]" = '3:--help'; printf "%s\n" 9 0; return; end
if test "$argv[1]:$argv[2]" = '4:--help'; printf "%s\n" 10 0; return; end
if test "$argv[1]:$argv[2]" = '5:--help'; printf "%s\n" 12 0; return; end
if test "$argv[1]:$argv[2]" = '6:--help'; printf "%s\n" 14 0; return; end
    printf '%s\n' -1 0
end

function __tsc_2a97516c354b6884
    set -l tokens (commandline -xpc)
    set -l current (commandline -ct)
    set -l unescaped (string unescape -- "$current")
    if test (count $unescaped) -eq 1
        set current "$unescaped"
    end
    set -l node 0
    set -l position 0
    set -l pending -1
    set -l ended 0
    for word in $tokens[2..-1]
        if test $pending -ge 0
            set pending -1
            continue
        end
        if test "$word" = --; and test $ended -eq 0
            set ended 1
            continue
        end
        if string match -qr '^-.+' -- "$word"; and test $ended -eq 0
            set -l flag (string split -m 1 = -- "$word")[1]
            set -l info (__tsc_2a97516c354b6884_option $node "$flag")
            if test $info[1] -ge 0
                if test $info[2] -eq 1; and not string match -q '*=*' -- "$word"
                    set pending $info[1]
                end
                continue
            end
            if not string match -q -- '--*' "$word"
                set -l rest (string sub -s 2 -- "$word")
                while test -n "$rest"
                    set flag -(string sub -l 1 -- "$rest")
                    set rest (string sub -s 2 -- "$rest")
                    set info (__tsc_2a97516c354b6884_option $node "$flag")
                    if test $info[1] -lt 0
                        return
                    end
                    if test $info[2] -eq 1
                        if test -z "$rest"
                            set pending $info[1]
                        end
                        break
                    end
                end
                continue
            end
            return
        end
if test "$node:$word" = '0:deploy'; set node 1; set position 0; set ended 0; continue; end
if test "$node:$word" = '0:tasks'; set node 2; set position 0; set ended 0; continue; end
if test "$node:$word" = '0:tags'; set node 3; set position 0; set ended 0; continue; end
if test "$node:$word" = '0:remote'; set node 4; set position 0; set ended 0; continue; end
if test "$node:$word" = '4:add'; set node 5; set position 0; set ended 0; continue; end
if test "$node:$word" = '4:remove'; set node 6; set position 0; set ended 0; continue; end
        switch $node
case 0; return
case 4; return
        end
        set position (math $position + 1)
    end
    set -l target $pending
    set -l prefix ''
    set -l candidates
    set -l descriptions
    set -l file_mode ''
    if test $target -lt 0; and test $ended -eq 0
        if string match -q -- '--*=*' "$current"
            set -l parts (string split -m 1 = -- "$current")
            set -l info (__tsc_2a97516c354b6884_option $node "$parts[1]")
            test $info[2] -eq 1; or return
            set target $info[1]
            set prefix "$parts[1]="
            set current "$parts[2]"
        else if string match -qr '^-[^-].*' -- "$current"
            set -l rest (string sub -s 2 -- "$current")
            set -l attached -
            while test -n "$rest"
                set -l flag -(string sub -l 1 -- "$rest")
                set attached "$attached"(string sub -l 1 -- "$rest")
                set rest (string sub -s 2 -- "$rest")
                set -l info (__tsc_2a97516c354b6884_option $node "$flag")
                if test $info[1] -lt 0
                    break
                end
                if test $info[2] -eq 1
                    set target $info[1]
                    set prefix "$attached"
                    set current "$rest"
                    break
                end
            end
        end
    end
    if test $target -lt 0
        switch $node
case 0
set candidates 'deploy' 'tasks' 'tags' 'remote'
set descriptions 'Deploy an application.' 'List tasks.' 'List tags.' ''
if test $ended -eq 0; and string match -q -- '-*' "$current"
set candidates '--profile' '--verbose' '--no-verbose' '--help'
set descriptions '' '' '' 'Show this message and exit.'
end
case 1
set candidates
set descriptions
if test $ended -eq 0; and string match -q -- '-*' "$current"
set candidates '--color' '-c' '--config' '--directory' '--cache' '--no-cache' '--help'
set descriptions '' '' '' '' '' '' 'Show this message and exit.'
end
case 2
set candidates
set descriptions
if test $ended -eq 0; and string match -q -- '-*' "$current"
set candidates '--help'
set descriptions 'Show this message and exit.'
end
case 3
set candidates
set descriptions
if test $ended -eq 0; and string match -q -- '-*' "$current"
set candidates '--help'
set descriptions 'Show this message and exit.'
end
case 4
set candidates 'add' 'remove'
set descriptions 'Add a remote.' 'Remove a remote.'
if test $ended -eq 0; and string match -q -- '-*' "$current"
set candidates '--help'
set descriptions 'Show this message and exit.'
end
case 5
set candidates
set descriptions
if test $ended -eq 0; and string match -q -- '-*' "$current"
set candidates '--help'
set descriptions 'Show this message and exit.'
end
case 6
set candidates
set descriptions
if test $ended -eq 0; and string match -q -- '-*' "$current"
set candidates '--help'
set descriptions 'Show this message and exit.'
end
        end
        if test $ended -eq 1; or not string match -q -- '-*' "$current"
if test $node -eq 5; and test $position -eq 0; set target 11; end
if test $node -eq 6; and test $position -eq 0; set target 13; end
        end
    end
    if test $target -ge 0
        set candidates
        set descriptions
        switch $target
case 0; set candidates
case 1; set candidates
case 2; set candidates
case 3; set candidates 'red' 'rose' 'blue' 'two words' 'quote\'s'
case 4; set file_mode file
case 5; set file_mode directory
case 6; set candidates
case 7; set candidates
case 8; set candidates
case 9; set candidates
case 10; set candidates
case 11; set candidates
case 12; set candidates
case 13; set candidates
case 14; set candidates
        end
    end
    set -l index 1
    for candidate in $candidates
        printf '%s\t%s\n' "$prefix$candidate" "$descriptions[$index]"
        set index (math $index + 1)
    end
    if test -n "$file_mode"
        set -l escaped (string escape -- "$current")
        set -l paths
        if test "$file_mode" = directory
            set paths (__fish_complete_directories "$escaped")
        else
            set paths (__fish_complete_path "$escaped")
        end
        for candidate in $paths
            printf '%s\n' "$prefix$candidate"
        end
    end
end
complete -c 'demo' -f -a '(__tsc_2a97516c354b6884)'
