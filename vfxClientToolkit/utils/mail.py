from mailer import Mailer
from mailer import Message

import vfxClientToolkit.api.config as vfxConfig

CONFIG_DATA = vfxConfig.getBundles()


def sendMail(data, subject, recipients, attach=[]):
    """
    Sends HTML mail using credientals specified in the email configuration file.

    Args:
        param1 (str): HTML encoded into Python string object.
        param2 (str): Email subject line.
        param3 (list): List of recipients.
        attach (list): List of file paths to attach.

    Returns:
        none: Returns none.

    """

    message = Message(
        From=CONFIG_DATA["email"]["settings"]["username"],
        To=recipients,
        attachments=attach,
    )
    message.Subject = subject
    message.Html = data
    sender = Mailer(
        host=CONFIG_DATA["email"]["settings"]["smtp"],
        port=CONFIG_DATA["email"]["settings"]["port"],
        use_tls=True,
    )
    sender.login(
        CONFIG_DATA["email"]["settings"]["username"],
        CONFIG_DATA["email"]["settings"]["password"],
    )
    sender.send(message)


if __name__ == "__main__":
    sendMail("data", "moo", "dom@reality-debug.co.uk")
