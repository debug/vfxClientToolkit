import os
import glob

import dropbox

import vfxClientToolkit.api.config as vfxConfig

MUTE = False

UPLOAD_RETRIES = 2
IGNORE_FILES = [".DS_Store"]

CONFIG_DATA = vfxConfig.getBundles()


def uploadDir(directory, progressBarObj=None):

    dbx = dropbox.Dropbox(
        CONFIG_DATA["mrFilmOut"]["settings"]["dropbox"]["access_token"]
    ).with_path_root(
        dropbox.common.PathRoot.namespace_id(
            CONFIG_DATA["mrFilmOut"]["settings"]["dropbox"]["namespace_id"]
        )
    )
    logFilePath = os.path.join(directory, "upload_log.txt")
    fh = open(logFilePath, "w")
    logStr = str()

    i = 0
    for dir in glob.glob("{0}/*"):
        if os.isdir(dir):
            i = i + 1

    if progressBarObj != None:
        progressBarObj.setMaximum(i)

    j = 0
    for dir, dirs, files in os.walk(directory):
        for file in files:
            if file not in IGNORE_FILES:
                try:
                    file_path = os.path.join(dir, file)
                    dest_path = os.path.join(dir, file)
                    dest_path = dest_path.replace(
                        CONFIG_DATA["mrFilmOut"]["settings"]["default_write_location"],
                        "",
                    )
                    finalPath = os.path.join(
                        CONFIG_DATA["mrFilmOut"]["settings"]["dropbox_root"], dest_path
                    )

                    with open(file_path, "rb") as f:
                        dbx.files_upload(f.read(), finalPath, mute=MUTE)

                except Exception as err:
                    try:
                        print("Retrying %s\n%s" % (file, err))
                        file_path = os.path.join(dir, file)
                        dest_path = os.path.join(dir, file)
                        dest_path = dest_path.replace(
                            CONFIG_DATA["mrFilmOut"]["settings"][
                                "default_write_location"
                            ],
                            "",
                        )
                        finalPath = os.path.join(
                            CONFIG_DATA["mrFilmOut"]["settings"]["dropbox_root"],
                            dest_path,
                        )

                        with open(file_path, "rb") as f:
                            dbx.files_upload(f.read(), finalPath, mute=MUTE)

                    except:
                        print("Failed to upload %s\n%s" % (file, err))
                        logStr = logStr + "Failed Upload :: {0} - {1} \n".format(
                            file, err
                        )

        j = j + 1
        if progressBarObj != None:
            progressBarObj.setValue(j)

    fh.write(logStr)
    fh.close()

    return logFilePath


if __name__ == "__main__":
    #    uploadDir("/Users/dom/Desktop/donkey")

    CONFIG_DATA
