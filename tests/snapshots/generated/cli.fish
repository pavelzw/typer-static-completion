# Generated - do not edit.
function __tsc_a0400f50fb4ab9f2_option
if test "$argv[1]:$argv[2]" = '0:--help'; printf "%s\n" 0 0; return; end
if test "$argv[1]:$argv[2]" = '1:--prog-name'; printf "%s\n" 2 1; return; end
if test "$argv[1]:$argv[2]" = '1:--shell'; printf "%s\n" 3 1; return; end
if test "$argv[1]:$argv[2]" = '1:--output'; printf "%s\n" 4 1; return; end
if test "$argv[1]:$argv[2]" = '1:-o'; printf "%s\n" 4 1; return; end
if test "$argv[1]:$argv[2]" = '1:--help'; printf "%s\n" 5 0; return; end
    printf '%s\n' -1 0
end

function __tsc_a0400f50fb4ab9f2
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
            set -l info (__tsc_a0400f50fb4ab9f2_option $node "$flag")
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
                    set info (__tsc_a0400f50fb4ab9f2_option $node "$flag")
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
if test "$node:$word" = '0:generate'; set node 1; set position 0; set ended 0; continue; end
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
    if test $target -lt 0; and test $ended -eq 0
        if string match -q -- '--*=*' "$current"
            set -l parts (string split -m 1 = -- "$current")
            set -l info (__tsc_a0400f50fb4ab9f2_option $node "$parts[1]")
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
                set -l info (__tsc_a0400f50fb4ab9f2_option $node "$flag")
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
set candidates 'generate'
set descriptions 'Render one app\'s completion script.'
if test $ended -eq 0; and string match -q -- '-*' "$current"
set candidates '--help'
set descriptions 'Show this message and exit.'
end
case 1
set candidates
set descriptions
if test $ended -eq 0; and string match -q -- '-*' "$current"
set candidates '--prog-name' '--shell' '--output' '-o' '--help'
set descriptions 'Command name users type.' 'Target shell.' 'Output file; omit or use - for stdout.' 'Output file; omit or use - for stdout.' 'Show this message and exit.'
end
        end
        if test $ended -eq 1; or not string match -q -- '-*' "$current"
if test $node -eq 1; and test $position -eq 0; set target 1; end
        end
    end
    if test $target -ge 0
        set candidates
        set descriptions
        switch $target
case 0; set candidates
case 1; set candidates
case 2; set candidates
case 3; set candidates 'bash' 'fish' 'zsh'; set descriptions 'Target shell.' 'Target shell.' 'Target shell.'
case 4; set file_mode file
case 5; set candidates
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
complete -c 'typer-static-completions' -f -a '(__tsc_a0400f50fb4ab9f2)'
