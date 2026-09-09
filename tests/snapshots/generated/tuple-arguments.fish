# Generated - do not edit.
function __tsc_2a97516c354b6884_option
if test "$argv[1]:$argv[2]" = '0:--help'; printf "%s\n" 0 0; return; end
if test "$argv[1]:$argv[2]" = '1:--mode'; printf "%s\n" 4 1; return; end
if test "$argv[1]:$argv[2]" = '1:-m'; printf "%s\n" 4 1; return; end
if test "$argv[1]:$argv[2]" = '1:--verbose'; printf "%s\n" 5 0; return; end
if test "$argv[1]:$argv[2]" = '1:-v'; printf "%s\n" 5 0; return; end
if test "$argv[1]:$argv[2]" = '1:--help'; printf "%s\n" 6 0; return; end
if test "$argv[1]:$argv[2]" = '2:--help'; printf "%s\n" 11 0; return; end
if test "$argv[1]:$argv[2]" = '3:--help'; printf "%s\n" 14 0; return; end
if test "$argv[1]:$argv[2]" = '4:--help'; printf "%s\n" 17 0; return; end
if test "$argv[1]:$argv[2]" = '5:--help'; printf "%s\n" 21 0; return; end
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
if test "$node:$word" = '0:framed'; set node 2; set position 0; set ended 0; continue; end
if test "$node:$word" = '0:resource'; set node 3; set position 0; set ended 0; continue; end
if test "$node:$word" = '0:directory'; set node 4; set position 0; set ended 0; continue; end
if test "$node:$word" = '0:triple'; set node 5; set position 0; set ended 0; continue; end
        switch $node
case 0; return
        end
        set position (math $position + 1)
    end
    set -l target $pending
    set -l prefix ''
    set -l candidates
    set -l descriptions
    set -l file_mode ''
    set -l choice_mode ''
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
set candidates 'paint' 'framed' 'resource' 'directory' 'triple'
set descriptions '' '' '' '' ''
if test $ended -eq 0; and string match -q -- '-*' "$current"
set candidates '--help'
set descriptions 'Show this message and exit.'
end
case 1
set candidates
set descriptions
if test $ended -eq 0; and string match -q -- '-*' "$current"
set candidates '--mode' '-m' '--verbose' '-v' '--help'
set descriptions '' '' '' '' 'Show this message and exit.'
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
set candidates
set descriptions
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
        end
        if test $ended -eq 1; or not string match -q -- '-*' "$current"
if test $node -eq 1; and test $position -eq 0; set target 1; end
if test $node -eq 1; and test $position -eq 1; set target 2; end
if test $node -eq 1; and test $position -ge 2; set target 3; end
if test $node -eq 2; and test $position -eq 0; set target 7; end
if test $node -eq 2; and test $position -eq 1; set target 8; end
if test $node -eq 2; and test $position -eq 2; set target 9; end
if test $node -eq 2; and test $position -eq 3; set target 10; end
if test $node -eq 3; and test $position -eq 0; set target 12; end
if test $node -eq 3; and test $position -eq 1; set target 13; end
if test $node -eq 4; and test $position -eq 0; set target 15; end
if test $node -eq 4; and test $position -eq 1; set target 16; end
if test $node -eq 5; and test $position -eq 0; set target 18; end
if test $node -eq 5; and test $position -eq 1; set target 19; end
if test $node -eq 5; and test $position -eq 2; set target 20; end
        end
    end
    if test $target -ge 0
        set candidates
        set descriptions
        switch $target
case 0; set candidates
case 1; set candidates 'red' 'rose' 'blue' 'two words' 'quote\'s'; set choice_mode sensitive
case 2; set candidates 'group' 'green'; set choice_mode sensitive
case 3; set candidates 'red' 'rose' 'blue' 'two words' 'quote\'s'; set choice_mode sensitive
case 4; set candidates 'red' 'rose' 'blue' 'two words' 'quote\'s'; set choice_mode sensitive
case 5; set candidates
case 6; set candidates
case 7; set candidates 'root' 'remote'; set choice_mode sensitive
case 8; set candidates 'red' 'rose' 'blue' 'two words' 'quote\'s'; set choice_mode sensitive
case 9; set candidates 'group' 'green'; set choice_mode sensitive
case 10; set candidates 'Blue' 'RED' 'Rose' 'Two Words' 'Café'; set choice_mode sensitive
case 11; set candidates
case 12; set candidates 'red' 'rose' 'blue' 'two words' 'quote\'s'; set choice_mode sensitive
case 13; set file_mode file
case 14; set candidates
case 15; set candidates 'red' 'rose' 'blue' 'two words' 'quote\'s'; set choice_mode sensitive
case 16; set file_mode directory
case 17; set candidates
case 18; set candidates
case 19; set candidates
case 20; set candidates 'Blue' 'RED' 'Rose' 'Two Words' 'Café'; set choice_mode insensitive
case 21; set candidates
        end
    end
    set -l index 1
    for candidate in $candidates
        set -l match_candidate "$candidate"
        set -l match_current "$current"
        if test "$choice_mode" = insensitive
            set match_candidate (string lower -- "$candidate")
            set match_current (string lower -- "$current")
        end
        if test -z "$choice_mode"; or string match -qr -- '^'(string escape --style=regex -- "$match_current") "$match_candidate"
            printf '%s\t%s\n' "$prefix$candidate" "$descriptions[$index]"
        end
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
