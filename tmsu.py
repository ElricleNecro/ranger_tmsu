import os

from ranger.api.commands import Command

from .tmsu_utils import Tmsu


class tmsu_base(Command):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self._tmsu = Tmsu.findTmsu(self.log)


class tmsu_tag(tmsu_base):
    """:tmsu_tag

    Tags the current file with tmsu
    """

    def execute(self):
        if not self._tmsu:
            self.log.error("tmsu was not found.")
            self.fm.notify("tmsu was not found.")
            return

        self.log.info(f"{self.rest(1)} {type(self.rest(1))}")
        self.log.info(f"{self.fm.thistab.get_selection()}")

        tags = []
        kwargs = {}
        for arg in self.args[1:]:
            key, *value = arg.split("=")

            if "--recursive" == key:
                if value[0] in (None, "true", "True", "1"):
                    kwargs["recursive"] = True
                else:
                    kwargs["recursive"] = False
            elif value:
                kwargs[key] = value[0]
            else:
                tags.append(arg)

        self.log.info(tags)
        self.log.info(kwargs)
        self.log.info(list(map(lambda s: s.basename, self.fm.thistab.get_selection())))
        files = map(lambda s: s.basename, self.fm.thistab.get_selection())
        self._tmsu.tag(files, *tags, **kwargs)

    def tab(self, tabnum):
        """Complete with tags"""
        if not self._tmsu:
            self.log.error("tmsu was not found.")
            raise FileNotFoundError("tmsu")

        results = []
        if self.arg(0) == self.arg(-1):
            input_tag = ""
            index = 1
        else:
            input_tag = self.arg(-1)
            index = -1

        if input_tag.startswith("-"):
            results.append("--recursive=true")
            results.append("--recursive=false")

        if "=" in input_tag:
            tag, value = input_tag.split("=")
            for tag_value in self._tmsu.values(tag):
                if tag_value.startswith(value):
                    results.append(tag + "=" + tag_value)
        else:
            for tag in self._tmsu.tags():
                if tag.startswith(input_tag):
                    results.append(tag)
        return (self.start(index) + result for result in results)


class tmsu_untag(tmsu_base):
    """:tmsu_untag

    Untags the current file with tmsu
    """

    def execute(self):
        if not self._tmsu:
            self.log.error("tmsu was not found.")
            raise FileNotFoundError("tmsu")

        cf = self.fm.thisfile
        self._tmsu.untag(cf.basename, self.rest(1))

    def tab(self, tabnum):
        """Complete with tags"""
        if not self._tmsu:
            self.log.error("tmsu was not found.")
            raise FileNotFoundError("tmsu")

        results = []
        if self.arg(0) == self.arg(-1):
            input_tag = ""
            index = 1
        else:
            input_tag = self.arg(-1)
            index = -1
        cf = self.fm.thisfile

        for tag in self._tmsu.tags(fileName=cf.basename):
            if tag.startswith(input_tag):
                results.append(tag)
        return (self.start(index) + result for result in results)


class tmsu_ls(tmsu_base):
    """:tmsu_ls

    List tags of the current file with tmsu
    """

    def execute(self):
        if not self._tmsu:
            self.log.error("tmsu was not found.")
            raise FileNotFoundError("tmsu")

        cf = self.fm.thisfile
        tags = self._tmsu.tags(cf.basename)
        self.fm.notify(tags)
