from pushover import Pushover
import vfxClientToolkit.api.config as vfxConfig

CONFIG_DATA = vfxConfig.getBundles()

def sendPushNotification(title, message):
    po = Pushover(CONFIG_DATA['push']['settings']['token'])
    po.user(CONFIG_DATA['push']['settings']['user'])
    msg = po.msg(message)
    msg.set("vfxClientToolkit", title)
    po.send(msg)


