"""Fish completion with command-scoped parsing and native candidate matching."""

from __future__ import annotations

import hashlib

from ..config import DynamicPolicy
from ..errors import IntrospectionError
from ..model import CommandTree, Param, ValueKind
from ..shells import Shell
from .base import Generator, value_slots


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

    def _value_action(self, param: Param, tree: CommandTree) -> str:
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
        if kind in (ValueKind.FILE, ValueKind.DIRECTORY):
            return f"set file_mode {kind.value}"
        if kind is ValueKind.CHOICE:
            values = " ".join(self.quote(c) for c in param.choices)
            action = f"set candidates {values}; set choice_mode {'sensitive' if param.case_sensitive else 'insensitive'}"
            if self.options.include_help and param.help:
                descriptions = " ".join(self.quote(param.help) for _ in param.choices)
                action += f"; set descriptions {descriptions}"
            return action
        return "set candidates"

    def render(self, tree: CommandTree) -> str:
        name = "__tsc_" + hashlib.sha256(tree.prog_name.encode()).hexdigest()[:16]
        nodes = list(tree.walk())
        ids = {c.path: i for i, c in enumerate(nodes)}
        params: list[Param] = []
        options, children, groups, arguments, suggestions = [], [], [], [], []
        operands = []
        prog = self.quote(tree.prog_name)
        for node, command in enumerate(nodes):
            if command.chain:
                raise IntrospectionError("Chain groups are not supported yet")
            if command.is_group or command.subcommands:
                groups.append(f"case {node}; return")
            position = 0
            flags: list[str] = []
            descriptions: list[str] = []
            for param in command.params:
                if param.is_help and not self.options.include_help_option:
                    continue
                param_id = len(params)
                slots = value_slots(param)
                params.extend(slots)
                if param.flags:
                    for flag in param.flags:
                        options.append(
                            f'if test "$argv[1]:$argv[2]" = {self.quote(f"{node}:{flag}")}; printf "%s\\n" {param_id} {param.nargs if param.takes_value else 0}; return; end'
                        )
                        flags.append(flag)
                        descriptions.append(
                            param.help if self.options.include_help else ""
                        )
                else:
                    comparison = "-ge" if param.nargs == -1 else "-eq"
                    for offset in range(len(slots)):
                        arguments.append(
                            f"if test $node -eq {node}; and test $position {comparison} {position}; set target {param_id + offset}; end"
                        )
                        position += 1
            if (command.is_group or command.subcommands) and command.arguments:
                condition = (
                    "true"
                    if any(p.nargs == -1 for p in command.arguments)
                    else f"test $position -lt {position}"
                )
                operands.append(
                    f"if test $node -eq {node}; and {condition}; set ended 1; set position (math $position + 1); continue; end"
                )
            command_names = []
            command_helps = []
            for child_name, child in command.subcommands.items():
                children.append(
                    f'if test "$node:$word" = {self.quote(f"{node}:{child_name}")}; set node {ids[child.path]}; set position 0; set ended 0; continue; end'
                )
                command_names.append(child_name)
                command_helps.append(child.help if self.options.include_help else "")

            def values(words: list[str]) -> str:
                return " ".join(self.quote(word) for word in words)

            suggestions.append(
                f"case {node}\nset candidates {values(command_names)}\nset descriptions {values(command_helps)}\n"
                f"if test $ended -eq 0; and string match -q -- '-*' \"$current\"\n"
                f"set candidates {values(flags)}\nset descriptions {values(descriptions)}\nend"
            )
        actions = [
            f"case {i}; {self._value_action(param, tree)}"
            for i, param in enumerate(params)
        ]
        runtime = _RUNTIME.replace("@NAME@", name)
        for marker, cases in (
            ("OPTIONS", options),
            ("CHILDREN", children),
            ("GROUPS", groups),
            ("OPERANDS", operands),
            ("ARGUMENTS", arguments),
            ("SUGGESTIONS", suggestions),
            ("ACTIONS", actions),
        ):
            runtime = runtime.replace(f"@{marker}@", "\n".join(cases))
        runtime = "\n".join(line.rstrip() for line in runtime.splitlines()) + "\n"
        banner = ""
        if self.options.banner:
            banner = "# Generated - do not edit.\n"
            if self.options.regenerate_command:
                self.quote(self.options.regenerate_command)
                banner += f"# Regenerate: {self.options.regenerate_command}\n"
            if self.options.include_version:
                from importlib.metadata import version

                banner += f"# typer-static-completion {version('typer-static-completion')}; typer {version('typer')}\n"
        return banner + runtime + f"complete -c {prog} -f -a '({name})'\n"


_RUNTIME = r"""function @NAME@_option
@OPTIONS@
    printf '%s\n' -1 0
end

function @NAME@
    set -l tokens (commandline -xpc)
    set -l current (commandline -ct)
    set -l unescaped (string unescape -- "$current")
    if test (count $unescaped) -eq 1
        set current "$unescaped"
    end
    set -l node 0
    set -l position 0
    set -l pending -1
    set -l remaining 0
    set -l ended 0
    for word in $tokens[2..-1]
        if test $pending -ge 0
            set remaining (math $remaining - 1)
            if test $remaining -gt 0
                set pending (math $pending + 1)
            else
                set pending -1
            end
            continue
        end
        if test "$word" = --; and test $ended -eq 0
            set ended 1
            continue
        end
        if string match -qr '^-.+' -- "$word"; and test $ended -eq 0
            set -l flag (string split -m 1 = -- "$word")[1]
            set -l info (@NAME@_option $node "$flag")
            if test $info[1] -ge 0
                set -l consumed 0
                string match -q '*=*' -- "$word"; and set consumed 1
                set remaining (math $info[2] - $consumed)
                if test $remaining -gt 0
                    set pending (math $info[1] + $consumed)
                end
                continue
            end
            if not string match -q -- '--*' "$word"
                set -l rest (string sub -s 2 -- "$word")
                while test -n "$rest"
                    set flag -(string sub -l 1 -- "$rest")
                    set rest (string sub -s 2 -- "$rest")
                    set info (@NAME@_option $node "$flag")
                    if test $info[1] -lt 0
                        return
                    end
                    if test $info[2] -gt 0
                        set -l consumed 0
                        test -n "$rest"; and set consumed 1
                        set remaining (math $info[2] - $consumed)
                        if test $remaining -gt 0
                            set pending (math $info[1] + $consumed)
                        end
                        break
                    end
                end
                continue
            end
            return
        end
@OPERANDS@
@CHILDREN@
        switch $node
@GROUPS@
        end
        set position (math $position + 1)
    end
    set -l target $pending
    set -l prefix ''
    set -l candidates
    set -l descriptions
    set -l file_mode ''
    set -l choice_mode ''
    if test $target -lt 0; and test $ended -eq 0
        if string match -q -- '--*=*' "$current"
            set -l parts (string split -m 1 = -- "$current")
            set -l info (@NAME@_option $node "$parts[1]")
            test $info[2] -gt 0; or return
            set target $info[1]
            set prefix "$parts[1]="
            set current "$parts[2]"
        else if string match -qr '^-[^-].*' -- "$current"
            set -l rest (string sub -s 2 -- "$current")
            set -l attached -
            while test -n "$rest"
                set -l flag -(string sub -l 1 -- "$rest")
                set attached "$attached"(string sub -l 1 -- "$rest")
                set rest (string sub -s 2 -- "$rest")
                set -l info (@NAME@_option $node "$flag")
                if test $info[1] -lt 0
                    break
                end
                if test $info[2] -gt 0
                    set target $info[1]
                    set prefix "$attached"
                    set current "$rest"
                    break
                end
            end
        end
    end
    if test $target -lt 0
        switch $node
@SUGGESTIONS@
        end
        if test $ended -eq 1; or not string match -q -- '-*' "$current"
@ARGUMENTS@
        end
    end
    if test $target -ge 0
        set candidates
        set descriptions
        switch $target
@ACTIONS@
        end
    end
    set -l index 1
    for candidate in $candidates
        set -l match_candidate "$candidate"
        set -l match_current "$current"
        if test "$choice_mode" = insensitive
            set match_candidate (string lower -- "$candidate")
            set match_current (string lower -- "$current")
        end
        if test -z "$choice_mode"; or string match -qr -- '^'(string escape --style=regex -- "$match_current") "$match_candidate"
            printf '%s\t%s\n' "$prefix$candidate" "$descriptions[$index]"
        end
        set index (math $index + 1)
    end
    if test -n "$file_mode"
        set -l escaped (string escape -- "$current")
        set -l paths
        if test "$file_mode" = directory
            set paths (__fish_complete_directories "$escaped")
        else
            set paths (__fish_complete_path "$escaped")
        end
        for candidate in $paths
            printf '%s\n' "$prefix$candidate"
        end
    end
end
"""
