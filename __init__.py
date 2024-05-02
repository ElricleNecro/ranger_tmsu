from ranger.api import register_linemode
from ranger.core.linemode import LinemodeBase
from ranger.ext.human_readable import human_readable
from .tmsu import tmsu_tag, tmsu_untag, tmsu_ls
from .tmsu_utils import Tmsu

tmsu = Tmsu.findTmsu()


@register_linemode  # It may be used as a decorator too!
class TmsuLinemode(LinemodeBase):
    name = "tmsu"

    uses_metadata = False

    def filetitle(self, file, metadata):
        return file.relative_path

    def infostring(self, file, metadata):
        if file.stat is None:
            return "?"
        if file.is_directory and not file.cumulative_size_calculated:
            if file.size is None:
                sizestring = ""
            else:
                sizestring = file.size
        else:
            sizestring = human_readable(file.size)

        tagstring = str(tmsu.tags(file.basename))
        return "%s %s" % (sizestring, tagstring)
