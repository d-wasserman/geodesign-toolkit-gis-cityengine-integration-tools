# --------------------------------
# Name: CEBatchWebSceneExport.py
# Purpose: Batch export of CE layers to web scenes.
# Current Owner: David Wasserman
# Last Modified: 12/22/2015
# Copyright:   (c) Co-Adaptive
# CityEngine Vs: 2015.2
# Python Version:   2.7
# License
# Copyright 2015 David J. Wasserman
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

outputFolder = "/BatchExport"
generateBoolean = False
deleteBoolean = False


# Turn off User Interface updates, or script might take forever.
@noUIupdate
def main(outputFolder):
    # This function will export in batch web scenes to the input outputFolder
    layers = ce.getObjectsFrom(ce.scene, ce.isLayer)
    print("There are " + str(len(layers)) + " layers in the current scene.")
    counter = 0
    for layer in layers:
        try:
            ce.setSelection(layer)
            OID = ce.getOID(layer)
            layerName = ce.getName(layer)
            if generateBoolean:
                # generate models on selected shapes (assumes size of file is too big)
                ce.generateModels(ce.selection())
                ce.waitForUIIdle()
            print ("Setting export settings for layer named: " + str(layerName))
            exportSettings = CEWebSceneExportModelSettings()
            exportSettings.setOutputPath(ce.toFSPath("models") + str(outputFolder))
            exportSettings.setBaseName(layerName)
            ce.export(ce.selection()[0], exportSettings)
            print ("Exported layer named: " + str(layerName) + "to models/BatchExport3WS")
            counter += 1
            if deleteBoolean:
                ce.delete(ce.selection())
                pass
            print("Exported web scene for layer named:" + str(layerName))
            # Change this to an absolute path that points to your KML files.
        except:
            print("Could not execute on counter " + str(counter))
            counter += 1
            pass


# Call
if __name__ == '__main__':
    print("Batch Layer script started.")
    main()
    print("Script completed.")
