import shotgun_api3
from qtpy import QtWidgets


def testConnection(uiInstance):
    settings = uiInstance.getSettings()

    sg = shotgun_api3.Shotgun(
        settings["server"],
        script_name=settings["script_name"],
        api_key=settings["api_key"],
    )

    filters = [["name", "is", settings["project_name"]]]
    fields = ["id", "name"]
    sg_project = sg.find_one("Project", filters, fields)

    print(sg_project)

    if sg_project != None:
        QtWidgets.QMessageBox().information(
            uiInstance, "Connection Success", "Connection Success"
        )
    else:
        QtWidgets.QMessageBox().warning(
            uiInstance,
            "Connection Failure \n Please check settings",
            "Connection Failure \n Please check settings",
        )
