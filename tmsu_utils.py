import enum
import os
import subprocess as sp
import sys
from logging import getLogger
from typing import Iterable


class Tmsu:
    def __init__(self, tmsu: str, log=None):
        if log:
            self._logger = log
        else:
            self._logger = getLogger(f"{Tmsu.__module__}.{Tmsu.__name__}")
        self.tmsu = tmsu

    def info(self):
        try:
            r = self._cmd(["info"])
        except sp.CalledProcessError as e:
            if e.returncode == 1:  # database doesn't exist
                return None

        lines = r.splitlines()

        def psplit(l):
            return map(lambda x: x.strip(), l.split(":"))

        d = dict(map(psplit, lines))

        return {"root": d["Root path"], "size": d["Size"], "database": d["Database"]}

    def tags(self, file_name: str = ""):
        """Returns a list of tags. If file_name is provided, list item is a tuple of
        (tag, value) pair."""
        if file_name:
            # Note: tmsu behaves differently for 'tags' command when used
            # interactively and called from scripts. That's why we add '-n'.
            r = self._cmd(["tags", "-1", "-n", "never", file_name])
            tag_value = r.splitlines()
            # for tag in r.splitlines():
            #    tv = tag.split("=")
            #    if len(tv) > 1:
            #        tag_value.append((tv[0], tv[1]))
            #    else:
            #        tag_value.append((tv[0], ""))
            return tag_value
        else:
            return self._cmd(["tags"]).splitlines()

    def tag(self, files: Iterable[str], *tags: list[str], recursive: bool = False, **value: dict[str, str | None]):
        try:
            cmd = ["tag"]

            if recursive:
                cmd.append("--recursive")

            tags_to_add = ""
            if tags:
                tags_to_add = " ".join(tags)

            if value:
                tags_to_add = f"{tags_to_add} {
                    " ".join(map(lambda k, v: f'{k}={v}', value))}"

            if tags_to_add:
                cmd.extend(["--tags", f"{tags_to_add}"])

            cmd.extend(files)
            self._logger.debug(cmd)
            self._logger.debug(self._cmd(cmd))

            return True
        except sp.CalledProcessError as e:
            self._logger.error(f"Failed to tag file: {e}.")
            return False

    def untag(self, file_name: str, tag: str, value: str = ""):
        try:
            cmd = ["untag", file_name]
            if value:
                cmd.append(f"{tag}={value}")

            self._cmd(cmd)

            return True
        except sp.CalledProcessError as e:
            self._logger.error("Failed to untag file: {}.", e)
            return False

    def rename(self, tag: str, new: str, is_value: bool = False):
        try:
            cmd = ["rename"]

            if is_value:
                cmd.append("--value")

            cmd.extend([tag, new])
            self._cmd(cmd)

            return True
        except sp.CalledProcessError as e:
            self._logger.error("Failed to rename tag: {}.", e)
            return False

    def values(self, tag: str | None = None) -> list[str]:
        try:
            cmd = ["values"]

            if tag:
                cmd.append(tag)

            return self._cmd(cmd).splitlines()
        except sp.CalledProcessError as e:
            self._logger.error("Failed to get value list: {}.", e)
            return False

    def delete(self, tag: str):
        try:
            self._cmd(["delete", tag])
            return True
        except sp.CalledProcessError as e:
            self._logger.error("Failed to delete tag '{}': {}", tag, e)
            return False

    def _cmd(self, cmd: str | list[str]):
        if isinstance(cmd, str):
            cmd = f"tmsu {cmd}"
        elif isinstance(cmd, list):
            cmd = ["tmsu"] + cmd

        self._logger.info(cmd)

        return sp.run(cmd, stdout=sp.PIPE, stderr=sp.STDOUT, encoding="utf-8").stdout

    @staticmethod
    def findTmsu(*args, **kwargs):
        import shutil

        tmsu = shutil.which("tmsu")
        if tmsu:
            return Tmsu(tmsu, *args, **kwargs)
        else:
            return None
