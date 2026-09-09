#compdef demo
# Generated - do not edit.
_tsc_2a97516c354b6884() {
    setopt localoptions ksharrays
    local COMP_LINE=$BUFFER COMP_POINT=$CURSOR
    local -a COMPREPLY
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
0:--pair) target=0; takes=2 ;;
0:--help) target=2; takes=0 ;;
1:--pair) target=3; takes=2 ;;
1:-p) target=3; takes=2 ;;
1:--resource) target=5; takes=2 ;;
1:--triple) target=7; takes=3 ;;
1:--verbose) target=10; takes=0 ;;
1:-v) target=10; takes=0 ;;
1:--help) target=11; takes=0 ;;
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
0:--pair) target=0; takes=2 ;;
0:--help) target=2; takes=0 ;;
1:--pair) target=3; takes=2 ;;
1:-p) target=3; takes=2 ;;
1:--resource) target=5; takes=2 ;;
1:--triple) target=7; takes=3 ;;
1:--verbose) target=10; takes=0 ;;
1:-v) target=10; takes=0 ;;
1:--help) target=11; takes=0 ;;
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
0:paint) node=1; position=0; ended=0; continue ;;
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
0:--pair) target=0; takes=2 ;;
0:--help) target=2; takes=0 ;;
1:--pair) target=3; takes=2 ;;
1:-p) target=3; takes=2 ;;
1:--resource) target=5; takes=2 ;;
1:--triple) target=7; takes=3 ;;
1:--verbose) target=10; takes=0 ;;
1:-v) target=10; takes=0 ;;
1:--help) target=11; takes=0 ;;
        esac
        ((takes)) || return 0
        prefix=$flag=; cur=${cur#*=}
    elif ((target < 0 && ended == 0)) && [[ $cur == -?* && $cur != --* ]]; then
        for ((j=1; j<${#cur}; j++)); do
            flag=-${cur:$j:1}; target=-1; takes=0
            case "$node:$flag" in
0:--pair) target=0; takes=2 ;;
0:--help) target=2; takes=0 ;;
1:--pair) target=3; takes=2 ;;
1:-p) target=3; takes=2 ;;
1:--resource) target=5; takes=2 ;;
1:--triple) target=7; takes=3 ;;
1:--verbose) target=10; takes=0 ;;
1:-v) target=10; takes=0 ;;
1:--help) target=11; takes=0 ;;
            esac
            if ((takes)); then prefix=${cur:0:$((j+1))}; cur=${cur:$((j+1))}; break; fi
            target=-1
        done
    fi
    if ((target < 0)); then
        case $node in
0) candidates=(paint); if [[ $cur == -* && $ended == 0 ]]; then candidates=(--pair --help); fi; descriptions=(paint); if [[ $cur == -* && $ended == 0 ]]; then descriptions=(--pair '--help -- Show this message and exit.'); fi ;;
1) candidates=(); if [[ $cur == -* && $ended == 0 ]]; then candidates=(--pair -p --resource --triple --verbose -v --help); fi; descriptions=(); if [[ $cur == -* && $ended == 0 ]]; then descriptions=(--pair -p --resource --triple --verbose -v '--help -- Show this message and exit.'); fi ;;
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
1) candidates=() ;;
2) candidates=() ;;
3) candidates=(red rose blue 'two words' 'quote'"'"'s'); : ;;
4) candidates=(group green); : ;;
5) candidates=(red rose blue 'two words' 'quote'"'"'s'); : ;;
6) file_mode=file ;;
7) candidates=() ;;
8) candidates=() ;;
9) candidates=(red rose blue 'two words' 'quote'"'"'s'); : ;;
10) candidates=() ;;
11) candidates=() ;;
        esac
    fi

    unsetopt ksharrays
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
        compadd -U -i "$IPREFIX" -- "${matches[@]}"
    else
        compadd -d descriptions -- "${candidates[@]}"
    fi
}
if (( $+compstate )); then _tsc_2a97516c354b6884 "$@"; elif (( $+functions[compdef] )); then compdef _tsc_2a97516c354b6884 demo; fi
