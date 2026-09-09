# Generated - do not edit.
function __tsc_2a97516c354b6884_option
if test "$argv[1]:$argv[2]" = '0:--target'; printf "%s\n" 0 1; return; end
if test "$argv[1]:$argv[2]" = '0:-t'; printf "%s\n" 0 1; return; end
if test "$argv[1]:$argv[2]" = '0:--token'; printf "%s\n" 1 1; return; end
if test "$argv[1]:$argv[2]" = '0:-k'; printf "%s\n" 1 1; return; end
if test "$argv[1]:$argv[2]" = '0:--verbose'; printf "%s\n" 2 0; return; end
if test "$argv[1]:$argv[2]" = '0:-v'; printf "%s\n" 2 0; return; end
if test "$argv[1]:$argv[2]" = '0:--root-only'; printf "%s\n" 3 0; return; end
if test "$argv[1]:$argv[2]" = '0:--no-root-only'; printf "%s\n" 3 0; return; end
if test "$argv[1]:$argv[2]" = '0:--help'; printf "%s\n" 4 0; return; end
if test "$argv[1]:$argv[2]" = '1:--target'; printf "%s\n" 7 1; return; end
if test "$argv[1]:$argv[2]" = '1:-t'; printf "%s\n" 7 1; return; end
if test "$argv[1]:$argv[2]" = '1:--color'; printf "%s\n" 8 1; return; end
if test "$argv[1]:$argv[2]" = '1:-c'; printf "%s\n" 8 1; return; end
if test "$argv[1]:$argv[2]" = '1:--tag'; printf "%s\n" 9 1; return; end
if test "$argv[1]:$argv[2]" = '1:-g'; printf "%s\n" 9 1; return; end
if test "$argv[1]:$argv[2]" = '1:--token'; printf "%s\n" 10 1; return; end
if test "$argv[1]:$argv[2]" = '1:-k'; printf "%s\n" 10 1; return; end
if test "$argv[1]:$argv[2]" = '1:--verbose'; printf "%s\n" 11 0; return; end
if test "$argv[1]:$argv[2]" = '1:-v'; printf "%s\n" 11 0; return; end
if test "$argv[1]:$argv[2]" = '1:--quiet'; printf "%s\n" 12 0; return; end
if test "$argv[1]:$argv[2]" = '1:-q'; printf "%s\n" 12 0; return; end
if test "$argv[1]:$argv[2]" = '1:--help'; printf "%s\n" 13 0; return; end
if test "$argv[1]:$argv[2]" = '2:--target'; printf "%s\n" 14 1; return; end
if test "$argv[1]:$argv[2]" = '2:-t'; printf "%s\n" 14 1; return; end
if test "$argv[1]:$argv[2]" = '2:--help'; printf "%s\n" 15 0; return; end
if test "$argv[1]:$argv[2]" = '3:--target'; printf "%s\n" 18 1; return; end
if test "$argv[1]:$argv[2]" = '3:-t'; printf "%s\n" 18 1; return; end
if test "$argv[1]:$argv[2]" = '3:--color'; printf "%s\n" 19 1; return; end
if test "$argv[1]:$argv[2]" = '3:-c'; printf "%s\n" 19 1; return; end
if test "$argv[1]:$argv[2]" = '3:--tag'; printf "%s\n" 20 1; return; end
if test "$argv[1]:$argv[2]" = '3:-g'; printf "%s\n" 20 1; return; end
if test "$argv[1]:$argv[2]" = '3:--token'; printf "%s\n" 21 1; return; end
if test "$argv[1]:$argv[2]" = '3:-k'; printf "%s\n" 21 1; return; end
if test "$argv[1]:$argv[2]" = '3:--verbose'; printf "%s\n" 22 0; return; end
if test "$argv[1]:$argv[2]" = '3:-v'; printf "%s\n" 22 0; return; end
if test "$argv[1]:$argv[2]" = '3:--quiet'; printf "%s\n" 23 0; return; end
if test "$argv[1]:$argv[2]" = '3:-q'; printf "%s\n" 23 0; return; end
if test "$argv[1]:$argv[2]" = '3:--help'; printf "%s\n" 24 0; return; end
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
    set -l remaining 0
    set -l ended 0
    for word in $tokens[2..-1]
        if test $pending -ge 0
            set remaining (math $remaining - 1)
            if test $remaining -gt 0
                set pending (math $pending + 1)
            else
                set pending -1
            end
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
                set -l consumed 0
                string match -q '*=*' -- "$word"; and set consumed 1
                set remaining (math $info[2] - $consumed)
                if test $remaining -gt 0
                    set pending (math $info[1] + $consumed)
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
                    if test $info[2] -gt 0
                        set -l consumed 0
                        test -n "$rest"; and set consumed 1
                        set remaining (math $info[2] - $consumed)
                        if test $remaining -gt 0
                            set pending (math $info[1] + $consumed)
                        end
                        break
                    end
                end
                continue
            end
            return
        end
if test "$node:$word" = '0:paint'; set node 1; set position 0; set ended 0; continue; end
if test "$node:$word" = '0:remote'; set node 2; set position 0; set ended 0; continue; end
if test "$node:$word" = '2:paint'; set node 3; set position 0; set ended 0; continue; end
        switch $node
case 0; return
case 2; return
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
            test $info[2] -gt 0; or return
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
                if test $info[2] -gt 0
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
set candidates 'paint' 'remote'
set descriptions 'Paint one or more colors.' ''
if test $ended -eq 0; and string match -q -- '-*' "$current"
set candidates '--target' '-t' '--token' '-k' '--verbose' '-v' '--root-only' '--no-root-only' '--help'
set descriptions '' '' '' '' '' '' '' '' 'Show this message and exit.'
end
case 1
set candidates
set descriptions
if test $ended -eq 0; and string match -q -- '-*' "$current"
set candidates '--target' '-t' '--color' '-c' '--tag' '-g' '--token' '-k' '--verbose' '-v' '--quiet' '-q' '--help'
set descriptions '' '' '' '' '' '' '' '' '' '' '' '' 'Show this message and exit.'
end
case 2
set candidates 'paint'
set descriptions 'Paint one or more colors.'
if test $ended -eq 0; and string match -q -- '-*' "$current"
set candidates '--target' '-t' '--help'
set descriptions '' '' 'Show this message and exit.'
end
case 3
set candidates
set descriptions
if test $ended -eq 0; and string match -q -- '-*' "$current"
set candidates '--target' '-t' '--color' '-c' '--tag' '-g' '--token' '-k' '--verbose' '-v' '--quiet' '-q' '--help'
set descriptions '' '' '' '' '' '' '' '' '' '' '' '' 'Show this message and exit.'
end
        end
        if test $ended -eq 1; or not string match -q -- '-*' "$current"
if test $node -eq 1; and test $position -eq 0; set target 5; end
if test $node -eq 1; and test $position -ge 1; set target 6; end
if test $node -eq 3; and test $position -eq 0; set target 16; end
if test $node -eq 3; and test $position -ge 1; set target 17; end
        end
    end
    if test $target -ge 0
        set candidates
        set descriptions
        switch $target
case 0; set candidates 'root' 'remote'
case 1; set candidates
case 2; set candidates
case 3; set candidates
case 4; set candidates
case 5; set candidates 'red' 'rose' 'blue' 'two words' 'quote\'s'
case 6; set candidates 'red' 'rose' 'blue' 'two words' 'quote\'s'
case 7; set candidates 'red' 'rose' 'blue' 'two words' 'quote\'s'
case 8; set candidates 'red' 'rose' 'blue' 'two words' 'quote\'s'
case 9; set candidates 'red' 'rose' 'blue' 'two words' 'quote\'s'
case 10; set candidates
case 11; set candidates
case 12; set candidates
case 13; set candidates
case 14; set candidates 'group' 'green'
case 15; set candidates
case 16; set candidates 'red' 'rose' 'blue' 'two words' 'quote\'s'
case 17; set candidates 'red' 'rose' 'blue' 'two words' 'quote\'s'
case 18; set candidates 'red' 'rose' 'blue' 'two words' 'quote\'s'
case 19; set candidates 'red' 'rose' 'blue' 'two words' 'quote\'s'
case 20; set candidates 'red' 'rose' 'blue' 'two words' 'quote\'s'
case 21; set candidates
case 22; set candidates
case 23; set candidates
case 24; set candidates
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
