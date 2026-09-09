#compdef demo
# Generated - do not edit.
_tsc_2a97516c354b6884() {
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
0:--target) target=0; takes=1 ;;
0:-t) target=0; takes=1 ;;
0:--token) target=1; takes=1 ;;
0:-k) target=1; takes=1 ;;
0:--verbose) target=2; takes=0 ;;
0:-v) target=2; takes=0 ;;
0:--root-only) target=3; takes=0 ;;
0:--no-root-only) target=3; takes=0 ;;
0:--help) target=4; takes=0 ;;
1:--target) target=7; takes=1 ;;
1:-t) target=7; takes=1 ;;
1:--color) target=8; takes=1 ;;
1:-c) target=8; takes=1 ;;
1:--tag) target=9; takes=1 ;;
1:-g) target=9; takes=1 ;;
1:--token) target=10; takes=1 ;;
1:-k) target=10; takes=1 ;;
1:--verbose) target=11; takes=0 ;;
1:-v) target=11; takes=0 ;;
1:--quiet) target=12; takes=0 ;;
1:-q) target=12; takes=0 ;;
1:--help) target=13; takes=0 ;;
2:--target) target=14; takes=1 ;;
2:-t) target=14; takes=1 ;;
2:--help) target=15; takes=0 ;;
3:--target) target=18; takes=1 ;;
3:-t) target=18; takes=1 ;;
3:--color) target=19; takes=1 ;;
3:-c) target=19; takes=1 ;;
3:--tag) target=20; takes=1 ;;
3:-g) target=20; takes=1 ;;
3:--token) target=21; takes=1 ;;
3:-k) target=21; takes=1 ;;
3:--verbose) target=22; takes=0 ;;
3:-v) target=22; takes=0 ;;
3:--quiet) target=23; takes=0 ;;
3:-q) target=23; takes=0 ;;
3:--help) target=24; takes=0 ;;
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
0:--target) target=0; takes=1 ;;
0:-t) target=0; takes=1 ;;
0:--token) target=1; takes=1 ;;
0:-k) target=1; takes=1 ;;
0:--verbose) target=2; takes=0 ;;
0:-v) target=2; takes=0 ;;
0:--root-only) target=3; takes=0 ;;
0:--no-root-only) target=3; takes=0 ;;
0:--help) target=4; takes=0 ;;
1:--target) target=7; takes=1 ;;
1:-t) target=7; takes=1 ;;
1:--color) target=8; takes=1 ;;
1:-c) target=8; takes=1 ;;
1:--tag) target=9; takes=1 ;;
1:-g) target=9; takes=1 ;;
1:--token) target=10; takes=1 ;;
1:-k) target=10; takes=1 ;;
1:--verbose) target=11; takes=0 ;;
1:-v) target=11; takes=0 ;;
1:--quiet) target=12; takes=0 ;;
1:-q) target=12; takes=0 ;;
1:--help) target=13; takes=0 ;;
2:--target) target=14; takes=1 ;;
2:-t) target=14; takes=1 ;;
2:--help) target=15; takes=0 ;;
3:--target) target=18; takes=1 ;;
3:-t) target=18; takes=1 ;;
3:--color) target=19; takes=1 ;;
3:-c) target=19; takes=1 ;;
3:--tag) target=20; takes=1 ;;
3:-g) target=20; takes=1 ;;
3:--token) target=21; takes=1 ;;
3:-k) target=21; takes=1 ;;
3:--verbose) target=22; takes=0 ;;
3:-v) target=22; takes=0 ;;
3:--quiet) target=23; takes=0 ;;
3:-q) target=23; takes=0 ;;
3:--help) target=24; takes=0 ;;
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
0:remote) node=2; position=0; ended=0; continue ;;
2:paint) node=3; position=0; ended=0; continue ;;
        esac
        # Once group arguments are consumed, the next operand must be a command.
        case $node in
0) return 0 ;;
2) return 0 ;;
        esac
        ((position+=1))
    done
    target=$pending
    if ((target < 0 && ended == 0)) && [[ $cur == --*=* ]]; then
        flag=${cur%%=*}; takes=0
        case "$node:$flag" in
0:--target) target=0; takes=1 ;;
0:-t) target=0; takes=1 ;;
0:--token) target=1; takes=1 ;;
0:-k) target=1; takes=1 ;;
0:--verbose) target=2; takes=0 ;;
0:-v) target=2; takes=0 ;;
0:--root-only) target=3; takes=0 ;;
0:--no-root-only) target=3; takes=0 ;;
0:--help) target=4; takes=0 ;;
1:--target) target=7; takes=1 ;;
1:-t) target=7; takes=1 ;;
1:--color) target=8; takes=1 ;;
1:-c) target=8; takes=1 ;;
1:--tag) target=9; takes=1 ;;
1:-g) target=9; takes=1 ;;
1:--token) target=10; takes=1 ;;
1:-k) target=10; takes=1 ;;
1:--verbose) target=11; takes=0 ;;
1:-v) target=11; takes=0 ;;
1:--quiet) target=12; takes=0 ;;
1:-q) target=12; takes=0 ;;
1:--help) target=13; takes=0 ;;
2:--target) target=14; takes=1 ;;
2:-t) target=14; takes=1 ;;
2:--help) target=15; takes=0 ;;
3:--target) target=18; takes=1 ;;
3:-t) target=18; takes=1 ;;
3:--color) target=19; takes=1 ;;
3:-c) target=19; takes=1 ;;
3:--tag) target=20; takes=1 ;;
3:-g) target=20; takes=1 ;;
3:--token) target=21; takes=1 ;;
3:-k) target=21; takes=1 ;;
3:--verbose) target=22; takes=0 ;;
3:-v) target=22; takes=0 ;;
3:--quiet) target=23; takes=0 ;;
3:-q) target=23; takes=0 ;;
3:--help) target=24; takes=0 ;;
        esac
        ((takes)) || return 0
        prefix=$flag=; cur=${cur#*=}
    elif ((target < 0 && ended == 0)) && [[ $cur == -?* && $cur != --* ]]; then
        for ((j=1; j<${#cur}; j++)); do
            flag=-${cur:$j:1}; target=-1; takes=0
            case "$node:$flag" in
0:--target) target=0; takes=1 ;;
0:-t) target=0; takes=1 ;;
0:--token) target=1; takes=1 ;;
0:-k) target=1; takes=1 ;;
0:--verbose) target=2; takes=0 ;;
0:-v) target=2; takes=0 ;;
0:--root-only) target=3; takes=0 ;;
0:--no-root-only) target=3; takes=0 ;;
0:--help) target=4; takes=0 ;;
1:--target) target=7; takes=1 ;;
1:-t) target=7; takes=1 ;;
1:--color) target=8; takes=1 ;;
1:-c) target=8; takes=1 ;;
1:--tag) target=9; takes=1 ;;
1:-g) target=9; takes=1 ;;
1:--token) target=10; takes=1 ;;
1:-k) target=10; takes=1 ;;
1:--verbose) target=11; takes=0 ;;
1:-v) target=11; takes=0 ;;
1:--quiet) target=12; takes=0 ;;
1:-q) target=12; takes=0 ;;
1:--help) target=13; takes=0 ;;
2:--target) target=14; takes=1 ;;
2:-t) target=14; takes=1 ;;
2:--help) target=15; takes=0 ;;
3:--target) target=18; takes=1 ;;
3:-t) target=18; takes=1 ;;
3:--color) target=19; takes=1 ;;
3:-c) target=19; takes=1 ;;
3:--tag) target=20; takes=1 ;;
3:-g) target=20; takes=1 ;;
3:--token) target=21; takes=1 ;;
3:-k) target=21; takes=1 ;;
3:--verbose) target=22; takes=0 ;;
3:-v) target=22; takes=0 ;;
3:--quiet) target=23; takes=0 ;;
3:-q) target=23; takes=0 ;;
3:--help) target=24; takes=0 ;;
            esac
            if ((takes)); then prefix=${cur:0:$((j+1))}; cur=${cur:$((j+1))}; break; fi
            target=-1
        done
    fi
    if ((target < 0)); then
        case $node in
0) candidates=(paint remote); if [[ $cur == -* && $ended == 0 ]]; then candidates=(--target -t --token -k --verbose -v --root-only --no-root-only --help); fi; descriptions=('paint -- Paint one or more colors.' remote); if [[ $cur == -* && $ended == 0 ]]; then descriptions=(--target -t --token -k --verbose -v --root-only --no-root-only '--help -- Show this message and exit.'); fi ;;
1) candidates=(); if [[ $cur == -* && $ended == 0 ]]; then candidates=(--target -t --color -c --tag -g --token -k --verbose -v --quiet -q --help); fi; descriptions=(); if [[ $cur == -* && $ended == 0 ]]; then descriptions=(--target -t --color -c --tag -g --token -k --verbose -v --quiet -q '--help -- Show this message and exit.'); fi ;;
2) candidates=(paint); if [[ $cur == -* && $ended == 0 ]]; then candidates=(--target -t --help); fi; descriptions=('paint -- Paint one or more colors.'); if [[ $cur == -* && $ended == 0 ]]; then descriptions=(--target -t '--help -- Show this message and exit.'); fi ;;
3) candidates=(); if [[ $cur == -* && $ended == 0 ]]; then candidates=(--target -t --color -c --tag -g --token -k --verbose -v --quiet -q --help); fi; descriptions=(); if [[ $cur == -* && $ended == 0 ]]; then descriptions=(--target -t --color -c --tag -g --token -k --verbose -v --quiet -q '--help -- Show this message and exit.'); fi ;;
        esac
        if [[ $cur != -* || $ended == 1 ]]; then
            case "$node:$position" in
1:0) target=5 ;;
1:*) target=6 ;;
3:0) target=16 ;;
3:*) target=17 ;;
            esac
        fi
    fi
    if ((target >= 0)); then
        candidates=(); descriptions=()
        case $target in
0) candidates=(root remote); : ;;
1) candidates=() ;;
2) candidates=() ;;
3) candidates=() ;;
4) candidates=() ;;
5) candidates=(red rose blue 'two words' 'quote'"'"'s'); : ;;
6) candidates=(red rose blue 'two words' 'quote'"'"'s'); : ;;
7) candidates=(red rose blue 'two words' 'quote'"'"'s'); : ;;
8) candidates=(red rose blue 'two words' 'quote'"'"'s'); : ;;
9) candidates=(red rose blue 'two words' 'quote'"'"'s'); : ;;
10) candidates=() ;;
11) candidates=() ;;
12) candidates=() ;;
13) candidates=() ;;
14) candidates=(group green); : ;;
15) candidates=() ;;
16) candidates=(red rose blue 'two words' 'quote'"'"'s'); : ;;
17) candidates=(red rose blue 'two words' 'quote'"'"'s'); : ;;
18) candidates=(red rose blue 'two words' 'quote'"'"'s'); : ;;
19) candidates=(red rose blue 'two words' 'quote'"'"'s'); : ;;
20) candidates=(red rose blue 'two words' 'quote'"'"'s'); : ;;
21) candidates=() ;;
22) candidates=() ;;
23) candidates=() ;;
24) candidates=() ;;
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
if (( $+compstate )); then _tsc_2a97516c354b6884 "$@"; elif (( $+functions[compdef] )); then compdef _tsc_2a97516c354b6884 demo; fi
