import sys
from qtpy import QtWidgets
from mailer import Mailer
from mailer import Message


def sendEmailTest(uiInstance):
    settings = uiInstance.getSettings()
    value, status = QtWidgets.QInputDialog.getText(
        uiInstance, "Input Dialog", "Enter email address:"
    )
    if status:
        message = Message(From=settings["username"], To=[value])
        message.Subject = "VFXClientToolkit - Email Test"
        message.Html = "If you can read this it's working.."
        sender = Mailer(host=settings["smtp"], port=settings["port"], use_tls=True)
        sender.login(settings["username"], settings["password"])
        sender.send(message)

        QtWidgets.QMessageBox().information(
            uiInstance, "Test Email Sent", "Test Email Sent"
        )
