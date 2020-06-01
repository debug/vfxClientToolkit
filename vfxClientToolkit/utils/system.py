import os
import glob
import shutil

import vfxClientToolkit.api.config as vfxConfig
from vfxClientToolkit.constants import SHOT_SEQ_STRUCTURE

CONFIG_DATA = vfxConfig.getBundles()


def copySupportFiles(path, file):

    if os.path.exists(path):
        combinedPath = os.path.join(
            CONFIG_DATA["filesystem"]["settings"]["project_tree_root"],
            SHOT_SEQ_STRUCTURE,
        )
        destinationPath = combinedPath.format(
            PROJECT=CONFIG_DATA["shotgun"]["settings"]["project_name"],
            SEQ=file["seq"].upper(),
            SHOT=file["shot"].upper(),
            DEPT=file["dept"],
        )
        destinationSupportPath = os.path.join(
            destinationPath, "{0}/SupportFiles".format(file["version_name"])
        )
        print(destinationSupportPath)
        try:
            os.mkdir(destinationSupportPath)
        except:
            pass

        try:
            shutil.copytree(path, destinationSupportPath)
        except:
            pass


def listIncomingDirectories():
    print(CONFIG_DATA["filesystem"]["settings"])
    dirs = []
    for path in glob.glob(
        "{0}/*".format(CONFIG_DATA["ingestIt"]["settings"]["incoming_root"])
    ):
        if os.path.isdir(path):
            dirs.append(path)
    dirs.sort()
    dirs.reverse()
    return dirs


def checkDriveMounts():
    if os.path.exists(
        CONFIG_DATA["ingestIt"]["settings"]["incoming_root"]
    ) and os.path.exists(CONFIG_DATA["filesystem"]["settings"]["project_tree_root"]):
        return True
    else:
        return False


def copyEXRs(path, file):
    if os.path.exists(path):

        exrs = glob.glob("{0}/*.exr".format(path))
        combinedPath = os.path.join(
            CONFIG_DATA["filesystem"]["settings"]["project_tree_root"],
            SHOT_SEQ_STRUCTURE,
        )
        destinationPath = combinedPath.format(
            PROJECT=CONFIG_DATA["shotgun"]["settings"]["project_name"],
            SEQ=file["seq"].lower(),
            SHOT=file["shot"].upper(),
            DEPT=file["dept"],
        )
        versionDir = os.path.join(
            destinationPath, "{0}/exrs".format(file["version_name"])
        )

        try:
            os.makedirs(versionDir)
        except:
            pass

        try:
            for exr in exrs:
                shutil.copy2(exr, versionDir)
        except:
            pass

        exrDestination = os.path.join(
            versionDir, "{0}.####.exr".format(file["version_name"])
        )

        return exrDestination


def copyMov(file, infoDict):
    combinedPath = os.path.join(
        CONFIG_DATA["filesystem"]["settings"]["project_tree_root"], SHOT_SEQ_STRUCTURE
    )
    destinationPath = combinedPath.format(
        PROJECT=CONFIG_DATA["shotgun"]["settings"]["project_name"],
        SEQ=infoDict["seq"],
        SHOT=infoDict["shot"].upper(),
        DEPT=infoDict["dept"],
    )
    try:
        os.makedirs(destinationPath)
    except:
        pass

    versionDir = os.path.join(
        destinationPath, "{0}/mov".format(infoDict["version_name"])
    )

    try:
        os.makedirs(versionDir)
    except:
        pass

    try:
        shutil.copy2(file, versionDir)
    except:
        pass

    return os.path.join(versionDir, os.path.basename(file))


def packageVersion(versionRoot, versionExportDir):
    try:
        shutil.copytree(versionRoot, versionExportDir)
        cdlExrs = os.path.join(versionExportDir, "cdl_exr")
        if os.path.exists(cdlExrs):
            shutil.rmtree(cdlExrs)
    except Exception:
        pass
