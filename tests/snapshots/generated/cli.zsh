#compdef typer-static-completion
# Generated - do not edit.
_tsc_a0400f50fb4ab9f2() {
    setopt localoptions ksharrays
    local COMP_LINE=$BUFFER COMP_POINT=$CURSOR
    local -a COMPREPLY
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
            :
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
0:--help) target=0; takes=0 ;;
1:--prog-name) target=2; takes=1 ;;
1:--shell) target=3; takes=1 ;;
1:--output) target=4; takes=1 ;;
1:-o) target=4; takes=1 ;;
1:--help) target=5; takes=0 ;;
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
0:--help) target=0; takes=0 ;;
1:--prog-name) target=2; takes=1 ;;
1:--shell) target=3; takes=1 ;;
1:--output) target=4; takes=1 ;;
1:-o) target=4; takes=1 ;;
1:--help) target=5; takes=0 ;;
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
0:generate) node=1; position=0; ended=0; continue ;;
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
0:--help) target=0; takes=0 ;;
1:--prog-name) target=2; takes=1 ;;
1:--shell) target=3; takes=1 ;;
1:--output) target=4; takes=1 ;;
1:-o) target=4; takes=1 ;;
1:--help) target=5; takes=0 ;;
        esac
        ((takes)) || return 0
        prefix=$flag=; cur=${cur#*=}
    elif ((target < 0 && ended == 0)) && [[ $cur == -?* && $cur != --* ]]; then
        for ((j=1; j<${#cur}; j++)); do
            flag=-${cur:$j:1}; target=-1; takes=0
            case "$node:$flag" in
0:--help) target=0; takes=0 ;;
1:--prog-name) target=2; takes=1 ;;
1:--shell) target=3; takes=1 ;;
1:--output) target=4; takes=1 ;;
1:-o) target=4; takes=1 ;;
1:--help) target=5; takes=0 ;;
            esac
            if ((takes)); then prefix=${cur:0:$((j+1))}; cur=${cur:$((j+1))}; break; fi
            target=-1
        done
    fi
    if ((target < 0)); then
        case $node in
0) candidates=(generate); if [[ $cur == -* && $ended == 0 ]]; then candidates=(--help); fi; descriptions=('generate -- Render one app'"'"'s completion script.'); if [[ $cur == -* && $ended == 0 ]]; then descriptions=('--help -- Show this message and exit.'); fi ;;
1) candidates=(); if [[ $cur == -* && $ended == 0 ]]; then candidates=(--prog-name --shell --output -o --help); fi; descriptions=(); if [[ $cur == -* && $ended == 0 ]]; then descriptions=('--prog-name -- Command name users type.' '--shell -- Target shell.' '--output -- Output file; omit or use - for stdout.' '-o -- Output file; omit or use - for stdout.' '--help -- Show this message and exit.'); fi ;;
        esac
        if [[ $cur != -* || $ended == 1 ]]; then
            case "$node:$position" in
1:0) target=1 ;;
            esac
        fi
    fi
    if ((target >= 0)); then
        candidates=(); descriptions=()
        case $target in
0) candidates=() ;;
1) candidates=() ;;
2) candidates=() ;;
3) candidates=(bash fish zsh); : ;;
4) file_mode=file ;;
5) candidates=() ;;
        esac
    fi

    unsetopt ksharrays
    # A closing quote already in the buffer must not receive a literal space.
    local -a suffix_args=()
    [[ -n $QISUFFIX ]] && suffix_args=(-S '')
    if [[ -n $prefix ]]; then
        # Tell Zsh that the attached flag is already present in the input.
        compset -P "${(b)prefix}"
    fi
    if [[ $file_mode == directory ]]; then
        _files -/
    elif [[ $file_mode == file ]]; then
        _files
    elif ((ignore_case)); then
        # Filter explicitly: native matcher character classes miss accented pairs.
        local -a matches=()
        for candidate in "${candidates[@]}"; do
            if [[ ${(L)candidate} == "${(L)cur}"* ]]; then matches+=("$candidate"); fi
        done
        compadd "${suffix_args[@]}" -U -i "$IPREFIX" -- "${matches[@]}"
    else
        compadd "${suffix_args[@]}" -d descriptions -- "${candidates[@]}"
    fi
}
if (( $+compstate )); then _tsc_a0400f50fb4ab9f2 "$@"; elif (( $+functions[compdef] )); then compdef _tsc_a0400f50fb4ab9f2 typer-static-completion; fi
