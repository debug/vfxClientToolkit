import nuke
import re
import glob
import os

ROOT = "/Volumes/RSO_3/shot/{seq}/{shot}/img/"


def autoContactSheet():

    nodeList = []
    xVals = []
    yVals = []

    for node in nuke.selectedNodes():

        if node.Class() == "Read":
            textValue = " [basename [file rootname [value [topnode].file]]]"
        else:
            textValue = " [value input.name]"

        # Creates a text node underneath every selected node & connects its input accordingly
        textNode = nuke.createNode("Text2")
        textNode.setInput(0, node)

        # Set the bbox of the text node to match the input format
        textNode["box"].setValue(0, 0)
        textNode["box"].setValue(0, 1)
        textNode["box"].setExpression("input.width", 2)
        textNode["box"].setExpression("input.height", 3)
        textNode["xjustify"].setValue("left")
        textNode["yjustify"].setValue("bottom")

        # Add relevant label as per the if/else statement above
        textNode["message"].setValue(textValue)
        textNode["shadow_opacity"].setValue("1")
        textNode["label"].setValue("[value message]")

        # Add selected nodes to a list
        nodeList.append(textNode)

        # Add the X and Y position of all selected nodes to their respective lists
        xVals.append(node["xpos"].value())
        yVals.append(node["ypos"].value())

    # Create a contact sheet node. This will come in with the new defaults we set above!
    cs = nuke.createNode("ContactSheet")

    # Add better knob defaults to Contact Sheet
    cs["width"].setExpression("input.width * columns * resMult")
    cs["height"].setExpression("input.height * rows * resMult")
    cs["roworder"].setValue("TopBottom")
    cs["colorder"].setValue("LeftRight")
    cs["rows"].setExpression("ceil(inputs/columns)")
    cs["columns"].setExpression("ceil(sqrt(inputs))")

    # Add custom knobs to the User tab to allow some control of our text nodes (User tab is created automatically by Nuke)
    cs.addKnob(nuke.Text_Knob("", ""))
    cs.addKnob(nuke.Double_Knob("resMult", "Resolution Multiplier"))
    cs["resMult"].setValue(1)
    cs.addKnob(nuke.Text_Knob("", ""))
    cs.addKnob(nuke.Boolean_Knob("showText", "Show Text", True))
    textBG_ops = "None", "Shadow", "Solid"
    cs.addKnob(nuke.Enumeration_Knob("textBG", "Text Background", textBG_ops))
    cs.addKnob(nuke.Double_Knob("textSize", "Text Size"))
    cs["textSize"].setValue(1)
    cs.addKnob(nuke.Text_Knob("", ""))

    iterator = 0

    # Add relevant expressions to our text nodes, so the Text size & background options work as expected
    for nodes in nodeList:

        cs.setInput(iterator, nodes)
        nodes["enable_background"].setExpression(
            cs["name"].value() + ".textBG == 2 ? 1 : 0"
        )
        nodes["enable_shadows"].setExpression(
            cs["name"].value() + ".textBG == 1 ? 1 : 0"
        )
        nodes["disable"].setExpression(cs["name"].value() + ".showText == 1 ? 0 : 1")
        nodes["global_font_scale"].setExpression(cs["name"].value() + ".textSize")

        iterator = iterator + 1

    # Find the average of all selected nodes' X and Y positions
    avgXpos = sum(xVals) / len(nodeList)
    avgYpos = sum(yVals) / len(nodeList)

    # Force set the position of our newly created contact sheet in the node graph
    cs["xpos"].setValue(avgXpos)
    cs["ypos"].setValue(avgYpos + 200)


def collectMovies(shots):
    dept = "cmp"

    subDirs = []
    dirDict = {}

    results = {}
    for shot in shots:
        results[shot] = []
        matchObj = re.match("([A-Za-z]{3}).+", shot)
        if matchObj != None:

            print(matchObj.groups())
            shotRoot = ROOT.format(seq=matchObj.groups()[0].lower(), shot=shot.upper())
            for item in glob.glob(shotRoot + "/*"):
                if os.path.basename(item) != ".DS_Store":
                    if os.path.isdir(item):
                        for subDir in glob.glob(item + "/*"):
                            subDirs.append(str(os.path.basename(subDir)))
                            dirDict[os.path.basename(subDir)] = os.path.abspath(subDir)
            subDirs.sort(key=natural_keys)

            subDirs.reverse()

            for dir in subDirs:
                if dept == "any":
                    movs = glob.glob(dirDict[dir] + "/mov/*.mov")
                    results[shot].append(movs)
                if dept == "plt":
                    pass
                if re.match(".+{0}.+".format(dept), dir) != None:
                    movs = glob.glob(dirDict[dir] + "/mov/*.mov")
                    results[shot].append(movs)

    return results


def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    return [atoi(c) for c in re.split(".+v[0-9][0-9][0-9]", text)]


if __name__ == "__main__":
    moo = collectMovies(["apc6190", "apc6370", "apc6210"])
    nodeStack = []
    for shot, item in moo.items():
        read = nuke.createNode("Read")
        read["file"].setValue(item[0][0])
        read.knob("selected").setValue(True)
        nodeStack.append(read)

    for node in nodeStack:
        print(node)
        nuke.toNode(node).setSelected(True)
        # print(item[0])
    # print(moo)
    autoContactSheet()
    # pass
