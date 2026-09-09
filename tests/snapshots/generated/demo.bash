# Generated - do not edit.
_tsc_2a97516c354b6884() {
    local line=${COMP_LINE:0:$COMP_POINT} char quote= token= escaped=0 started=0 i
    local -a words=() candidates=() descriptions=()
    # Tokenize only the text before the cursor, without eval or external tools.
    for ((i=0; i<${#line}; i++)); do
        char=${line:$i:1}
        if ((escaped)); then
            if [[ $quote == '"' && $char != '$' && $char != '"' && $char != '\' && $char != '`' ]]; then token+='\'; fi
            token+=$char; escaped=0; started=1
        elif [[ $char == '\' && $quote != "'" ]]; then escaped=1; started=1
        elif [[ -n $quote ]]; then
            if [[ $char == "$quote" ]]; then quote=; else token+=$char; fi
        elif [[ $char == "'" || $char == '"' ]]; then quote=$char; started=1
        elif [[ $char == ' ' || $char == $'\t' ]]; then
            if ((started)); then words+=("$token"); token=; started=0; fi
        else token+=$char; started=1
        fi
    done
    words+=("$token")
    local cur=$token node=0 position=0 ended=0 pending=-1 remaining=0 target=-1 takes=0
    local word flag value j prefix= file_mode= candidate ignore_case=0
    COMPREPLY=()
    for ((i=1; i<${#words[@]}-1; i++)); do
        word=${words[i]}
        if ((pending >= 0)); then
            ((remaining-=1))
            if ((remaining)); then ((pending+=1)); else pending=-1; fi
            continue
        fi
        if [[ $word == -- && $ended == 0 ]]; then ended=1; continue; fi
        if [[ $word == -* && $word != - && $ended == 0 ]]; then
            flag=${word%%=*}; value=0
            [[ $word == *=* ]] && value=1
            target=-1; takes=0
            case "$node:$flag" in
0:--profile) target=0; takes=1 ;;
0:--verbose) target=1; takes=0 ;;
0:--no-verbose) target=1; takes=0 ;;
0:--help) target=2; takes=0 ;;
1:--color) target=3; takes=1 ;;
1:-c) target=3; takes=1 ;;
1:--config) target=4; takes=1 ;;
1:--directory) target=5; takes=1 ;;
1:--cache) target=6; takes=0 ;;
1:--no-cache) target=6; takes=0 ;;
1:--help) target=7; takes=0 ;;
2:--help) target=8; takes=0 ;;
3:--help) target=9; takes=0 ;;
4:--help) target=10; takes=0 ;;
5:--help) target=12; takes=0 ;;
6:--help) target=14; takes=0 ;;
            esac
            if ((target >= 0)); then
                remaining=$((takes-value))
                if ((remaining > 0)); then pending=$((target+value)); fi
                continue
            fi
            # Short flag clusters and attached short values.
            if [[ $word != --* ]]; then
                for ((j=1; j<${#word}; j++)); do
                    flag=-${word:$j:1}; target=-1; takes=0
                    case "$node:$flag" in
0:--profile) target=0; takes=1 ;;
0:--verbose) target=1; takes=0 ;;
0:--no-verbose) target=1; takes=0 ;;
0:--help) target=2; takes=0 ;;
1:--color) target=3; takes=1 ;;
1:-c) target=3; takes=1 ;;
1:--config) target=4; takes=1 ;;
1:--directory) target=5; takes=1 ;;
1:--cache) target=6; takes=0 ;;
1:--no-cache) target=6; takes=0 ;;
1:--help) target=7; takes=0 ;;
2:--help) target=8; takes=0 ;;
3:--help) target=9; takes=0 ;;
4:--help) target=10; takes=0 ;;
5:--help) target=12; takes=0 ;;
6:--help) target=14; takes=0 ;;
                    esac
                    ((target < 0)) && return 0
                    if ((takes)); then
                        value=0
                        ((j < ${#word}-1)) && value=1
                        remaining=$((takes-value))
                        if ((remaining > 0)); then pending=$((target+value)); fi
                        break
                    fi
                done
                continue
            fi
            return 0
        fi
        # Group operands precede the command and end group option parsing.
        case $node in

        esac
        case "$node:$word" in
0:deploy) node=1; position=0; ended=0; continue ;;
0:tasks) node=2; position=0; ended=0; continue ;;
0:tags) node=3; position=0; ended=0; continue ;;
0:remote) node=4; position=0; ended=0; continue ;;
4:add) node=5; position=0; ended=0; continue ;;
4:remove) node=6; position=0; ended=0; continue ;;
        esac
        # Once group arguments are consumed, the next operand must be a command.
        case $node in
0) return 0 ;;
4) return 0 ;;
        esac
        ((position+=1))
    done
    target=$pending
    if ((target < 0 && ended == 0)) && [[ $cur == --*=* ]]; then
        flag=${cur%%=*}; takes=0
        case "$node:$flag" in
0:--profile) target=0; takes=1 ;;
0:--verbose) target=1; takes=0 ;;
0:--no-verbose) target=1; takes=0 ;;
0:--help) target=2; takes=0 ;;
1:--color) target=3; takes=1 ;;
1:-c) target=3; takes=1 ;;
1:--config) target=4; takes=1 ;;
1:--directory) target=5; takes=1 ;;
1:--cache) target=6; takes=0 ;;
1:--no-cache) target=6; takes=0 ;;
1:--help) target=7; takes=0 ;;
2:--help) target=8; takes=0 ;;
3:--help) target=9; takes=0 ;;
4:--help) target=10; takes=0 ;;
5:--help) target=12; takes=0 ;;
6:--help) target=14; takes=0 ;;
        esac
        ((takes)) || return 0
        prefix=$flag=; cur=${cur#*=}
    elif ((target < 0 && ended == 0)) && [[ $cur == -?* && $cur != --* ]]; then
        for ((j=1; j<${#cur}; j++)); do
            flag=-${cur:$j:1}; target=-1; takes=0
            case "$node:$flag" in
0:--profile) target=0; takes=1 ;;
0:--verbose) target=1; takes=0 ;;
0:--no-verbose) target=1; takes=0 ;;
0:--help) target=2; takes=0 ;;
1:--color) target=3; takes=1 ;;
1:-c) target=3; takes=1 ;;
1:--config) target=4; takes=1 ;;
1:--directory) target=5; takes=1 ;;
1:--cache) target=6; takes=0 ;;
1:--no-cache) target=6; takes=0 ;;
1:--help) target=7; takes=0 ;;
2:--help) target=8; takes=0 ;;
3:--help) target=9; takes=0 ;;
4:--help) target=10; takes=0 ;;
5:--help) target=12; takes=0 ;;
6:--help) target=14; takes=0 ;;
            esac
            if ((takes)); then prefix=${cur:0:$((j+1))}; cur=${cur:$((j+1))}; break; fi
            target=-1
        done
    fi
    if ((target < 0)); then
        case $node in
0) candidates=(deploy tasks tags remote); if [[ $cur == -* && $ended == 0 ]]; then candidates=(--profile --verbose --no-verbose --help); fi ;;
1) candidates=(); if [[ $cur == -* && $ended == 0 ]]; then candidates=(--color -c --config --directory --cache --no-cache --help); fi ;;
2) candidates=(); if [[ $cur == -* && $ended == 0 ]]; then candidates=(--help); fi ;;
3) candidates=(); if [[ $cur == -* && $ended == 0 ]]; then candidates=(--help); fi ;;
4) candidates=(add remove); if [[ $cur == -* && $ended == 0 ]]; then candidates=(--help); fi ;;
5) candidates=(); if [[ $cur == -* && $ended == 0 ]]; then candidates=(--help); fi ;;
6) candidates=(); if [[ $cur == -* && $ended == 0 ]]; then candidates=(--help); fi ;;
        esac
        if [[ $cur != -* || $ended == 1 ]]; then
            case "$node:$position" in
5:0) target=11 ;;
6:0) target=13 ;;
            esac
        fi
    fi
    if ((target >= 0)); then
        candidates=(); descriptions=()
        case $target in
0) candidates=() ;;
1) candidates=() ;;
2) candidates=() ;;
3) candidates=(red rose blue 'two words' 'quote'"'"'s'); compopt -o filenames 2>/dev/null || : ;;
4) file_mode=file ;;
5) file_mode=directory ;;
6) candidates=() ;;
7) candidates=() ;;
8) candidates=() ;;
9) candidates=() ;;
10) candidates=() ;;
11) candidates=() ;;
12) candidates=() ;;
13) candidates=() ;;
14) candidates=() ;;
        esac
    fi
    if [[ -n $file_mode ]]; then
        while IFS= read -r candidate; do candidates+=("$candidate"); done < <(compgen -A "$file_mode" -- "$cur")
        compopt -o filenames 2>/dev/null || :
    fi
    # Readline replaces only the part after its last word-break character.
    local trim= full=$prefix$cur k
    for ((k=0; k<${#full}; k++)); do
        char=${full:$k:1}
        if [[ $char != ' ' && $char != "'" && $char != '"' && $char != '\' && $COMP_WORDBREAKS == *"$char"* ]]; then trim=${full:0:k+1}; fi
    done
    # Readline's filename quoting leaves command substitutions executable.
    # Quote literal candidates ourselves when they contain expansion syntax.
    local quote_literals=0
    for candidate in "${candidates[@]}"; do
        if [[ $candidate == *'$'* || $candidate == *'`'* ]]; then
            if compopt -o noquote 2>/dev/null; then quote_literals=1; fi
            break
        fi
    done
    for candidate in "${candidates[@]}"; do
        if [[ $candidate == "$cur"* ]] || { ((ignore_case)) && [[ ${candidate,,} == "${cur,,}"* ]]; }; then
            candidate=$prefix$candidate
            candidate=${candidate#"$trim"}
            if ((quote_literals)); then
                if [[ $quote == '"' ]]; then
                    candidate=${candidate//\\/\\\\}
                    candidate=${candidate//\"/\\\"}
                    candidate=${candidate//\$/\\\$}
                    candidate=${candidate//\`/\\\`}
                elif [[ $quote == "'" ]]; then
                    candidate=${candidate//\'/\'\\\'\'}
                else
                    printf -v candidate '%q' "$candidate"
                fi
            fi
            COMPREPLY+=("$candidate")
        fi
    done
    return 0
}
complete -F _tsc_2a97516c354b6884 -- demo
