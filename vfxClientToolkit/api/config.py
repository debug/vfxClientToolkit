import json
import os
from os.path import expanduser
from pathlib import Path

import vfxClientToolkit
import vfxClientToolkit.api.logger as vfxLogger
from vfxClientToolkit.constants import CONFIG_DIR

HOME = Path(expanduser("~"))

CONFIG_TEMPLATE_DIR = Path(
    os.path.join(os.path.split(vfxClientToolkit.__file__)[0], "configs")
)
LOCAL_CONFIG_DIR = HOME / CONFIG_DIR

LOGGER = vfxLogger.getLogger()


class ConfigBundle(object):
    def __init__(self):
        self.__localConfigDirPresent = False
        if LOCAL_CONFIG_DIR.exists():
            self.__localConfigDirPresent = True
            LOGGER.debug("Config directory found")
        else:
            LOGGER.debug("Config directory missing")

    def getContexts(self, rollupConfigStack=True):
        data = {}
        if rollupConfigStack:
            if self.__localConfigDirPresent:
                for config in LOCAL_CONFIG_DIR.glob("*.json"):
                    fh = open(config, "r")
                    configData = json.loads(fh.read())
                    data[list(configData.keys())[0]] = configData[
                        list(configData.keys())[0]
                    ]
            else:
                pass
                # throw exception
        return data

    def getTemplates(self):
        templates = {}
        for config in CONFIG_TEMPLATE_DIR.glob("*.json"):
            fh = open(config, "r")
            configData = json.loads(fh.read())
            templates[list(configData.keys())[0]] = configData[
                list(configData.keys())[0]
            ]

        return templates


def getBundles():
    cb = ConfigBundle()
    data = cb.getContexts()
    return data


def getConfigTemplates():
    cb = ConfigBundle()
    data = cb.getTemplates()
    return data


if __name__ == "__main__":
    cb = ConfigBundle()

    data = cb.getContexts("shotgun")
    import pprint as pp

    pp.pprint(data)
