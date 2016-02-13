# --------------------------------
# Name: CESelectLayerByAttribute.py
# Purpose: Select an object by an attribute in CityEngine.
# Current Owner: David Wasserman
# Last Modified: 12/22/2015
# Copyright:   (c) Co-Adaptive
# CityEngine Vs: 2015.2
# Python Version:   2.7
# License
# Copyright 2016 David J. Wasserman
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
fieldName = "Crosswalk_End"
fieldValue = "ladder"


# Main Function

def selectObjByAttribute(attr, value):
    layers = ce.getObjectsFrom(ce.scene, ce.isLayer)
    print(
        "There are " + str(len(layers) - 2) + " layers in the current scene.")  # -2 To remove Panorama and Scene Light
    counter = 0
    print("Iterating through all layers")

    print("Collecting objects from scene.")
    selectedLayers = []  # Selection is an empty list to hold all our slection
    for layer in layers:  # for loop iterates through all objects in scene
        print("Checking objects in layer ", layer)
        objectList = ce.getObjectsFrom(layer)
        for object in objectList:
            attrvalue = ce.getAttribute(object, attr)  # attrvalue gets assigned to it a retrieved attribute
            print("The current layer is:", layer)
            if attrvalue == value:  # if the attribute equals our value
                selectedLayers.append(layer)  # append the attribute value pair to the list selection
                print("Matched Attribute at value", value, " layer Added to selection.")
                break

    ce.setSelection(selectedLayers)  # set the selection equal to the list we just made
    ce.waitForUIIdle()


if __name__ == '__main__':
    selectObjByAttribute(fieldName, fieldValue)

    pass
