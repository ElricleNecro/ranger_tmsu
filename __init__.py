from ranger.api import register_linemode
from ranger.core.linemode import LinemodeBase
from .tmsu import tmsu_tag, tmsu_untag, tmsu_ls


@register_linemode  # It may be used as a decorator too!
class TmsuLinemode(LinemodeBase):
    name = "tmsu"

    uses_metadata = False

    def filetitle(self, file, metadata):
        return file.relative_path + str(tmsu.tags(file))

    def infostring(self, file, metadata):
        return file.user
