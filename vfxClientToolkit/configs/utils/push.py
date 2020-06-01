from pushover import Client
from qtpy import QtWidgets


def sendTestPush(uiInstance):
    settings = uiInstance.getSettings()

    if settings["user"] != "" and settings["token"] != "":
        client = Client(settings["user"], api_token=settings["token"])
        client.send_message(
            "If you can read this it works!", title="VFXClientToolkit - Test Message"
        )

        QtWidgets.QMessageBox().information(
            uiInstance, "Test Message sent", "Test Message Sent"
        )
    else:
        QtWidgets.QMessageBox().warning(
            uiInstance, "Please complete all fields", "Please complete all fields."
        )
