import re
import glob
import json
import csv
import os

from pathlib import Path

import pandas as pd

import vfxClientToolkit.api.sg as sg
import vfxClientToolkit.api.config as vfxConfig
from vfxClientToolkit.constants import METADATA_ORDER, SUPPORT_FILES_DIR, EXR_DIR

CONFIG_DATA = vfxConfig.getBundles()


def decomposeFileName(fileName):
    info = {}
    matchString = "([a-zA-Z][a-zA-Z][a-zA-Z])[0-9][0-9][0-9][0-9]_(.+)_(.+)"

    matchObj = re.match(matchString, fileName)
    info["shot"] = fileName.split("_")[0]
    info["seq"] = matchObj.groups()[0]
    info["dept"] = matchObj.groups()[1]
    info["version"] = matchObj.groups()[2]
    return info


def getFrameRange(sequence):
    if sequence != []:
        sequence.sort()
        matchFirstFrame = re.match(".+([0-9][0-9][0-9][0-9]).exr", sequence[0])
        matchLastFrame = re.match(".+([0-9][0-9][0-9][0-9]).exr", sequence[-1])
        return [matchFirstFrame.groups()[0], matchLastFrame.groups()[0]]


def getVendor(path):
    # vendorMapping = CONFIG_DATA['ingestIt']['settings']['vendor_mapping']

    vendors = sg.getVendors()
    vendorDict = {}

    matchStr = ".+("

    for vendor in vendors:
        matchStr = matchStr + "{0}|".format(vendor.tags[0]["name"])
        vendorDict[vendor.tags[0]["name"]] = vendor

    combinedString = matchStr[:-1] + ")_.+"

    matchObj = re.match(combinedString, path)
    print(combinedString, path)
    if matchObj != None:
        if matchObj.groups()[0] in vendorDict:
            return vendorDict[matchObj.groups()[0]]
        else:
            return None


def openMetadataManifest(path):
    for metadataFormat in METADATA_ORDER:
        for file in glob.glob("{0}/*.{1}".format(path, metadataFormat)):
            if metadataFormat == "xlsx":
                data = openExcelFile(file)
                return data
            elif metadataFormat == "csv":
                data = openCSVFile(file)
                return data
            elif metadataFormat == "json":
                data = openJSONFile(file)
                return data


def openExcelFile(filePath):
    manifest = []
    dataFrame = pd.read_excel(filePath)
    for index in dataFrame.index:
        data = {}
        data["version_name"] = dataFrame["Version Name"][index]
        data["submission_notes"] = dataFrame["Submission Notes"][index]
        data["dept"] = dataFrame["Dept"][index]
        data["date"] = dataFrame["Date"][index]
        data["shot"] = dataFrame["Shot"][index]

        manifest.append(data)

    return manifest


def openJSONFile(filePath):
    fh = open(filePath, "r")
    data = json.loads(fh.read())
    fh.close()
    return data


def openCSVFile(filePath):
    manifest = []
    rows = []
    data = []

    with open(filePath) as csvFile:
        csvReader = csv.reader(csvFile, delimiter=",")

        lineCount = 0
        for row in csvReader:
            if lineCount == 0:
                rows = row
                lineCount += 1
            else:

                data.append(row)
            lineCount += 1

    for row in data:
        rowData = {}
        rowData["version_name"] = row[0]
        rowData["shot"] = row[1]
        rowData["submission_notes"] = row[2]
        rowData["dept"] = row[3]
        rowData["date"] = row[4]
        manifest.append(rowData)

    return manifest


def addToDict(parentList, key, value, newKey, newValue):

    for item in parentList:
        if item[key] == value:
            item[newKey] = newValue

    return parentList


def buildExtendedManifest(path):
    shotgunHandle = sg.getShotgunHandle()
    pathObj = Path(path)
    manifest = openMetadataManifest(path)
    for movFile in glob.glob("{0}/*.mov".format(path)):

        fileName = os.path.basename(movFile)
        shotName = fileName.split("_")[0]
        versionName = os.path.splitext(fileName)[0]
        shotObj = sg.getShot(shotName, shotgunHandle)
        if shotObj != None:
            addToDict(manifest, "shot", shotName, "shot_entity", shotObj)
            addToDict(manifest, "shot", shotName, "mov_file", movFile)

            metaD = decomposeFileName(versionName)
            addToDict(manifest, "shot", shotName, "seq", metaD["seq"])
            addToDict(manifest, "shot", shotName, "dept", metaD["dept"])
            addToDict(manifest, "shot", shotName, "version_number", metaD["version"])

        if (pathObj / EXR_DIR).exists():
            if (pathObj / EXR_DIR / versionName).exists():
                addToDict(
                    manifest, "shot", shotName, "exrs", (pathObj / "EXR" / versionName)
                )
            else:
                addToDict(manifest, "shot", shotName, "exrs", None)
        else:
            addToDict(manifest, "shot", shotName, "exrs", None)

        if (pathObj / SUPPORT_FILES_DIR).exists():
            if (pathObj / SUPPORT_FILES_DIR / versionName).exists():
                addToDict(
                    manifest,
                    "shot",
                    shotName,
                    "support_files",
                    (pathObj / SUPPORT_FILES_DIR / versionName),
                )
            else:
                addToDict(manifest, "shot", shotName, "support_files", None)
        else:
            addToDict(manifest, "shot", shotName, "support_files", None)

    return manifest


if __name__ == "__main__":
    getVendor("")
