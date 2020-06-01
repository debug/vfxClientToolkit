import glob
import os
import datetime


import urllib

from urllib import parse

from http.cookiejar import CookieJar, Cookie

from vfxClientToolkit.api.config import ConfigBundle
import vfxClientToolkit.api.sg as vfxSG

cb = ConfigBundle()
CONFIG_DATA = cb.getContexts()

LOCATION = os.path.split(os.path.realpath(__file__))[0]


class AbstractEntity(object):
    def __init__(self, infoDict, sgHandle):
        self.__info = infoDict
        self.__sgHandle = sgHandle

    @property
    def info(self):
        return self.__info

    def getFields(self, typeIn=None):
        if typeIn == None:
            allFields = []
            fields = self.sgHandle.schema_field_read(self.TYPE)
            for field in fields:
                allFields.append(field)
            return allFields

        else:
            allFields = []
            fields = self.sgHandle.schema_field_read(typeIn)
            for field in fields:
                allFields.append(field)
            return allFields

    @property
    def sgHandle(self):
        return self.__sgHandle

    def getProject(self):
        filters = [["name", "is", CONFIG_DATA["shotgun"]["settings"]["project_name"]]]
        fields = ["id", "name"]
        sg_project = self.sgHandle.find_one("Project", filters, fields)

        return sg_project


class Sequence(AbstractEntity):

    TYPE = "Sequence"

    def __init__(self, infoDict, sgHandle):
        AbstractEntity.__init__(self, infoDict, sgHandle)

    @property
    def code(self):
        """
        Name of sequence.

        Returns:
            str: Name of sequence.

        """
        return self.info["code"]

    def getShots(self):
        """
        Collects all shots linked to sequence.

        Returns:
            list: List of `vfxClientToolkit.api.entities.Shot` objects.

        """
        return vfxSG.getShotsBySequence(self.code)


class Shot(AbstractEntity):

    TYPE = "Shot"

    def __init__(self, infoDict, sgHandle):
        AbstractEntity.__init__(self, infoDict, sgHandle)

    @property
    def code(self):
        """
        Name of sequence.

        Returns:
            str: Name of sequence.

        """
        return self.info["code"]

    def getProject(self):
        """
        Gets project associated with this shot.

        Returns:
            dict: Shotgun dictionary entity info.

        """
        filters = [["name", "is", CONFIG_DATA["shotgun"]["settings"]["project_name"]]]
        fields = ["id", "name"]
        sg_project = self.sgHandle.find_one("Project", filters, fields)

        return sg_project

    def getVersions(self, customFilters=[]):
        """
        Returns all versions associated with shot instance.

        Returns:
            list: List of `vfxClientToolkit.api.entities.Version` objects.

        """
        sorting = [{"column": "created_at", "direction": "desc"}]
        versionObjs = []

        filters = [["name", "is", CONFIG_DATA["shotgun"]["settings"]["project_name"]]]
        fields = ["id", "name"]
        sg_project = self.sgHandle.find_one("Project", filters, fields)

        filters = [
            [
                "project",
                "is",
                {"type": "Project", "name": sg_project["name"], "id": sg_project["id"]},
            ],
            ["code", "is", self.code],
        ]
        fields = ["id", "code", "sg_task"]
        sg_shot = self.sgHandle.find_one("Shot", filters, fields)

        versionFilters = [
            [
                "entity",
                "is",
                {"type": "Shot", "code": sg_shot["code"], "id": sg_shot["id"]},
            ]
        ]

        for fil in customFilters:
            versionFilters.append(fil)

        fields = self.getFields()
        fields.append("sg_task")
        fields.append("sg_path_to_movie")
        fields.append("sg_path_to_frames")
        fields.append("sg_temp_delivery_1")
        fields.append("sg_temp_delivery_2")
        fields.append("sg_final")
        fields.append("sg_status_list")
        fields.append("sg_deliver_to_di")
        shotVersions = self.sgHandle.find("Version", versionFilters, fields, sorting)

        for version in shotVersions:
            versionObjs.append(Version(version, self.sgHandle))

        return versionObjs

    def getVersion(self, versionName):
        """
        Return named version

        Args:
            param1 (str): Name of version.

        Returns:
            vfxClientToolkit.api.entities.Version: Matching version entity.

        """
        for version in self.versions:
            if version.name == versionName:
                return version

    def getVersionsByDept(self, dept):
        """
        Return versions based on department.

        Args:
            param1 (str): Short code for department (e.g cmp, lgt etc).

        Returns:
            list: List of matching `vfxClientToolkit.api.entities.Version` objects.

        """
        collectedVersions = []
        for version in self.getVersions():
            if version.task == dept:
                collectedVersions.append(version)

        return collectedVersions

    def getTasks(self):
        """
        Return versions based on department.

        Args:
            param1 (str): Short code for department (e.g cmp, lgt etc).

        Returns:
            list: List of matching `vfxClientToolkit.api.entities.Version` objects.

        """
        sgTasks = self.sgHandle.find(
            "Task",
            [
                ["project.Project.name", "is", CONFIG_DATA["shotgun"]["project_name"]],
                ["code", "is", self.code],
            ],
            ["code"],
        )
        return sgTasks

    def getOrCreateTask(self, task, vendorInfo):
        """
        Gets or creates a task with the provided information.

        Args:
            param1 (str): Task name.
            param1 (dict): Vendor info.

        Returns:
            dict: Shotgun dictionary task info.

        """
        filters = [["entity", "is", {"type": "Shot", "id": self.info["id"]}]]
        fields = [
            "content",
            "start_date",
            "due_date",
            "upstream_tasks",
            "downstream_tasks",
            "dependency_violation",
            "pinned",
        ]

        results = self.sgHandle.find("Task", filters, fields)

        for taskResult in results:
            if taskResult["content"] == task:
                return taskResult

        data = {
            "project": {"type": "Project", "id": self.getProject()["id"]},
            "content": task,
            #'task_assignees': [{'type':'HumanUser', 'id': vendorInfo['id']}],
            "entity": {"type": "Shot", "id": self.info["id"]},
        }

        result = self.sgHandle.create("Task", data)

        return result

    def createVersion(
        self, metadata, pathToMov, task, vendor, pathToFrames=None, firstLastFrame=None
    ):
        """
        """
        project = self.getProject()
        task = self.getOrCreateTask(task, vendor)

        if pathToFrames == None:
            pathToFrames = ""

        data = {
            "project": {"type": "Project", "id": project["id"]},
            "code": metadata["version_name"],
            "description": metadata["submission_notes"],
            "sg_status_list": "rev",
            "sg_path_to_movie": pathToMov,
            "sg_movie_has_slate": True,
            #'sg_last_frame': firstLastFrame[0],
            #'sg_first_frame': firstLastFrame[1],
            "sg_path_to_frames": pathToFrames,
            "entity": {"type": "Shot", "id": self.info["id"]},
            "sg_task": {"type": "Task", "id": task["id"]},
        }
        #'user': {'type': 'HumanUser', 'id': vendor['id']} }

        result = self.sgHandle.create("Version", data)

        return Version(result, self.sgHandle)

    @property
    def vendor(self):
        return self.info["sg_vendor"]

    @property
    def vendorGroups(self):
        return self.info["sg_vendor_groups"]

    @property
    def status(self):
        return self.info["sg_status_list"]

    @property
    def handles(self):
        return self.info["sg_handle"]

    @property
    def headIn(self):
        return self.info["sg_head_in"]

    @property
    def tailOut(self):
        return self.info["sg_tail_out"]


class Version(AbstractEntity):

    TYPE = "Version"

    def __init__(self, infoDict, sgHandle):
        AbstractEntity.__init__(self, infoDict, sgHandle)

    @property
    def movPath(self):
        if self.info["sg_path_to_movie"] != None:
            movList = glob.glob(
                "{0}/*.mov".format(
                    self.info["sg_path_to_movie"].replace(
                        CONFIG_DATA["filesystem"]["settings"]["posix_prefix"],
                        "/Volumes",
                    )
                )
            )

            return movList[0]

    @property
    def framePath(self):
        return self.info["sg_path_to_frames"]

    @property
    def shot(self):
        return vfxSG.getShot(self.name.split("_")[0], self.sgHandle)

    @property
    def vendorGroups(self):
        return self.shot.vendorGroups

    def uploadMov(self, movPath):
        self.sgHandle.upload(
            "Version", self.info["id"], movPath, field_name="sg_uploaded_movie"
        )
        # os.system("python3 {path}/uploadSG.py --id {id} --mov {mov}".format(path=LOCATION, id=self.info['id'], mov=movPath))

    def getNotes(self):
        noteObjs = []
        for note in self.info["open_notes"]:

            noteInfo = self.sgHandle.find_one(
                "Note",
                [["id", "is", note["id"]]],
                ["id", "url", "attachments", "content", "user", "created_at"],
            )
            noteObjs.append(Note(noteInfo, self.sgHandle))

        return noteObjs

    @property
    def pathToMov(self):
        return self.info["sg_path_to_movie"]

    @property
    def name(self):
        return self.info["code"]

    @property
    def task(self):
        try:
            return self.info["sg_task"]["name"]
        except:
            return ""

    @property
    def status(self):
        if (
            self.info["sg_status_list"]
            in CONFIG_DATA["shotgun"]["settings"]["version_status_mapping"]
        ):
            return CONFIG_DATA["shotgun"]["settings"]["version_status_mapping"][
                self.info["sg_status_list"]
            ]

    def setAttribute(self, attrName, attrValue):
        data = {attrName: attrValue}
        self.sgHandle.update("Version", self.info["id"], data)


class Playlist(AbstractEntity):
    def __init__(self, infoDict, sgHandle):
        AbstractEntity.__init__(self, infoDict, sgHandle)

    @property
    def name(self):
        return self.info["code"]

    def getVersions(self):
        #        filters = [
        #            ['name', 'is', CONFIG_DATA['shotgun']['settings']['project_name']]
        #        ]
        #        fields = ['id', 'name']
        #
        sgProject = self.sgHandle.find_one(
            "Project",
            [["name", "is", CONFIG_DATA["shotgun"]["settings"]["project_name"]]],
        )

        linked_shot = {"type": "Playlist", "id": self.info["id"]}

        version_filters = [
            ["project", "is", {"type": "Project", "id": sgProject["id"]}],
            ["playlists", "is", linked_shot],
        ]

        linked_versions = self.sgHandle.find(
            "Version",
            version_filters,
            [
                "id",
                "code",
                "type",
                "open_notes",
                "sg_status_list",
                "entity",
                "sg_path_to_movie",
                "sg_vendor_groups",
            ],
        )

        versionObjs = []

        for version in linked_versions:
            versionObj = Version(version, self.sgHandle)
            versionObjs.append(versionObj)

        return versionObjs

    @staticmethod
    def createPlaylist(name, versions):
        sgHandle = vfxSG.getShotgunHandle()
        baseName = os.path.basename(name)
        dateDir = baseName.split("_")[0]
        dateTimeObj = datetime.datetime.strptime(dateDir, "%Y%m%d")
        versions_list = [{"type": "Version", "id": x} for x in versions]
        project = sgHandle.find(
            "Project",
            [["name", "is", CONFIG_DATA["shotgun"]["settings"]["project_name"]]],
        )
        data = {
            "project": {"type": "Project", "id": project[0]["id"]},
            "code": baseName,
            "description": "",
            "versions": versions_list,
            "sg_date_and_time": dateTimeObj,
        }

        playlist = sgHandle.create("Playlist", data)
        return playlist


class Note(AbstractEntity):
    def __init__(self, infoDict, sgHandle):
        AbstractEntity.__init__(self, infoDict, sgHandle)

    @property
    def attachments(self):
        project = self.getProject()
        attachmentObjs = []
        for attachment in self.info["attachments"]:
            filters = [["id", "is", attachment["id"]], ["project", "is", project]]

            attachmentInfo = self.sgHandle.find_one(
                "Attachment", filters, self.getFields(typeIn="Attachment")
            )
            attachmentInfo["name"] = attachment["name"]
            attachmentObjs.append(Attachment(attachmentInfo, self.sgHandle))
        return attachmentObjs

    @property
    def author(self):
        return self.info["user"]

    @property
    def content(self):
        return self.info["content"]

    @property
    def createdAt(self):
        return self.info["created_at"]


class Attachment(AbstractEntity):
    def __init__(self, infoDict, sgHandle):
        AbstractEntity.__init__(self, infoDict, sgHandle)

    def download(self, outputDir):

        filePath = os.path.join(outputDir, self.info["name"])

        sid = self.sgHandle.get_session_token()
        domain = parse.urlparse(self.sgHandle.base_url)[1].split(":", 1)[0]
        cj = CookieJar()
        c = Cookie(
            "0",
            "_session_id",
            sid,
            None,
            False,
            domain,
            False,
            False,
            "/",
            True,
            False,
            None,
            True,
            None,
            None,
            {},
        )
        cj.set_cookie(c)
        cookie_handler = urllib.request.HTTPCookieProcessor(cj)
        urllib.request.install_opener(urllib.request.build_opener(cookie_handler))
        url = "%s/file_serve/attachment/%s" % (self.sgHandle.base_url, self.info["id"])
        request = urllib.request.Request(url)
        request.add_header(
            "User-agent",
            "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.5; en-US; rv:1.9.0.7) Gecko/2009021906 Firefox/3.0.7",
        )

        result = urllib.request.urlopen(request)
        f = open(filePath, "wb")
        f.write(result.read())
        f.close()

        return filePath


class Vendor(AbstractEntity):
    def __init__(self, infoDict, sgHandle):
        AbstractEntity.__init__(self, infoDict, sgHandle)

    @property
    def name(self):
        return self.info["name"]

    @property
    def firstName(self):
        return self.info["firstname"]

    @property
    def lastName(self):
        return self.info["lastname"]

    @property
    def tags(self):
        return self.info["tags"]


if __name__ == "__main__":
    pass
