import re
import datetime
import ssl

import shotgun_api3
from vfxClientToolkit.api.config import ConfigBundle
import vfxClientToolkit.api.entities as vfxEntities

ssl._create_default_https_context = ssl._create_unverified_context

cb = ConfigBundle()
CONFIG_DATA = cb.getContexts()


def getShotgunHandle():
    """
    Returns `shotgun_api3.Shotgun` object using the API key from the configuration files.

    Returns:
        shotgun_api3.shotgun.Shotgun: Configured Shotgun object.

    """
    sg = shotgun_api3.Shotgun(
        CONFIG_DATA["shotgun"]["settings"]["server"],
        script_name=CONFIG_DATA["shotgun"]["settings"]["script_name"],
        api_key=CONFIG_DATA["shotgun"]["settings"]["api_key"],
    )
    return sg


def getPlaylists(sg):
    """
    Returns all playlists based on the show specified in the configuration file(s).

    Args:
        param1 (shotgun_api3.Shotgun): Shotgun DB Object.

    Returns:
        list: List of dictionaries with Shotgun entity information.

    """
    sgPlaylists = sg.find(
        "Playlist",
        [
            [
                "project.Project.name",
                "is",
                CONFIG_DATA["shotgun"]["settings"]["project_name"],
            ]
        ],
        ["code"],
    )
    playlistObjs = []
    for playlist in sgPlaylists:
        playlistObjs.append(vfxEntities.Playlist(playlist, sg))

    playlistObjs.reverse()
    return playlistObjs


def getProject():
    """
    Returns Shotgun dictionary entity based on defined project in configuration file.

    Returns:
        dict: Shotgun entity information.

    """
    sgHandle = getShotgunHandle()
    filters = [["name", "is", CONFIG_DATA["shotgun"]["settings"]["project_name"]]]
    fields = ["id", "name"]
    sg_project = sgHandle.find_one("Project", filters, fields)

    return sg_project


def getSequences():
    """
    Collects and returns all sequences from the configured Shotgun projet.

    Returns:
        list: List of `vfxClientToolkit.api.entities.Sequence` objects.

    """
    seqObjs = []
    sg = getShotgunHandle()

    sequences = sg.find(
        "Sequence",
        [
            [
                "project.Project.name",
                "is",
                CONFIG_DATA["shotgun"]["settings"]["project_name"],
            ]
        ],
        ["code"],
    )
    for sequence in sequences:
        seqObjs.append(vfxEntities.Sequence(sequence, sg))

    return seqObjs


def getSequence(sequenceName):
    """
    Returns sequence object based upon specified name.

    Args:
        param1 (str): Name of sequence.

    Returns:
        vfxClientToolkit.api.entities.Sequence: Sequence object that matches provided name.

    """
    for sequence in getSequences():
        if sequence.name == sequenceName:
            return sequence


def getShotsBySequence(sequenceCode):
    """
    Collects and returns list of `vfxClientToolkit.api.entities.Shot` objects that below to provided sequence name.

    Args:
        param1 (str): Name of sequence.

    Returns:
        list: List of Shot entities.

    """
    sg = getShotgunHandle()
    shotObjs = []

    sgShots = sg.find(
        "Shot",
        [
            [
                "project.Project.name",
                "is",
                CONFIG_DATA["shotgun"]["settings"]["project_name"],
            ],
            ["sg_sequence.Sequence.code", "is", sequenceCode],
        ],
        [
            "code",
            "sg_status_list",
            "sg_handle",
            "sg_vendor",
            "sg_head_in",
            "sg_tail_out",
            "sg_head_in",
            "sg_tail_out",
        ],
    )

    for shotInfo in sgShots:
        shotObjs.append(vfxEntities.Shot(shotInfo, sg))

    return shotObjs


def getShot(shotName, sg):
    """
    Collects and returns `vfxClientToolkit.api.entities.Shot` object.

    Args:
        param1 (str): Name of shot.
        param2 (shotgun_api3.shotgun.Shotgun): Shotgun handle.

    Returns:
        vfxClientToolkit.api.entities.Shot: Shot object.

    """
    sgShot = sg.find(
        "Shot",
        [
            [
                "project.Project.name",
                "is",
                CONFIG_DATA["shotgun"]["settings"]["project_name"],
            ],
            ["code", "is", shotName],
        ],
        [
            "code",
            "sg_vendor_groups",
            "sg_status_list",
            "sg_handle",
            "sg_head_in",
            "sg_tail_out",
        ],
    )

    if sgShot != []:
        shotObj = vfxEntities.Shot(sgShot[0], sg)
        return shotObj
    else:
        return None


def getVersion(name, sg):
    """
    Collects and returns `vfxClientToolkit.api.entities.Version` object.

    Args:
        param1 (str): Name of version.
        param2 (shotgun_api3.shotgun.Shotgun): Shotgun handle.

    Returns:
        vfxClientToolkit.api.entities.Version: Version object.

    """
    fields = getFields("Shot", sg)
    fields.append("sg_path_to_frames")
    version = sg.find_one("Version", [["code", "is", name]], fields)
    versionObj = vfxEntities.Version(version, sg)
    if version == None:
        return None
    else:
        return versionObj


def getVersionsByAttr(attrs, sg):
    """
    Returns list of `vfxClientToolkit.api.entities.Version` objects that match the attribute filter provided.

    Args:
        param1 (list): Filter attribute.
        param2 (shotgun_api3.shotgun.Shotgun): Shotgun handle.

    Returns:
        list: Version objects in list that match filter criteria.

    """
    fields = getFields("Version", sg)
    versionObjs = []
    versions = sg.find(
        "Version",
        [
            [
                "project.Project.name",
                "is",
                CONFIG_DATA["shotgun"]["settings"]["project_name"],
            ],
            attrs,
        ],
        fields,
    )

    for version in versions:
        versionObjs.append(vfxEntities.Version(version, sg))

    return versionObjs


def getShotsByAttr(attrs, sg):
    """
    Returns list of `vfxClientToolkit.api.entities.Version` objects that match the attribute filter provided.

    Args:
        param1 (list): Filter attribute.
        param2 (shotgun_api3.shotgun.Shotgun): Shotgun handle.

    Returns:
        list: Version objects in list that match filter criteria.

    """
    fields = getFields("Shot", sg)
    shotObjs = []
    shots = sg.find(
        "Shot",
        [
            [
                "project.Project.name",
                "is",
                CONFIG_DATA["shotgun"]["settings"]["project_name"],
            ],
            attrs,
        ],
        fields,
    )

    for shot in shots:
        shotObjs.append(vfxEntities.Shot(shot, sg))

    return shotObjs


def getFields(entityName, sg):
    """
    Returns list of entity attributes based on the provided entity type.

    Args:
        param1 (str): Entity name.
        param2 (shotgun_api3.shotgun.Shotgun): Shotgun handle.

    Returns:
        list: List of entity attributes.

    """
    allFields = []
    fields = sg.schema_field_read(entityName)
    for field in fields:
        allFields.append(field)
    return allFields


def createPlaylist(name, versions):
    """
    Creates playlist and adds provided versions to newly created list.

    Args:
        param1 (str): Name of playlist (note: this should have the date provided in the following notation YYYYMMDD).
        param2 (list): List of `vfxClientToolkit.api.entities.Version` objects.

    Returns:
        vfxClientToolkit.api.entities.Playlist: Newly created playlist object.

    """
    sgHandle = getShotgunHandle()
    now = datetime.datetime.now()

    matchObj = re.match(str(name), "([0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9])_(.+)")
    if matchObj != None:
        name = "{0}_{1}".format(matchObj.groups()[1], matchObj.groups()[0])

    versions_list = [{"type": "Version", "id": x} for x in versions]
    project = sgHandle.find(
        "Project", [["name", "is", CONFIG_DATA["shotgun"]["settings"]["project_name"]]]
    )
    data = {
        "project": {"type": "Project", "id": project[0]["id"]},
        "code": name,
        "description": "",
        "versions": versions_list,
        "sg_date_and_time": now,
    }

    playlist = sgHandle.create("Playlist", data)
    return playlist


def getPlate(plateName, sg):
    """
    Collects plate from Shotgun.

    Args:
        param1 (str): Plate name.
        param2 (shotgun_api3.shotgun.Shotgun): Shotgun handle.

    Returns:
        dict: Shotgun dictionary with entity info.

    """
    sgPlate = sg.find(
        "Plate",
        [
            [
                "project.Project.name",
                "is",
                CONFIG_DATA["shotgun"]["settings"]["projectName"],
            ],
            ["code", "is", plateName],
        ],
        ["code"],
    )

    return sgPlate


def createDeliveryEntity(title, addressedTo, deliveryMethod, sg):
    """
    Creates delivery entitiy in Shotgun.

    Args:
        param1 (str): Delivery title.
        param2 (str):shotgun.Shotgun): Addressed to.
        param3 (str): Delivery method.
        param4 (shotgun_api3.shotgun.Shotgun): Shotgun handle.

    Returns:
        dict: Shotgun dictionary with entity info.

    """
    project = sg.find(
        "Project", [["name", "is", CONFIG_DATA["shotgun"]["settings"]["project_name"]]]
    )
    data = {
        "title": title,
        "addressings_to": addressedTo,
        "sg_delivery_method": deliveryMethod,
        "project": {"type": "Project", "id": project[0]["id"]},
    }
    entity = sg.create("Delivery", data)
    return entity


def getAllDeliveries(sg):
    """
    Returns all delivery entities in Shotgun.

    Args:
        param1 (shotgun_api3.shotgun.Shotgun): Shotgun handle.

    Returns:
        dict: Shotgun dictionary with entity info.

    """
    deliveries = sg.find(
        "Delivery",
        [
            [
                "project.Project.name",
                "is",
                CONFIG_DATA["shotgun"]["settings"]["project_name"],
            ]
        ],
        ["code"],
    )
    indices = []
    for delivery in deliveries:
        indices.append(delivery["id"])

    indices.sort()
    indices.reverse()
    if indices == []:
        return 1
    else:
        return indices[0]


def schemaRead(entityType, fieldName):
    """
    Returns all delivery entities in Shotgun.

    Args:
        param1 (shotgun_api3.shotgun.Shotgun): Shotgun handle.

    Returns:
        dict: Shotgun dictionary with entity info.

    """
    sgHandle = getShotgunHandle()
    schema = sgHandle.schema_field_read(entityType, fieldName)
    values = schema["sg_status_list"]["properties"]["display_values"]["value"]

    return values


def getVendors():
    """
    Returns all delivery entities in Shotgun.

    Args:
        param1 (shotgun_api3.shotgun.Shotgun): Shotgun handle.

    Returns:
        dict: Shotgun dictionary with entity info.

    """

    sgHandle = getShotgunHandle()
    fields = ["id", "name", "permission_rule_set", "firstname", "lastname", "tags"]

    filters = [
        [
            "permission_rule_set",
            "is",
            {"id": 13, "name": "Vendor", "type": "PermissionRuleSet"},
        ]
    ]

    vendors = sgHandle.find("HumanUser", filters, fields)

    vendorObjs = []

    for vendor in vendors:
        vendorObjs.append(vfxEntities.Vendor(vendor, sgHandle))

    return vendorObjs


if __name__ == "__main__":
    print(getVendors()[3].info)
    pass
