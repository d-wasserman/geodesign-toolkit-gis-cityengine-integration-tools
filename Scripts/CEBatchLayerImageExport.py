# --------------------------------
# Name: CEBatchLayerImageExport.py
# Purpose: Batch export of snapshots of data driven images.
# Current Owner: David Wasserman
# Last Modified: 5/10/2017
# Copyright:   (c) Co-Adaptive
# CityEngine Vs: 2016.1
# Python Version:   2.7
# License
# Copyright 2017 David J. Wasserman
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# --------------------------------

# Import Modules

from scripting import *

# get a CityEngine instance
ce = CE()
# Declare variables
outputFolder = "\BatchExport/"
width = 1920
height = 1080
fileType = ".png"
turnOffAllLayers=True
generateBoolean = False
deleteBoolean = False
iterateThroughBookMarksBoolean = False


# Turn off User Interface updates, or script might take forever.
# @noUIupdate
def turnLayersInvisible(layersList):
    """Turns off all layers within a CityEngine Scene from being visble."""
    print("Turning off visibility for all layers.")
    for layer in layersList:
        layer.setVisible(False)


def generateImagePath(baseFolderParam=ce.toFSPath("images"), outputDirParam="/BatchExport/", layerNameParam="ImageName",
                      bookmarkNameParam="", fileTypeParam=".png"):
    """Generates an image path that accounts for layer name, book mark name, and desired output directories. """
    adjustedLayerName = str(layerNameParam).replace(" ", "_")
    adjustedBookMarkName = str(bookmarkNameParam).replace(" ", "_")
    spacer = "_" if adjustedBookMarkName else ""
    return str(baseFolderParam) + str(outputDirParam) + adjustedLayerName + spacer + adjustedBookMarkName + str(
        fileTypeParam)


# @noUIupdate
def main():
    """ This function will export in batch images to the input outputFolder suggested resolution and file type can also 
    be declared."""
    layers = ce.getObjectsFrom(ce.scene, ce.isLayer)
    print(
        "There are " + str(len(layers) - 2) + " layers in the current scene.")  # -2 To remove Panorama and Scene Light
    counter = 0
    # Turns off visibility of all layers.
    if turnOffAllLayers:
        turnLayersInvisible(layers)
    else:
        print("Not turning off layers...")
    print("Iterating through all layers")
    for layer in layers:
        try:
            layerName = str(ce.getName(layer))
            if layerName == "Panorama" or layerName == "Scene Light":
                continue  # skip
            # print layer.getVisible()
            layer.setVisible(False)
            # print layer.getVisible()
            layer.setVisible(True)
            layerView = ce.getObjectsFrom(ce.get3DViews(), ce.isViewport)
            if len(layerView) < 1:
                counter += 1
                print("No Views found on object number " + str(counter))
            else:
                ce.waitForUIIdle()
                ce.setSelection(layer)
                if generateBoolean:
                    # generate models on selected shapes (assumes size of file is too big)
                    ce.generateModels(ce.selection())
                    ce.waitForUIIdle()
                if iterateThroughBookMarksBoolean:
                    bookMarkObjects = layerView[0].getBookmarks()
                    for bookmark in bookMarkObjects:
                        bookmarkName = str(bookmark)
                        layerView[0].restoreBookmark(str(bookmarkName), False)
                        outputPath = generateImagePath(ce.toFSPath("images"), outputFolder, layerName, bookmarkName,
                                                       fileType)
                        layerView[0].snapshot(outputPath, width, height)
                        counter += 1
                        print("Exported snapshot for layer named:" + str(layerName) +
                              " and bookmark named " + str(bookmark) + ".")
                else:
                    outputPath = generateImagePath(ce.toFSPath("images"), outputFolder, layerName, "", fileType)
                    layerView[0].snapshot(outputPath, width, height)
                    counter += 1
                    print("Exported snapshot for layer named:" + str(layerName))
            layer.setVisible(False)
            # After Snap Shots are retrieved delete the selection, memory management
            if deleteBoolean:
                ce.delete(ce.selection())
                pass
        except Exception as e:
            print("Could not execute on counter " + str(counter))
            print("Error:",e.args[0])
            counter += 1
            pass



# Call
if __name__ == '__main__':
    print("Batch Layer script started.")
    main()
    print("Script completed.")
