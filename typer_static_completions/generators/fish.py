"""Native Fish completion rules guarded by a token-aware command scanner."""

from __future__ import annotations

import hashlib

from ..config import DynamicPolicy
from ..errors import IntrospectionError
from ..model import CommandTree, Param, ValueKind
from ..shells import Shell
from .base import Generator


class FishGenerator(Generator):
    shell: str = Shell.fish
    install_layout = "share/fish/vendor_completions.d/{prog}.fish"
    filename = "{prog}.fish"

    def quote(self, text: str) -> str:
        if any(ord(c) < 32 or ord(c) == 127 for c in text):
            raise IntrospectionError(
                "Shell metadata must not contain control characters"
            )
        return "'" + text.replace("\\", "\\\\").replace("'", "\\'") + "'"

    def value_action(self, param: Param, tree: CommandTree) -> str:
        kind = param.value_kind
        if kind is ValueKind.DYNAMIC:
            if self.options.dynamic in (DynamicPolicy.ERROR, DynamicPolicy.DELEGATE):
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
        if kind is ValueKind.FILE:
            return "-F"
        if kind is ValueKind.DIRECTORY:
            return "-f -a '(__fish_complete_directories)'"
        if kind is ValueKind.CHOICE:
            # Fish evaluates the argument expression once; quote each literal
            # inside it, then quote the whole expression in the registration.
            choices = " ".join(self.quote(c) for c in param.choices)
            return "-f -a " + self.quote(choices)
        return "-f"

    def render(self, tree: CommandTree) -> str:
        name = "__tsc_" + hashlib.sha256(tree.prog_name.encode()).hexdigest()[:16]
        nodes = list(tree.walk())
        ids = {c.path: i for i, c in enumerate(nodes)}
        options, children, rules = [], [], []
        prog = self.quote(tree.prog_name)
        # Explicit -F on file rules overrides the default suppression.
        rules.append(f"complete -c {prog} -f")
        for node, command in enumerate(nodes):
            if command.chain:
                raise IntrospectionError("Chain groups are not supported yet")
            if (command.is_group or command.subcommands) and command.arguments:
                raise IntrospectionError("Group arguments are not supported yet")
            position = 0
            for param in command.params:
                if param.is_help and not self.options.include_help_option:
                    continue
                if param.nargs not in (1, -1) or (param.flags and param.nargs != 1):
                    raise IntrospectionError(
                        "Only scalar options and scalar/variadic arguments are supported yet"
                    )
                description = ""
                if self.options.include_help and param.help:
                    description = " -d " + self.quote(param.help)
                action = self.value_action(param, tree)
                if param.flags:
                    for flag in param.flags:
                        options.append(
                            f'if test "$node:$flag" = {self.quote(f"{node}:{flag}")}; set takes {int(param.takes_value)}; end'
                        )
                        if flag.startswith("--"):
                            selector = "-l " + self.quote(flag[2:])
                        elif len(flag) == 2 and flag.startswith("-"):
                            selector = "-s " + self.quote(flag[1:])
                        else:
                            raise IntrospectionError(
                                f"Unsupported Fish option spelling: {flag!r}"
                            )
                        condition = self.quote(f"{name} {node} option")
                        required = " -r" if param.takes_value else ""
                        rules.append(
                            f"complete -c {prog} -n {condition} {selector}{required} {action}{description}"
                        )
                else:
                    slot = "variadic" if param.nargs == -1 else str(position)
                    condition = self.quote(f"{name} {node} {slot} {position}")
                    rules.append(
                        f"complete -c {prog} -n {condition} {action}{description}"
                    )
                    position += 1
            for child_name, child in command.subcommands.items():
                children.append(
                    f'if test "$node:$word" = {self.quote(f"{node}:{child_name}")}; set node {ids[child.path]}; set position 0; set ended 0; continue; end'
                )
                description = ""
                if self.options.include_help and child.help:
                    description = " -d " + self.quote(child.help)
                condition = self.quote(f"{name} {node} command")
                rules.append(
                    f"complete -c {prog} -n {condition} -f -a {self.quote(self.quote(child_name))}{description}"
                )
        runtime = (
            _RUNTIME.replace("@NAME@", name)
            .replace("@OPTIONS@", "\n".join(options))
            .replace("@CHILDREN@", "\n".join(children))
        )
        banner = ""
        if self.options.banner:
            banner = "# Generated - do not edit.\n"
            if self.options.regenerate_command:
                self.quote(self.options.regenerate_command)
                banner += f"# Regenerate: {self.options.regenerate_command}\n"
            if self.options.include_version:
                from importlib.metadata import version

                banner += f"# typer-static-completions {version('typer-static-completions')}; typer {version('typer')}\n"
        return banner + runtime + "\n".join(rules) + "\n"


_RUNTIME = r"""function @NAME@
    set -l tokens (commandline -xpc)
    set -l node 0
    set -l position 0
    set -l pending 0
    set -l ended 0
    for word in $tokens[2..-1]
        if test $pending -eq 1
            set pending 0
            continue
        end
        if test "$word" = --; and test $ended -eq 0
            set ended 1
            continue
        end
        if string match -qr '^-.+' -- "$word"; and test $ended -eq 0
            set -l flag (string split -m 1 = -- "$word")[1]
            set -l takes -1
@OPTIONS@
            if test $takes -ge 0
                if test $takes -eq 1; and not string match -q '*=*' -- "$word"
                    set pending 1
                end
                continue
            end
            if not string match -q -- '--*' "$word"
                set -l rest (string sub -s 2 -- "$word")
                while test -n "$rest"
                    set flag -(string sub -l 1 -- "$rest")
                    set rest (string sub -s 2 -- "$rest")
                    set takes -1
@OPTIONS@
                    if test $takes -lt 0
                        return 1
                    end
                    if test $takes -eq 1
                        if test -z "$rest"
                            set pending 1
                        end
                        break
                    end
                end
                continue
            end
            return 1
        end
@CHILDREN@
        set position (math $position + 1)
    end
    test $node -eq $argv[1]; or return 1
    if test "$argv[2]" = option
        test $ended -eq 0
    else if test $pending -eq 1
        return 1
    else if test "$argv[2]" = command
        test $position -eq 0
    else if test "$argv[2]" = variadic
        test $position -ge $argv[3]
    else
        test $position -eq $argv[2]
    end
end
"""
