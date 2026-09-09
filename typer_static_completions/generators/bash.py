"""Standalone Bash completion with token-aware command and value dispatch."""

from __future__ import annotations

import hashlib
import shlex

from ..config import DynamicPolicy
from ..errors import IntrospectionError
from ..model import Command, CommandTree, Param, ValueKind
from ..shells import Shell
from .base import Generator, value_slots


class BashGenerator(Generator):
    shell: str = Shell.bash
    install_layout = "share/bash-completion/completions/{prog}"
    filename = "{prog}"

    def quote(self, text: str) -> str:
        if any(ord(c) < 32 or ord(c) == 127 for c in text):
            raise IntrospectionError(
                "Shell metadata must not contain control characters"
            )
        return shlex.quote(text)

    def runtime(self) -> str:
        return _PARSER.replace("@SETUP@", "") + _OUTPUT

    def registration(self, name: str, prog_name: str) -> str:
        return f"complete -F {name} -- {self.quote(prog_name)}\n"

    def choice_options(self) -> str:
        return "compopt -o filenames 2>/dev/null || :"

    def suggestion_action(self, command: Command, flags: list[str]) -> str:
        words = " ".join(self.quote(x) for x in command.subcommands)
        options = " ".join(self.quote(x) for x in flags)
        return f"candidates=({words}); if [[ $cur == -* && $ended == 0 ]]; then candidates=({options}); fi"

    def render(self, tree: CommandTree) -> str:
        nodes = list(tree.walk())
        ids = {c.path: i for i, c in enumerate(nodes)}
        params: list[Param] = []
        option_cases, command_cases, argument_cases, suggestion_cases = [], [], [], []
        group_cases = []
        for node_id, command in enumerate(nodes):
            if command.chain:
                raise IntrospectionError("Chain groups are not supported yet")
            if (command.is_group or command.subcommands) and command.arguments:
                raise IntrospectionError("Group arguments are not supported yet")
            if command.is_group or command.subcommands:
                group_cases.append(f"{node_id}) return 0 ;;")
            flags: list[str] = []
            argument_index = 0
            for param in command.params:
                if param.is_help and not self.options.include_help_option:
                    continue
                param_id = len(params)
                params.extend(value_slots(param))
                if param.flags:
                    flags.extend(param.flags)
                    for flag in param.flags:
                        option_cases.append(
                            f"{self.quote(f'{node_id}:{flag}')}) target={param_id}; takes={param.nargs if param.takes_value else 0} ;;"
                        )
                else:
                    pattern = (
                        f"{node_id}:*"
                        if param.nargs == -1
                        else f"{node_id}:{argument_index}"
                    )
                    argument_cases.append(f"{pattern}) target={param_id} ;;")
                    argument_index += 1
            for name, child in command.subcommands.items():
                command_cases.append(
                    f"{self.quote(f'{node_id}:{name}')}) node={ids[child.path]}; position=0; ended=0; continue ;;"
                )
            suggestion_cases.append(
                f"{node_id}) {self.suggestion_action(command, flags)} ;;"
            )
        actions = []
        for index, param in enumerate(params):
            kind = param.value_kind
            if kind is ValueKind.DYNAMIC:
                if self.options.dynamic in (
                    DynamicPolicy.ERROR,
                    DynamicPolicy.DELEGATE,
                ):
                    raise IntrospectionError(
                        "Dynamic callbacks require OMIT or FILE; delegation is not implemented yet"
                    )
                kind = (
                    ValueKind.FILE
                    if self.options.dynamic is DynamicPolicy.FILE
                    else ValueKind.OPAQUE
                )
            if (
                param.value_kind is ValueKind.OPAQUE
                and param.name in self.options.file_params
            ):
                kind = ValueKind.FILE
            action = "candidates=()"
            if kind is ValueKind.CHOICE:
                action = (
                    "candidates=("
                    + " ".join(self.quote(c) for c in param.choices)
                    + "); "
                    + self.choice_options()
                    + ("; ignore_case=1" if not param.case_sensitive else "")
                )
            elif kind in (ValueKind.FILE, ValueKind.DIRECTORY):
                action = f"file_mode={'directory' if kind is ValueKind.DIRECTORY else 'file'}"
            actions.append(f"{index}) {action} ;;")
        name = "_tsc_" + hashlib.sha256(tree.prog_name.encode()).hexdigest()[:16]
        banner = ""
        if self.options.banner:
            banner = "# Generated - do not edit.\n"
            if self.options.regenerate_command:
                self.quote(self.options.regenerate_command)
                banner += f"# Regenerate: {self.options.regenerate_command}\n"
            if self.options.include_version:
                from importlib.metadata import version

                banner += f"# typer-static-completions {version('typer-static-completions')}; typer {version('typer')}\n"
        script = self.runtime().replace("@NAME@", name)
        for marker, cases in (
            ("OPTIONS", option_cases),
            ("COMMANDS", command_cases),
            ("GROUPS", group_cases),
            ("ARGUMENTS", argument_cases),
            ("SUGGESTIONS", suggestion_cases),
            ("ACTIONS", actions),
        ):
            script = script.replace(f"@{marker}@", "\n".join(cases))
        return banner + script + self.registration(name, tree.prog_name)


_PARSER = r"""@NAME@() {
@SETUP@    local line=${COMP_LINE:0:$COMP_POINT} char quote= token= escaped=0 started=0 i
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
@OPTIONS@
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
@OPTIONS@
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
        case "$node:$word" in
@COMMANDS@
        esac
        # Groups without arguments require the next operand to be a command.
        case $node in
@GROUPS@
        esac
        ((position+=1))
    done
    target=$pending
    if ((target < 0 && ended == 0)) && [[ $cur == --*=* ]]; then
        flag=${cur%%=*}; takes=0
        case "$node:$flag" in
@OPTIONS@
        esac
        ((takes)) || return 0
        prefix=$flag=; cur=${cur#*=}
    elif ((target < 0 && ended == 0)) && [[ $cur == -?* && $cur != --* ]]; then
        for ((j=1; j<${#cur}; j++)); do
            flag=-${cur:$j:1}; target=-1; takes=0
            case "$node:$flag" in
@OPTIONS@
            esac
            if ((takes)); then prefix=${cur:0:$((j+1))}; cur=${cur:$((j+1))}; break; fi
            target=-1
        done
    fi
    if ((target < 0)); then
        case $node in
@SUGGESTIONS@
        esac
        if [[ $cur != -* || $ended == 1 ]]; then
            case "$node:$position" in
@ARGUMENTS@
            esac
        fi
    fi
    if ((target >= 0)); then
        candidates=(); descriptions=()
        case $target in
@ACTIONS@
        esac
    fi
"""

_OUTPUT = r"""    if [[ -n $file_mode ]]; then
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
"""
