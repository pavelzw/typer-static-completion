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
0:--help) target=0; takes=0 ;;
1:--mode) target=4; takes=1 ;;
1:-m) target=4; takes=1 ;;
1:--verbose) target=5; takes=0 ;;
1:-v) target=5; takes=0 ;;
1:--help) target=6; takes=0 ;;
2:--help) target=11; takes=0 ;;
3:--help) target=14; takes=0 ;;
4:--help) target=17; takes=0 ;;
5:--help) target=21; takes=0 ;;
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
1:--mode) target=4; takes=1 ;;
1:-m) target=4; takes=1 ;;
1:--verbose) target=5; takes=0 ;;
1:-v) target=5; takes=0 ;;
1:--help) target=6; takes=0 ;;
2:--help) target=11; takes=0 ;;
3:--help) target=14; takes=0 ;;
4:--help) target=17; takes=0 ;;
5:--help) target=21; takes=0 ;;
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
0:framed) node=2; position=0; ended=0; continue ;;
0:resource) node=3; position=0; ended=0; continue ;;
0:directory) node=4; position=0; ended=0; continue ;;
0:triple) node=5; position=0; ended=0; continue ;;
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
1:--mode) target=4; takes=1 ;;
1:-m) target=4; takes=1 ;;
1:--verbose) target=5; takes=0 ;;
1:-v) target=5; takes=0 ;;
1:--help) target=6; takes=0 ;;
2:--help) target=11; takes=0 ;;
3:--help) target=14; takes=0 ;;
4:--help) target=17; takes=0 ;;
5:--help) target=21; takes=0 ;;
        esac
        ((takes)) || return 0
        prefix=$flag=; cur=${cur#*=}
    elif ((target < 0 && ended == 0)) && [[ $cur == -?* && $cur != --* ]]; then
        for ((j=1; j<${#cur}; j++)); do
            flag=-${cur:$j:1}; target=-1; takes=0
            case "$node:$flag" in
0:--help) target=0; takes=0 ;;
1:--mode) target=4; takes=1 ;;
1:-m) target=4; takes=1 ;;
1:--verbose) target=5; takes=0 ;;
1:-v) target=5; takes=0 ;;
1:--help) target=6; takes=0 ;;
2:--help) target=11; takes=0 ;;
3:--help) target=14; takes=0 ;;
4:--help) target=17; takes=0 ;;
5:--help) target=21; takes=0 ;;
            esac
            if ((takes)); then prefix=${cur:0:$((j+1))}; cur=${cur:$((j+1))}; break; fi
            target=-1
        done
    fi
    if ((target < 0)); then
        case $node in
0) candidates=(paint framed resource directory triple); if [[ $cur == -* && $ended == 0 ]]; then candidates=(--help); fi ;;
1) candidates=(); if [[ $cur == -* && $ended == 0 ]]; then candidates=(--mode -m --verbose -v --help); fi ;;
2) candidates=(); if [[ $cur == -* && $ended == 0 ]]; then candidates=(--help); fi ;;
3) candidates=(); if [[ $cur == -* && $ended == 0 ]]; then candidates=(--help); fi ;;
4) candidates=(); if [[ $cur == -* && $ended == 0 ]]; then candidates=(--help); fi ;;
5) candidates=(); if [[ $cur == -* && $ended == 0 ]]; then candidates=(--help); fi ;;
        esac
        if [[ $cur != -* || $ended == 1 ]]; then
            case "$node:$position" in
1:0) target=1 ;;
1:1) target=2 ;;
1:*) target=3 ;;
2:0) target=7 ;;
2:1) target=8 ;;
2:2) target=9 ;;
2:3) target=10 ;;
3:0) target=12 ;;
3:1) target=13 ;;
4:0) target=15 ;;
4:1) target=16 ;;
5:0) target=18 ;;
5:1) target=19 ;;
5:2) target=20 ;;
            esac
        fi
    fi
    if ((target >= 0)); then
        candidates=(); descriptions=()
        case $target in
0) candidates=() ;;
1) candidates=(red rose blue 'two words' 'quote'"'"'s'); compopt -o filenames 2>/dev/null || : ;;
2) candidates=(group green); compopt -o filenames 2>/dev/null || : ;;
3) candidates=(red rose blue 'two words' 'quote'"'"'s'); compopt -o filenames 2>/dev/null || : ;;
4) candidates=(red rose blue 'two words' 'quote'"'"'s'); compopt -o filenames 2>/dev/null || : ;;
5) candidates=() ;;
6) candidates=() ;;
7) candidates=(root remote); compopt -o filenames 2>/dev/null || : ;;
8) candidates=(red rose blue 'two words' 'quote'"'"'s'); compopt -o filenames 2>/dev/null || : ;;
9) candidates=(group green); compopt -o filenames 2>/dev/null || : ;;
10) candidates=(Blue RED Rose 'Two Words' 'Café'); compopt -o filenames 2>/dev/null || : ;;
11) candidates=() ;;
12) candidates=(red rose blue 'two words' 'quote'"'"'s'); compopt -o filenames 2>/dev/null || : ;;
13) file_mode=file ;;
14) candidates=() ;;
15) candidates=(red rose blue 'two words' 'quote'"'"'s'); compopt -o filenames 2>/dev/null || : ;;
16) file_mode=directory ;;
17) candidates=() ;;
18) candidates=() ;;
19) candidates=() ;;
20) candidates=(Blue RED Rose 'Two Words' 'Café'); compopt -o filenames 2>/dev/null || :; ignore_case=1 ;;
21) candidates=() ;;
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
