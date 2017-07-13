# --------------------------------
# Name: CEBatchFBXExport.py
# Purpose: Batch export of CE layers to game engine importable FBXs.
# Current Owner: David Wasserman
# Last Modified: 7/12/2017
# Copyright:   (c) Co-Adaptive
# CityEngine Vs: 2017
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
import os
# get a CityEngine instance
ce = CE()

outputFolder = "/BatchExportFBX"
generateBoolean = False
deleteBoolean = False
fileType="BINARY" #Or "TEXT"
CollectTextures=True
CreateShapeGroups=True
IncludeMaterials=True
ExportGeometry= "MODEL_GEOMETRY_FALLBACK"#["MODEL_GEOMETRY_FALLBACK", "MODEL_GEOMETRY", "SHAPE_GEOMETRY"]

def assure_dir(Base_Dir_Path, Base_Name=""):
    """Worker function will ensure that a directory exists. If it does not it, will create one. If an
    optional basename is passed it will create a folder with the base name joined if it does not exist."""
    if os.path.exists(Base_Dir_Path):
        if Base_Name:
            new_folder = os.path.join(Base_Dir_Path, Base_Name)
            if os.path.exists(new_folder):
                return new_folder
            else:
                os.makedirs(new_folder)
                return new_folder
        else:
            return Base_Dir_Path
    else:
        os.makedirs(Base_Dir_Path)
        return Base_Dir_Path

# Turn off User Interface updates, or script might take forever.
@noUIupdate
def main():
    # This function will export in batch web scenes to the input outputFolder
    layers = ce.getObjectsFrom(ce.scene, ce.isLayer)
    print("There are " + str(len(layers)) + " layers in the current scene.")
    counter = 0
    for layer in layers:
        try:
            ce.setSelection(layer)
            OID = ce.getOID(layer)
            layerName = ce.getName(layer)
            if layerName == "Panorama" or layerName == "Scene Light":
                continue  # skip
            if generateBoolean:
                # generate models on selected shapes (assumes size of file is too big)
                ce.generateModels(ce.selection())
                ce.waitForUIIdle()
            print ("Setting export settings for layer named: " + str(layerName))
            exportSettings = FBXExportModelSettings()
            assure_dir(ce.toFSPath("models"),str(outputFolder).strip(r"/"))
            exportSettings.setOutputPath(ce.toFSPath("models") + str(outputFolder))
            exportSettings.setBaseName(layerName)
            exportSettings.setFileType(fileType)
            exportSettings.setCollectTextures(CollectTextures)
            exportSettings.setCreateShapeGroups(CreateShapeGroups)
            exportSettings.setIncludeMaterials(IncludeMaterials)
            exportSettings.setExportGeometry(ExportGeometry)
            ce.export(ce.selection()[0], exportSettings)
            print ("Exported layer named: " + str(layerName) + "to models/BatchExportFBX")
            counter += 1
            if deleteBoolean:
                ce.delete(ce.selection())
                pass
            print("Exported FBX for layer named:" + str(layerName))
            # Change this to an absolute path that points to your KML files.
        except Exception as e:
            print("Could not execute on counter " + str(counter))
            print("Error:", e.args[0])
            counter += 1
            pass


# Call
if __name__ == '__main__':
    print("Batch Layer script started.")
    main()
    print("Script completed.")
