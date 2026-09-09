# Generated - do not edit.
_tsc_a0400f50fb4ab9f2() {
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
0:--help) target=0; takes=0 ;;
1:--prog-name) target=2; takes=1 ;;
1:--shell) target=3; takes=1 ;;
1:--output) target=4; takes=1 ;;
1:-o) target=4; takes=1 ;;
1:--help) target=5; takes=0 ;;
2:--pyproject) target=6; takes=1 ;;
2:--output-dir) target=7; takes=1 ;;
2:--shell) target=8; takes=1 ;;
2:--only) target=9; takes=1 ;;
2:--app) target=10; takes=1 ;;
2:--prune) target=11; takes=0 ;;
2:--no-prune) target=11; takes=0 ;;
2:--help) target=12; takes=0 ;;
3:--pyproject) target=13; takes=1 ;;
3:--output-dir) target=14; takes=1 ;;
3:--shell) target=15; takes=1 ;;
3:--only) target=16; takes=1 ;;
3:--app) target=17; takes=1 ;;
3:--prune) target=18; takes=0 ;;
3:--no-prune) target=18; takes=0 ;;
3:--diff) target=19; takes=0 ;;
3:--no-diff) target=19; takes=0 ;;
3:--max-files) target=20; takes=1 ;;
3:--help) target=21; takes=0 ;;
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
0:--help) target=0; takes=0 ;;
1:--prog-name) target=2; takes=1 ;;
1:--shell) target=3; takes=1 ;;
1:--output) target=4; takes=1 ;;
1:-o) target=4; takes=1 ;;
1:--help) target=5; takes=0 ;;
2:--pyproject) target=6; takes=1 ;;
2:--output-dir) target=7; takes=1 ;;
2:--shell) target=8; takes=1 ;;
2:--only) target=9; takes=1 ;;
2:--app) target=10; takes=1 ;;
2:--prune) target=11; takes=0 ;;
2:--no-prune) target=11; takes=0 ;;
2:--help) target=12; takes=0 ;;
3:--pyproject) target=13; takes=1 ;;
3:--output-dir) target=14; takes=1 ;;
3:--shell) target=15; takes=1 ;;
3:--only) target=16; takes=1 ;;
3:--app) target=17; takes=1 ;;
3:--prune) target=18; takes=0 ;;
3:--no-prune) target=18; takes=0 ;;
3:--diff) target=19; takes=0 ;;
3:--no-diff) target=19; takes=0 ;;
3:--max-files) target=20; takes=1 ;;
3:--help) target=21; takes=0 ;;
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
0:generate) node=1; position=0; ended=0; continue ;;
0:sync) node=2; position=0; ended=0; continue ;;
0:check) node=3; position=0; ended=0; continue ;;
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
0:--help) target=0; takes=0 ;;
1:--prog-name) target=2; takes=1 ;;
1:--shell) target=3; takes=1 ;;
1:--output) target=4; takes=1 ;;
1:-o) target=4; takes=1 ;;
1:--help) target=5; takes=0 ;;
2:--pyproject) target=6; takes=1 ;;
2:--output-dir) target=7; takes=1 ;;
2:--shell) target=8; takes=1 ;;
2:--only) target=9; takes=1 ;;
2:--app) target=10; takes=1 ;;
2:--prune) target=11; takes=0 ;;
2:--no-prune) target=11; takes=0 ;;
2:--help) target=12; takes=0 ;;
3:--pyproject) target=13; takes=1 ;;
3:--output-dir) target=14; takes=1 ;;
3:--shell) target=15; takes=1 ;;
3:--only) target=16; takes=1 ;;
3:--app) target=17; takes=1 ;;
3:--prune) target=18; takes=0 ;;
3:--no-prune) target=18; takes=0 ;;
3:--diff) target=19; takes=0 ;;
3:--no-diff) target=19; takes=0 ;;
3:--max-files) target=20; takes=1 ;;
3:--help) target=21; takes=0 ;;
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
2:--pyproject) target=6; takes=1 ;;
2:--output-dir) target=7; takes=1 ;;
2:--shell) target=8; takes=1 ;;
2:--only) target=9; takes=1 ;;
2:--app) target=10; takes=1 ;;
2:--prune) target=11; takes=0 ;;
2:--no-prune) target=11; takes=0 ;;
2:--help) target=12; takes=0 ;;
3:--pyproject) target=13; takes=1 ;;
3:--output-dir) target=14; takes=1 ;;
3:--shell) target=15; takes=1 ;;
3:--only) target=16; takes=1 ;;
3:--app) target=17; takes=1 ;;
3:--prune) target=18; takes=0 ;;
3:--no-prune) target=18; takes=0 ;;
3:--diff) target=19; takes=0 ;;
3:--no-diff) target=19; takes=0 ;;
3:--max-files) target=20; takes=1 ;;
3:--help) target=21; takes=0 ;;
            esac
            if ((takes)); then prefix=${cur:0:$((j+1))}; cur=${cur:$((j+1))}; break; fi
            target=-1
        done
    fi
    if ((target < 0)); then
        case $node in
0) candidates=(generate sync check); if [[ $cur == -* && $ended == 0 ]]; then candidates=(--help); fi ;;
1) candidates=(); if [[ $cur == -* && $ended == 0 ]]; then candidates=(--prog-name --shell --output -o --help); fi ;;
2) candidates=(); if [[ $cur == -* && $ended == 0 ]]; then candidates=(--pyproject --output-dir --shell --only --app --prune --no-prune --help); fi ;;
3) candidates=(); if [[ $cur == -* && $ended == 0 ]]; then candidates=(--pyproject --output-dir --shell --only --app --prune --no-prune --diff --no-diff --max-files --help); fi ;;
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
3) candidates=(bash fish zsh); compopt -o filenames 2>/dev/null || : ;;
4) file_mode=file ;;
5) candidates=() ;;
6) file_mode=file ;;
7) file_mode=file ;;
8) candidates=(bash fish zsh); compopt -o filenames 2>/dev/null || : ;;
9) candidates=() ;;
10) candidates=() ;;
11) candidates=() ;;
12) candidates=() ;;
13) file_mode=file ;;
14) file_mode=file ;;
15) candidates=(bash fish zsh); compopt -o filenames 2>/dev/null || : ;;
16) candidates=() ;;
17) candidates=() ;;
18) candidates=() ;;
19) candidates=() ;;
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
    for candidate in "${candidates[@]}"; do
        if [[ $candidate == "$cur"* ]]; then
            candidate=$prefix$candidate
            COMPREPLY+=("${candidate#"$trim"}")
        fi
    done
    return 0
}
complete -F _tsc_a0400f50fb4ab9f2 -- typer-static-completions
