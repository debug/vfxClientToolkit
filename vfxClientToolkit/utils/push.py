import vfxClientToolkit.api.config as vfxConfig
from pushover import Client

CONFIG_DATA = vfxConfig.getBundles()


def sendPushNotification(title, message):
    client = Client(
        CONFIG_DATA["push"]["settings"]["user"],
        api_token=CONFIG_DATA["push"]["settings"]["token"],
    )
    client.send_message(message, title=title)
