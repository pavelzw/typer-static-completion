"""Zsh completion using the shared Bourne scanner and native completion actions."""

from __future__ import annotations

from ..model import Command, CommandTree
from ..shells import Shell
from .bash import _PARSER, BashGenerator


class ZshGenerator(BashGenerator):
    shell: str = Shell.zsh
    install_layout = "share/zsh/site-functions/_{prog}"
    filename = "_{prog}"

    def render(self, tree: CommandTree) -> str:
        return f"#compdef {self.quote(tree.prog_name)}\n" + super().render(tree)

    def suggestion_action(self, command: Command, flags: list[str]) -> str:
        action = super().suggestion_action(command, flags)
        if not self.options.include_help:
            return action
        commands = " ".join(
            self.quote(name + (" -- " + child.help if child.help else ""))
            for name, child in command.subcommands.items()
        )
        helps = {flag: p.help for p in command.options for flag in p.flags}
        options = " ".join(
            self.quote(flag + (" -- " + helps[flag] if helps[flag] else ""))
            for flag in flags
        )
        return (
            action
            + f"; descriptions=({commands}); if [[ $cur == -* && $ended == 0 ]]; then descriptions=({options}); fi"
        )

    def runtime(self) -> str:
        # The scanner uses zero-based arrays. Keep that emulation local and
        # restore native Zsh options before invoking its completion helpers.
        parser = _PARSER.replace(
            "@SETUP@",
            "    setopt localoptions ksharrays\n"
            "    local COMP_LINE=$BUFFER COMP_POINT=$CURSOR\n"
            "    local -a COMPREPLY\n",
        )
        return (
            parser
            + r"""
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
"""
        )

    def choice_options(self) -> str:
        return ":"

    def registration(self, name: str, prog_name: str) -> str:
        prog = self.quote(prog_name)
        return (
            f'if (( $+compstate )); then {name} "$@"; '
            f"elif (( $+functions[compdef] )); then compdef {name} {prog}; fi\n"
        )
