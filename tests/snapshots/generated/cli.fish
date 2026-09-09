# Generated - do not edit.
function __tsc_a0400f50fb4ab9f2_option
if test "$argv[1]:$argv[2]" = '0:--help'; printf "%s\n" 0 0; return; end
if test "$argv[1]:$argv[2]" = '1:--prog-name'; printf "%s\n" 2 1; return; end
if test "$argv[1]:$argv[2]" = '1:--shell'; printf "%s\n" 3 1; return; end
if test "$argv[1]:$argv[2]" = '1:--output'; printf "%s\n" 4 1; return; end
if test "$argv[1]:$argv[2]" = '1:-o'; printf "%s\n" 4 1; return; end
if test "$argv[1]:$argv[2]" = '1:--help'; printf "%s\n" 5 0; return; end
if test "$argv[1]:$argv[2]" = '2:--pyproject'; printf "%s\n" 6 1; return; end
if test "$argv[1]:$argv[2]" = '2:--output-dir'; printf "%s\n" 7 1; return; end
if test "$argv[1]:$argv[2]" = '2:--shell'; printf "%s\n" 8 1; return; end
if test "$argv[1]:$argv[2]" = '2:--only'; printf "%s\n" 9 1; return; end
if test "$argv[1]:$argv[2]" = '2:--app'; printf "%s\n" 10 1; return; end
if test "$argv[1]:$argv[2]" = '2:--prune'; printf "%s\n" 11 0; return; end
if test "$argv[1]:$argv[2]" = '2:--no-prune'; printf "%s\n" 11 0; return; end
if test "$argv[1]:$argv[2]" = '2:--help'; printf "%s\n" 12 0; return; end
if test "$argv[1]:$argv[2]" = '3:--pyproject'; printf "%s\n" 13 1; return; end
if test "$argv[1]:$argv[2]" = '3:--output-dir'; printf "%s\n" 14 1; return; end
if test "$argv[1]:$argv[2]" = '3:--shell'; printf "%s\n" 15 1; return; end
if test "$argv[1]:$argv[2]" = '3:--only'; printf "%s\n" 16 1; return; end
if test "$argv[1]:$argv[2]" = '3:--app'; printf "%s\n" 17 1; return; end
if test "$argv[1]:$argv[2]" = '3:--prune'; printf "%s\n" 18 0; return; end
if test "$argv[1]:$argv[2]" = '3:--no-prune'; printf "%s\n" 18 0; return; end
if test "$argv[1]:$argv[2]" = '3:--diff'; printf "%s\n" 19 0; return; end
if test "$argv[1]:$argv[2]" = '3:--no-diff'; printf "%s\n" 19 0; return; end
if test "$argv[1]:$argv[2]" = '3:--max-files'; printf "%s\n" 20 1; return; end
if test "$argv[1]:$argv[2]" = '3:--help'; printf "%s\n" 21 0; return; end
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
if test "$node:$word" = '0:sync'; set node 2; set position 0; set ended 0; continue; end
if test "$node:$word" = '0:check'; set node 3; set position 0; set ended 0; continue; end
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
set candidates 'generate' 'sync' 'check'
set descriptions 'Render one app\'s completion script.' 'Write project completions and their ownership manifest.' 'Fail if committed completions differ, without writing files.'
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
case 2
set candidates
set descriptions
if test $ended -eq 0; and string match -q -- '-*' "$current"
set candidates '--pyproject' '--output-dir' '--shell' '--only' '--app' '--prune' '--no-prune' '--help'
set descriptions 'Project metadata; defaults to nearest pyproject.toml.' 'Output directory; defaults to completions beside pyproject.' 'Shell to generate; repeat to select several.' 'Script name to manage; repeat to select several.' 'Override a declared script: NAME=MODULE:APP.' 'Remove unchanged owned orphan files.' 'Remove unchanged owned orphan files.' 'Show this message and exit.'
end
case 3
set candidates
set descriptions
if test $ended -eq 0; and string match -q -- '-*' "$current"
set candidates '--pyproject' '--output-dir' '--shell' '--only' '--app' '--prune' '--no-prune' '--diff' '--no-diff' '--max-files' '--help'
set descriptions 'Project metadata; defaults to nearest pyproject.toml.' 'Output directory; defaults to completions beside pyproject.' 'Shell to check; repeat to select several.' 'Script name to manage; repeat to select several.' 'Override a declared script: NAME=MODULE:APP.' 'Report owned orphan files.' 'Report owned orphan files.' 'Include unified diffs.' 'Include unified diffs.' 'Maximum diagnostic entries to display.' 'Show this message and exit.'
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
case 6; set file_mode file
case 7; set file_mode file
case 8; set candidates 'bash' 'fish' 'zsh'; set descriptions 'Shell to generate; repeat to select several.' 'Shell to generate; repeat to select several.' 'Shell to generate; repeat to select several.'
case 9; set candidates
case 10; set candidates
case 11; set candidates
case 12; set candidates
case 13; set file_mode file
case 14; set file_mode file
case 15; set candidates 'bash' 'fish' 'zsh'; set descriptions 'Shell to check; repeat to select several.' 'Shell to check; repeat to select several.' 'Shell to check; repeat to select several.'
case 16; set candidates
case 17; set candidates
case 18; set candidates
case 19; set candidates
case 20; set candidates
case 21; set candidates
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
