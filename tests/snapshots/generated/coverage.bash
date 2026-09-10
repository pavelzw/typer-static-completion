# Generated - do not edit.
_tsc_2a97516c354b6884() {
    local line=${COMP_LINE:0:$COMP_POINT} char quote= quote_prefix= token= trim= escaped=0 started=0 i
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
        elif [[ $char == "'" || $char == '"' ]]; then quote=$char; quote_prefix=$token; started=1
        elif [[ $char == ' ' || $char == $'\t' ]]; then
            if ((started)); then words+=("$token"); token=; trim=; started=0; fi
        else
            token+=$char; started=1
            if [[ $COMP_WORDBREAKS == *"$char"* ]]; then trim=$token; fi
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
0:-h) target=0; takes=0 ;;
0:--assist) target=0; takes=0 ;;
1:--value) target=1; takes=1 ;;
1:-h) target=2; takes=0 ;;
1:--assist) target=2; takes=0 ;;
2:-h) target=3; takes=0 ;;
2:--assist) target=3; takes=0 ;;
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
0:-h) target=0; takes=0 ;;
0:--assist) target=0; takes=0 ;;
1:--value) target=1; takes=1 ;;
1:-h) target=2; takes=0 ;;
1:--assist) target=2; takes=0 ;;
2:-h) target=3; takes=0 ;;
2:--assist) target=3; takes=0 ;;
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
0:show) node=1; position=0; ended=0; continue ;;
0:legacy-deprecated) node=2; position=0; ended=0; continue ;;
0:bare) node=3; position=0; ended=0; continue ;;
        esac
        # Once group arguments are consumed, the next operand must be a command.
        case $node in
0) return 0 ;;
        esac
        ((position+=1))
    done
    target=$pending
    if ((target < 0 && ended == 0)) && [[ $cur == --*=* ]]; then
        flag=${cur%%=*}; takes=0
        case "$node:$flag" in
0:-h) target=0; takes=0 ;;
0:--assist) target=0; takes=0 ;;
1:--value) target=1; takes=1 ;;
1:-h) target=2; takes=0 ;;
1:--assist) target=2; takes=0 ;;
2:-h) target=3; takes=0 ;;
2:--assist) target=3; takes=0 ;;
        esac
        ((takes)) || return 0
        prefix=$flag=; cur=${cur#*=}
    elif ((target < 0 && ended == 0)) && [[ $cur == -?* && $cur != --* ]]; then
        for ((j=1; j<${#cur}; j++)); do
            flag=-${cur:$j:1}; target=-1; takes=0
            case "$node:$flag" in
0:-h) target=0; takes=0 ;;
0:--assist) target=0; takes=0 ;;
1:--value) target=1; takes=1 ;;
1:-h) target=2; takes=0 ;;
1:--assist) target=2; takes=0 ;;
2:-h) target=3; takes=0 ;;
2:--assist) target=3; takes=0 ;;
            esac
            if ((takes)); then prefix=${cur:0:$((j+1))}; cur=${cur:$((j+1))}; break; fi
            target=-1
        done
    fi
    if ((target < 0)); then
        case $node in
0) candidates=(show legacy-deprecated bare); if [[ $cur == -* && $ended == 0 ]]; then candidates=(-h --assist); fi ;;
1) candidates=(); if [[ $cur == -* && $ended == 0 ]]; then candidates=(--value -h --assist); fi ;;
2) candidates=(); if [[ $cur == -* && $ended == 0 ]]; then candidates=(-h --assist); fi ;;
3) candidates=(); if [[ $cur == -* && $ended == 0 ]]; then candidates=(); fi ;;
        esac
        if [[ $cur != -* || $ended == 1 ]]; then
            case "$node:$position" in

            esac
        fi
    fi
    if ((target >= 0)); then
        candidates=(); descriptions=()
        case $target in
0) candidates=() ;;
1) candidates=('apos'"'"'trophe' 'café' 'bracket[one]:two' 'dollar$(demo)' 'tick`demo`' 'quote"double' 'slash\path'); compopt -o filenames 2>/dev/null || : ;;
2) candidates=() ;;
3) candidates=() ;;
        esac
    fi
    if [[ -n $file_mode ]]; then
        while IFS= read -r candidate; do candidates+=("$candidate"); done < <(compgen -A "$file_mode" -- "$cur")
        compopt -o filenames 2>/dev/null || :
    fi
    # An open quote makes Readline replace only the portion inside it.
    if [[ -n $quote ]]; then trim=$quote_prefix; fi
    # Readline retains @ at the start of its replacement word (the second
    # completion argument), unlike ordinary word-break delimiters such as :.
    if [[ ${2-} == @* && $trim == *@ ]]; then trim=${trim%@}; fi
    # Otherwise the scanner records unquoted, unescaped Readline word breaks.
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
