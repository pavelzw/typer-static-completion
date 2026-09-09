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
0:--profile) target=1; takes=1 ;;
0:-p) target=1; takes=1 ;;
0:--help) target=2; takes=0 ;;
1:--mode) target=4; takes=1 ;;
1:-m) target=4; takes=1 ;;
1:--help) target=5; takes=0 ;;
2:--mode) target=8; takes=1 ;;
2:-m) target=8; takes=1 ;;
2:--help) target=9; takes=0 ;;
3:--mode) target=11; takes=1 ;;
3:-m) target=11; takes=1 ;;
3:--help) target=12; takes=0 ;;
4:--help) target=14; takes=0 ;;
5:--help) target=15; takes=0 ;;
6:--help) target=17; takes=0 ;;
7:--help) target=18; takes=0 ;;
8:--help) target=20; takes=0 ;;
9:--help) target=21; takes=0 ;;
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
0:--profile) target=1; takes=1 ;;
0:-p) target=1; takes=1 ;;
0:--help) target=2; takes=0 ;;
1:--mode) target=4; takes=1 ;;
1:-m) target=4; takes=1 ;;
1:--help) target=5; takes=0 ;;
2:--mode) target=8; takes=1 ;;
2:-m) target=8; takes=1 ;;
2:--help) target=9; takes=0 ;;
3:--mode) target=11; takes=1 ;;
3:-m) target=11; takes=1 ;;
3:--help) target=12; takes=0 ;;
4:--help) target=14; takes=0 ;;
5:--help) target=15; takes=0 ;;
6:--help) target=17; takes=0 ;;
7:--help) target=18; takes=0 ;;
8:--help) target=20; takes=0 ;;
9:--help) target=21; takes=0 ;;
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
0) if ((position < 1)); then ended=1; ((position+=1)); continue; fi ;;
2) if ((position < 2)); then ended=1; ((position+=1)); continue; fi ;;
4) if ((position < 1)); then ended=1; ((position+=1)); continue; fi ;;
6) if ((position < 1)); then ended=1; ((position+=1)); continue; fi ;;
8) if ((1)); then ended=1; ((position+=1)); continue; fi ;;
        esac
        case "$node:$word" in
0:deploy) node=1; position=0; ended=0; continue ;;
0:remote) node=2; position=0; ended=0; continue ;;
0:files) node=4; position=0; ended=0; continue ;;
0:optional) node=6; position=0; ended=0; continue ;;
0:many) node=8; position=0; ended=0; continue ;;
2:paint) node=3; position=0; ended=0; continue ;;
4:show) node=5; position=0; ended=0; continue ;;
6:show) node=7; position=0; ended=0; continue ;;
8:show) node=9; position=0; ended=0; continue ;;
        esac
        # Once group arguments are consumed, the next operand must be a command.
        case $node in
0) return 0 ;;
2) return 0 ;;
4) return 0 ;;
6) return 0 ;;
8) return 0 ;;
        esac
        ((position+=1))
    done
    target=$pending
    if ((target < 0 && ended == 0)) && [[ $cur == --*=* ]]; then
        flag=${cur%%=*}; takes=0
        case "$node:$flag" in
0:--profile) target=1; takes=1 ;;
0:-p) target=1; takes=1 ;;
0:--help) target=2; takes=0 ;;
1:--mode) target=4; takes=1 ;;
1:-m) target=4; takes=1 ;;
1:--help) target=5; takes=0 ;;
2:--mode) target=8; takes=1 ;;
2:-m) target=8; takes=1 ;;
2:--help) target=9; takes=0 ;;
3:--mode) target=11; takes=1 ;;
3:-m) target=11; takes=1 ;;
3:--help) target=12; takes=0 ;;
4:--help) target=14; takes=0 ;;
5:--help) target=15; takes=0 ;;
6:--help) target=17; takes=0 ;;
7:--help) target=18; takes=0 ;;
8:--help) target=20; takes=0 ;;
9:--help) target=21; takes=0 ;;
        esac
        ((takes)) || return 0
        prefix=$flag=; cur=${cur#*=}
    elif ((target < 0 && ended == 0)) && [[ $cur == -?* && $cur != --* ]]; then
        for ((j=1; j<${#cur}; j++)); do
            flag=-${cur:$j:1}; target=-1; takes=0
            case "$node:$flag" in
0:--profile) target=1; takes=1 ;;
0:-p) target=1; takes=1 ;;
0:--help) target=2; takes=0 ;;
1:--mode) target=4; takes=1 ;;
1:-m) target=4; takes=1 ;;
1:--help) target=5; takes=0 ;;
2:--mode) target=8; takes=1 ;;
2:-m) target=8; takes=1 ;;
2:--help) target=9; takes=0 ;;
3:--mode) target=11; takes=1 ;;
3:-m) target=11; takes=1 ;;
3:--help) target=12; takes=0 ;;
4:--help) target=14; takes=0 ;;
5:--help) target=15; takes=0 ;;
6:--help) target=17; takes=0 ;;
7:--help) target=18; takes=0 ;;
8:--help) target=20; takes=0 ;;
9:--help) target=21; takes=0 ;;
            esac
            if ((takes)); then prefix=${cur:0:$((j+1))}; cur=${cur:$((j+1))}; break; fi
            target=-1
        done
    fi
    if ((target < 0)); then
        case $node in
0) candidates=(deploy remote files optional many); if [[ $cur == -* && $ended == 0 ]]; then candidates=(--profile -p --help); fi ;;
1) candidates=(); if [[ $cur == -* && $ended == 0 ]]; then candidates=(--mode -m --help); fi ;;
2) candidates=(paint); if [[ $cur == -* && $ended == 0 ]]; then candidates=(--mode -m --help); fi ;;
3) candidates=(); if [[ $cur == -* && $ended == 0 ]]; then candidates=(--mode -m --help); fi ;;
4) candidates=(show); if [[ $cur == -* && $ended == 0 ]]; then candidates=(--help); fi ;;
5) candidates=(); if [[ $cur == -* && $ended == 0 ]]; then candidates=(--help); fi ;;
6) candidates=(show); if [[ $cur == -* && $ended == 0 ]]; then candidates=(--help); fi ;;
7) candidates=(); if [[ $cur == -* && $ended == 0 ]]; then candidates=(--help); fi ;;
8) candidates=(show); if [[ $cur == -* && $ended == 0 ]]; then candidates=(--help); fi ;;
9) candidates=(); if [[ $cur == -* && $ended == 0 ]]; then candidates=(--help); fi ;;
        esac
        if [[ $cur != -* || $ended == 1 ]]; then
            case "$node:$position" in
0:0) target=0 ;;
1:0) target=3 ;;
2:0) target=6 ;;
2:1) target=7 ;;
3:0) target=10 ;;
4:0) target=13 ;;
6:0) target=16 ;;
8:*) target=19 ;;
            esac
        fi
    fi
    if ((target >= 0)); then
        candidates=(); descriptions=()
        case $target in
0) candidates=(root remote); compopt -o filenames 2>/dev/null || : ;;
1) candidates=(red rose blue 'two words' 'quote'"'"'s'); compopt -o filenames 2>/dev/null || : ;;
2) candidates=() ;;
3) candidates=(red rose blue 'two words' 'quote'"'"'s'); compopt -o filenames 2>/dev/null || : ;;
4) candidates=(red rose blue 'two words' 'quote'"'"'s'); compopt -o filenames 2>/dev/null || : ;;
5) candidates=() ;;
6) candidates=(red rose blue 'two words' 'quote'"'"'s'); compopt -o filenames 2>/dev/null || : ;;
7) candidates=(group green); compopt -o filenames 2>/dev/null || : ;;
8) candidates=(red rose blue 'two words' 'quote'"'"'s'); compopt -o filenames 2>/dev/null || : ;;
9) candidates=() ;;
10) candidates=(red rose blue 'two words' 'quote'"'"'s'); compopt -o filenames 2>/dev/null || : ;;
11) candidates=(Blue RED Rose 'Two Words' 'Café'); compopt -o filenames 2>/dev/null || :; ignore_case=1 ;;
12) candidates=() ;;
13) file_mode=directory ;;
14) candidates=() ;;
15) candidates=() ;;
16) candidates=() ;;
17) candidates=() ;;
18) candidates=() ;;
19) candidates=(red rose blue 'two words' 'quote'"'"'s'); compopt -o filenames 2>/dev/null || : ;;
20) candidates=() ;;
21) candidates=() ;;
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
