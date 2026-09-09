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
    local cur=$token node=0 position=0 ended=0 pending=-1 target=-1 takes=0
    local word flag value j prefix= file_mode= candidate
    COMPREPLY=()
    for ((i=1; i<${#words[@]}-1; i++)); do
        word=${words[i]}
        if ((pending >= 0)); then pending=-1; continue; fi
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
                if ((takes && !value)); then pending=$target; fi
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
                        ((j == ${#word}-1)) && pending=$target
                        break
                    fi
                done
                continue
            fi
            return 0
        fi
        case "$node:$word" in
0:show) node=1; position=0; ended=0; continue ;;
0:legacy-deprecated) node=2; position=0; ended=0; continue ;;
0:bare) node=3; position=0; ended=0; continue ;;
        esac
        # Groups without arguments require the next operand to be a command.
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
0) candidates=(show legacy-deprecated bare); if [[ $cur == -* && $ended == 0 ]]; then candidates=(-h --assist); fi; descriptions=('show -- Show literal values: [x], $HOME, and `demo`.' 'legacy-deprecated -- A deprecated command.' 'bare -- A command without a help flag.'); if [[ $cur == -* && $ended == 0 ]]; then descriptions=('-h -- Show this message and exit.' '--assist -- Show this message and exit.'); fi ;;
1) candidates=(); if [[ $cur == -* && $ended == 0 ]]; then candidates=(--value -h --assist); fi; descriptions=(); if [[ $cur == -* && $ended == 0 ]]; then descriptions=('--value -- Use [x]: "$HOME", `demo`, and $(demo).' '-h -- Show this message and exit.' '--assist -- Show this message and exit.'); fi ;;
2) candidates=(); if [[ $cur == -* && $ended == 0 ]]; then candidates=(-h --assist); fi; descriptions=(); if [[ $cur == -* && $ended == 0 ]]; then descriptions=('-h -- Show this message and exit.' '--assist -- Show this message and exit.'); fi ;;
3) candidates=(); if [[ $cur == -* && $ended == 0 ]]; then candidates=(); fi; descriptions=(); if [[ $cur == -* && $ended == 0 ]]; then descriptions=(); fi ;;
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
1) candidates=('apos'"'"'trophe' 'café' 'bracket[one]:two' 'dollar$(demo)' 'tick`demo`' 'quote"double' 'slash\path'); : ;;
2) candidates=() ;;
3) candidates=() ;;
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
    else
        compadd -d descriptions -- "${candidates[@]}"
    fi
}
if (( $+compstate )); then _tsc_2a97516c354b6884 "$@"; elif (( $+functions[compdef] )); then compdef _tsc_2a97516c354b6884 demo; fi
