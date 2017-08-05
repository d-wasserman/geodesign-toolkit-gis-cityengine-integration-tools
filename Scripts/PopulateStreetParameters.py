# --------------------------------
# Name: PopulateStreetParameters.py
# Purpose: This tool is designed to populate with default fields and values for street shapes and is designed
# to add core complete street rule fields. 
# Current Owner: David Wasserman
# Last Modified: 3/15/2016
# Copyright:  (c) Co-Adaptive- David Wasserman
# ArcGIS Version:   10.3
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
import os, math, arcpy, random


# String Parameters
streetWidth = "streetWidth"
streetOffset = "streetOffset"
sidewalkWidthRight = "sidewalkWidthRight"
sidewalkWidthLeft = "sidewalkWidthLeft"
precision = "precision"
laneWidth = "laneWidth"
type = "type"
cornerStyle = "cornerStyle"
# String Attributes of Complete Street Rule
Lane_Distribution = "Lane_Distribution"
Lane_Width = "Lane_Width"
Speed_Limit_in_MPH = "Speed_Limit_in_MPH"
Stop_Begin = "Stop_Begin"
Stop_End = "Stop_End"

Crosswalk_Begin = "Crosswalk_Begin"
Crosswalk_End = "Crosswalk_End"
Begin_Crosswalk_To_Stop_Bar = "Begin_Crosswalk_To_Stop_Bar"
End_Crosswalk_To_Stop_Bar = "End_Crosswalk_To_Stop_Bar"
Crosswalk_Width = "Crosswalk_Width"

Right_Parking_Type = "Right_Parking_Type"
Right_Parking_Width = "Right_Parking_Width"
Left_Parking_Type = "Left_Parking_Type"
Left_Parking_Width = "Left_Parking_Width"

Center_Type = "Center_Type"
Center_Width = "Center_Width"
Planting_and_Walkway_Layout = "Planting_and_Walkway_Layout"
Boulevard_Inside_Width = "Boulevard_Inside_Width"
Boulevard_Configuration = "Boulevard_Configuration"
Median_Ground_Cover = "Median_Ground_Cover"
Median_Planting_Length = "Median_Planting_Length"

Median_Bus_Stop = "Median_Bus_Stop"
Median_Bus_Stop_Location = "Median_Bus_Stop_Location"

Transit_Lane = "Transit_Lane"
Transit_Lane_Sides = "Transit_Lane_Sides"
Transit_Lane_Width = "Transit_Lane_Width"
Transit_Lane_Position = "Transit_Lane_Position"

Right_Bike_Lane_Width = "Right_Bike_Lane_Width"
Left_Bike_Lane_Width = "Left_Bike_Lane_Width"
Right_Buffer_Width = "Right_Buffer_Width"
Left_Buffer_Width = "Left_Buffer_Width"
Buffer_Type = "Buffer_Type"
Buffer_Protection = "Buffer_Protection"
Parking_Protection = "Parking_Protection"
Left_Bike_Box = "Left_Bike_Box"
Right_Bike_Box = "Right_Bike_Box"
Bike_Box_Color_Override = "Bike_Box_Color_Override"

Sidewalk_Ground_Cover = "Sidewalk_Ground_Cover"
Sidewalk_Planting_Width = "Sidewalk_Planting_Width"
Sidewalk_Planting_Length = "Sidewalk_Planting_Length"
Sidewalk_Planting_Spacing = "Sidewalk_Planting_Spacing"

Sidewalk_Bus_Stop = "Sidewalk_Bus_Stop"
Sidewalk_Bus_Stop_Location = "Sidewalk_Bus_Stop_Location"
Sidewalk_Benches = "Sidewalk_Benches"
Parking_Meters = "Parking_Meters"
Sidewalk_Street_Lamps = "Sidewalk_Street_Lamps"
Traffic_Lights = "Traffic_Lights"

Bridge_Display = "Bridge_Display"


# Function Definitions
def funcReport(function=None,reportBool=False):
    """This decorator function is designed to be used as a wrapper with other functions to enable basic try and except
     reporting (if function fails it will report the name of the function that failed and its arguments. If a report
      boolean is true the function will report inputs and outputs of a function.-David Wasserman"""
    def funcReport_Decorator(function):
        def funcWrapper(*args, **kwargs):
            try:
                funcResult = function(*args, **kwargs)
                if reportBool:
                    print("Function:{0}".format(str(function.__name__)))
                    print("     Input(s):{0}".format(str(args)))
                    print("     Ouput(s):{0}".format(str(funcResult)))
                return funcResult
            except Exception as e:
                print("{0} - function failed -|- Function arguments were:{1}.".format(str(function.__name__), str(args)))
                print(e.args[0])
        return funcWrapper
    if not function:  # User passed in a bool argument
        def waiting_for_function(function):
            return funcReport_Decorator(function)
        return waiting_for_function
    else:
        return funcReport_Decorator(function)


def arcToolReport(function=None, arcToolMessageBool=False, arcProgressorBool=False):
    """This decorator function is designed to be used as a wrapper with other GIS functions to enable basic try and except
     reporting (if function fails it will report the name of the function that failed and its arguments. If a report
      boolean is true the function will report inputs and outputs of a function.-David Wasserman"""
    def arcToolReport_Decorator(function):
        def funcWrapper(*args, **kwargs):
            try:
                funcResult = function(*args, **kwargs)
                if arcToolMessageBool:
                    arcpy.AddMessage("Function:{0}".format(str(function.__name__)))
                    arcpy.AddMessage("     Input(s):{0}".format(str(args)))
                    arcpy.AddMessage("     Ouput(s):{0}".format(str(funcResult)))
                if arcProgressorBool:
                    arcpy.SetProgressorLabel("Function:{0}".format(str(function.__name__)))
                    arcpy.SetProgressorLabel("     Input(s):{0}".format(str(args)))
                    arcpy.SetProgressorLabel("     Ouput(s):{0}".format(str(funcResult)))
                return funcResult
            except Exception as e:
                arcpy.AddMessage(
                    "{0} - function failed -|- Function arguments were:{1}.".format(str(function.__name__), str(args)))
                print("{0} - function failed -|- Function arguments were:{1}.".format(str(function.__name__), str(args)))
                print(e.args[0])
        return funcWrapper
    if not function:  # User passed in a bool argument
        def waiting_for_function(function):
            return  arcToolReport_Decorator(function)
        return waiting_for_function
    else:
        return arcToolReport_Decorator(function)

@arcToolReport
def arcPrint(string, progressor_Bool=False):
    # This function is used to simplify using arcpy reporting for tool creation,if progressor bool is true it will
    # create a tool label.
    try:
        if progressor_Bool:
            arcpy.SetProgressorLabel(string)
            arcpy.AddMessage(string)
            print(string)
        else:
            arcpy.AddMessage(string)
            print(string)
    except arcpy.ExecuteError:
        arcpy.GetMessages(2)
        pass
    except:
        arcpy.AddMessage("Could not create message, bad arguments.")
        pass

@arcToolReport
def FieldExist(featureclass, fieldname):
    """ Check if a field in a feature class field exists and return true it does, false if not."""
    fieldList = arcpy.ListFields(featureclass, fieldname)
    fieldCount = len(fieldList)
    if (fieldCount >= 1) and fieldname.strip():  # If there is one or more of this field return true
        return True
    else:
        return False


# CR: add comment describing functionality and parameter purposes (apply to all instances)
@arcToolReport
def AddNewField(in_table, field_name, field_type, field_precision="#", field_scale="#", field_length="#",
                field_alias="#", field_is_nullable="#", field_is_required="#", field_domain="#"):
    # Add a new field if it currently does not exist...add field alone is slower than checking first.
    if FieldExist(in_table, field_name):
        print(field_name + " Exists")
        arcpy.AddMessage(field_name + " Exists")
    else:
        print("Adding " + field_name)
        arcpy.AddMessage("Adding " + field_name)
        arcpy.AddField_management(in_table, field_name, field_type, field_precision, field_scale,
                                  field_length,
                                  field_alias,
                                  field_is_nullable, field_is_required, field_domain)

@arcToolReport
def buffDist(bikelnWidth):
    if bikelnWidth > 1.6:
        return 1
    if bikelnWidth > 0:
        return random.randint(0, 1)
    else:
        return 0

@arcToolReport
def ifBelowThreshZero(number, threshold):
    if number < threshold:
        return 0
    else:
        return 1

@arcToolReport
def evenStreetWidth(lanesCount, lnWidth, additionalWidth=0):
    if lanesCount % 2 == 0:
        stWidth = (lnWidth * lanesCount) + additionalWidth
        return stWidth  # From bike lanes and other random features
    else:
        lanesCount += 1
        stWidth = ((lnWidth * lanesCount) + additionalWidth)
        return stWidth

@arcToolReport
def parkingWidth(string):
    if string == "Parallel":
        return 2.44
    else:
        return 0

# Main Function

# Function Definitions
def do_analysis(inFeatureClass, CompStAttr, DefaultStParam, RandomCompStr):
    # Populate a feature class with CityEngine street parameters and complete street rule attributes/values
    try:
        arcPrint("Defining workspace strings and street parameter street names.")
        # String and path definitions
        #############################
        # Street Parameters
        name = os.path.split(inFeatureClass)[1]
        workspace = os.path.split(inFeatureClass)[0]
        spstreetWidth = arcpy.ValidateFieldName(streetWidth, workspace)
        spsidewalkWidthLeft = arcpy.ValidateFieldName(sidewalkWidthLeft, workspace)
        spsidewalkWidthRight = arcpy.ValidateFieldName(sidewalkWidthRight, workspace)
        spstoffset = arcpy.ValidateFieldName(streetOffset, workspace)
        spprecision = arcpy.ValidateFieldName(precision, workspace)
        splaneWidth = arcpy.ValidateFieldName(laneWidth, workspace)
        sptype = arcpy.ValidateFieldName(type, workspace)
        spcornerStyle = arcpy.ValidateFieldName(cornerStyle, workspace)

        arcPrint("Adding Core Street Parameter Fields for: {0}".format(str(name)), True)
        AddNewField(inFeatureClass, spstreetWidth, "DOUBLE", field_alias=streetWidth)
        AddNewField(inFeatureClass, spsidewalkWidthLeft, "DOUBLE",
                    field_alias=sidewalkWidthLeft)
        AddNewField(inFeatureClass, spsidewalkWidthRight, "DOUBLE",
                    field_alias=sidewalkWidthRight)
        AddNewField(inFeatureClass, spstoffset, "DOUBLE", field_alias=streetOffset)
        AddNewField(inFeatureClass, spprecision, "DOUBLE", field_alias=precision)
        AddNewField(inFeatureClass, splaneWidth, "DOUBLE", field_alias=laneWidth)
        AddNewField(inFeatureClass, sptype, "TEXT", field_alias="Intersection type")
        AddNewField(inFeatureClass, spcornerStyle, "TEXT", field_alias=cornerStyle)

        if CompStAttr:
            arcPrint("Adding Core Complete Street Rule Attributes Fields for: {0}".format(str(name)), True)
            # Section 1
            AddNewField(inFeatureClass, arcpy.ValidateFieldName(Lane_Distribution, workspace), "DOUBLE",
                        field_alias=Lane_Distribution)
            AddNewField(inFeatureClass, arcpy.ValidateFieldName(Lane_Width, workspace), "DOUBLE",
                        field_alias=Lane_Width)
            AddNewField(inFeatureClass, arcpy.ValidateFieldName(Speed_Limit_in_MPH, workspace), "DOUBLE",
                        field_alias=Speed_Limit_in_MPH)
            AddNewField(inFeatureClass, arcpy.ValidateFieldName(Stop_Begin, workspace), "TEXT", field_alias=Stop_Begin)
            AddNewField(inFeatureClass, arcpy.ValidateFieldName(Stop_End, workspace), "TEXT", field_alias=Stop_End)
            # Section 2
            AddNewField(inFeatureClass, arcpy.ValidateFieldName(Crosswalk_Begin, workspace), "TEXT",
                        field_alias=Crosswalk_Begin)
            AddNewField(inFeatureClass, arcpy.ValidateFieldName(Crosswalk_End, workspace), "TEXT",
                        field_alias=Crosswalk_End)
            AddNewField(inFeatureClass, arcpy.ValidateFieldName(Begin_Crosswalk_To_Stop_Bar, workspace), "DOUBLE",
                        field_alias=Begin_Crosswalk_To_Stop_Bar)
            AddNewField(inFeatureClass, arcpy.ValidateFieldName(End_Crosswalk_To_Stop_Bar, workspace), "DOUBLE",
                        field_alias=End_Crosswalk_To_Stop_Bar)
            AddNewField(inFeatureClass, arcpy.ValidateFieldName(Crosswalk_Width, workspace), "DOUBLE",
                        field_alias=Crosswalk_Width)
            # Section 3
            AddNewField(inFeatureClass, arcpy.ValidateFieldName(Right_Parking_Type, workspace), "TEXT",
                        field_alias=Right_Parking_Type)
            AddNewField(inFeatureClass, arcpy.ValidateFieldName(Right_Parking_Width, workspace), "DOUBLE",
                        field_alias=Right_Parking_Width)
            AddNewField(inFeatureClass, arcpy.ValidateFieldName(Left_Parking_Type, workspace), "TEXT",
                        field_alias=Left_Parking_Type)
            AddNewField(inFeatureClass, arcpy.ValidateFieldName(Left_Parking_Width, workspace), "DOUBLE",
                        field_alias=Left_Parking_Width)
            # Section 4
            AddNewField(inFeatureClass, arcpy.ValidateFieldName(Center_Type, workspace), "TEXT",
                        field_alias=Center_Type)
            AddNewField(inFeatureClass, arcpy.ValidateFieldName(Center_Width, workspace), "DOUBLE",
                        field_alias=Center_Width)
            AddNewField(inFeatureClass, arcpy.ValidateFieldName(Planting_and_Walkway_Layout, workspace), "TEXT",
                        field_alias=Planting_and_Walkway_Layout)
            AddNewField(inFeatureClass, arcpy.ValidateFieldName(Boulevard_Inside_Width, workspace), "DOUBLE",
                        field_alias=Boulevard_Inside_Width)
            AddNewField(inFeatureClass, arcpy.ValidateFieldName(Boulevard_Configuration, workspace), "TEXT",
                        field_alias=Boulevard_Configuration)
            AddNewField(inFeatureClass, arcpy.ValidateFieldName(Median_Ground_Cover, workspace), "TEXT",
                        field_alias=Median_Ground_Cover)
            AddNewField(inFeatureClass, arcpy.ValidateFieldName(Median_Planting_Length, workspace), "DOUBLE",
                        field_alias=Median_Planting_Length)
            # Section 5
            AddNewField(inFeatureClass, arcpy.ValidateFieldName(Median_Bus_Stop, workspace), "TEXT",
                        field_alias=Median_Bus_Stop)
            AddNewField(inFeatureClass, arcpy.ValidateFieldName(Median_Bus_Stop_Location, workspace), "TEXT",
                        field_alias=Median_Bus_Stop_Location)
            # Section 6
            AddNewField(inFeatureClass, arcpy.ValidateFieldName(Transit_Lane, workspace), "TEXT",
                        field_alias=Transit_Lane)
            AddNewField(inFeatureClass, arcpy.ValidateFieldName(Transit_Lane_Sides, workspace), "TEXT",
                        field_alias=Transit_Lane_Sides)
            AddNewField(inFeatureClass, arcpy.ValidateFieldName(Transit_Lane_Width, workspace), "DOUBLE",
                        field_alias=Transit_Lane_Width)
            AddNewField(inFeatureClass, arcpy.ValidateFieldName(Transit_Lane_Position, workspace), "TEXT",
                        field_alias=Transit_Lane_Position)
            # Section 7
            AddNewField(inFeatureClass, arcpy.ValidateFieldName(Right_Bike_Lane_Width, workspace), "DOUBLE",
                        field_alias=Right_Bike_Lane_Width)
            AddNewField(inFeatureClass, arcpy.ValidateFieldName(Left_Bike_Lane_Width, workspace), "DOUBLE",
                        field_alias=Left_Bike_Lane_Width)
            AddNewField(inFeatureClass, arcpy.ValidateFieldName(Right_Buffer_Width, workspace), "DOUBLE",
                        field_alias=Right_Buffer_Width)
            AddNewField(inFeatureClass, arcpy.ValidateFieldName(Left_Buffer_Width, workspace), "DOUBLE",
                        field_alias=Left_Buffer_Width)
            AddNewField(inFeatureClass, arcpy.ValidateFieldName(Buffer_Type, workspace), "TEXT",
                        field_alias=Buffer_Type)
            AddNewField(inFeatureClass, arcpy.ValidateFieldName(Buffer_Protection, workspace), "TEXT",
                        field_alias=Buffer_Protection)
            AddNewField(inFeatureClass, arcpy.ValidateFieldName(Parking_Protection, workspace), "TEXT",
                        field_alias=Parking_Protection)
            AddNewField(inFeatureClass, arcpy.ValidateFieldName(Left_Bike_Box, workspace), "TEXT",
                        field_alias=Left_Bike_Box)
            AddNewField(inFeatureClass, arcpy.ValidateFieldName(Right_Bike_Box, workspace), "TEXT",
                        field_alias=Right_Bike_Box)
            AddNewField(inFeatureClass, arcpy.ValidateFieldName(Bike_Box_Color_Override, workspace), "TEXT",
                        field_alias=Bike_Box_Color_Override)
            # Section 8
            AddNewField(inFeatureClass, arcpy.ValidateFieldName(Sidewalk_Ground_Cover, workspace), "TEXT",
                        field_alias=Sidewalk_Ground_Cover)
            AddNewField(inFeatureClass, arcpy.ValidateFieldName(Sidewalk_Planting_Width, workspace), "DOUBLE",
                        field_alias=Sidewalk_Planting_Width)
            AddNewField(inFeatureClass, arcpy.ValidateFieldName(Sidewalk_Planting_Length, workspace), "DOUBLE",
                        field_alias=Sidewalk_Planting_Length)
            AddNewField(inFeatureClass, arcpy.ValidateFieldName(Sidewalk_Planting_Spacing, workspace), "DOUBLE",
                        field_alias=Sidewalk_Planting_Spacing)
            # Section 9
            AddNewField(inFeatureClass, arcpy.ValidateFieldName(Sidewalk_Bus_Stop, workspace), "TEXT",
                        field_alias=Sidewalk_Bus_Stop)
            AddNewField(inFeatureClass, arcpy.ValidateFieldName(Sidewalk_Bus_Stop_Location, workspace), "TEXT",
                        field_alias=Sidewalk_Bus_Stop_Location)
            AddNewField(inFeatureClass, arcpy.ValidateFieldName(Sidewalk_Benches, workspace), "TEXT",
                        field_alias=Sidewalk_Benches)
            AddNewField(inFeatureClass, arcpy.ValidateFieldName(Parking_Meters, workspace), "TEXT",
                        field_alias=Parking_Meters)
            AddNewField(inFeatureClass, arcpy.ValidateFieldName(Sidewalk_Street_Lamps, workspace), "TEXT",
                        field_alias=Sidewalk_Street_Lamps)
            AddNewField(inFeatureClass, arcpy.ValidateFieldName(Traffic_Lights, workspace), "TEXT",
                        field_alias=Traffic_Lights)
            # Section 10
            AddNewField(inFeatureClass, arcpy.ValidateFieldName(Bridge_Display, workspace), "TEXT",
                        field_alias=Bridge_Display)
        if DefaultStParam:
            arcPrint("Calculating default street parameter values.", True)
            cursor = arcpy.da.UpdateCursor(inFeatureClass,
                                           [spstreetWidth, spstoffset, spsidewalkWidthRight, spsidewalkWidthLeft,
                                            spprecision, splaneWidth, sptype, spcornerStyle,
                                            arcpy.ValidateFieldName(Stop_Begin, workspace),
                                            arcpy.ValidateFieldName(Stop_End, workspace),
                                            arcpy.ValidateFieldName(Lane_Width, workspace),
                                            arcpy.ValidateFieldName(Begin_Crosswalk_To_Stop_Bar, workspace),
                                            arcpy.ValidateFieldName(End_Crosswalk_To_Stop_Bar, workspace),
                                            arcpy.ValidateFieldName(Transit_Lane, workspace),
                                            arcpy.ValidateFieldName(Transit_Lane_Width, workspace),
                                            arcpy.ValidateFieldName(Right_Bike_Lane_Width, workspace),
                                            arcpy.ValidateFieldName(Left_Bike_Lane_Width, workspace),
                                            arcpy.ValidateFieldName(Right_Buffer_Width, workspace),
                                            arcpy.ValidateFieldName(Left_Buffer_Width, workspace),
                                            arcpy.ValidateFieldName(Buffer_Type, workspace),
                                            arcpy.ValidateFieldName(Right_Parking_Type, workspace),
                                            arcpy.ValidateFieldName(Left_Parking_Type, workspace),
                                            arcpy.ValidateFieldName(Sidewalk_Ground_Cover, workspace),
                                            arcpy.ValidateFieldName(Bridge_Display, workspace),
                                            arcpy.ValidateFieldName(Crosswalk_End, workspace),
                                            arcpy.ValidateFieldName(Crosswalk_Begin, workspace)])
            counter = 1
            for spRow in cursor:
                try:
                    arcPrint("Calculating row number {0}".format(str(counter)))
                    sidewalkWidth = random.randint(3, 5)
                    lanesWidth = 3.5
                    strWidth = evenStreetWidth(random.randint(8, 35), (lanesWidth - .2))
                    spRow[0] = strWidth
                    spRow[1] = 0
                    spRow[2] = sidewalkWidth
                    spRow[3] = sidewalkWidth
                    spRow[4] = .5
                    spRow[5] = lanesWidth
                    spRow[6] = "Crossing"
                    spRow[7] = "Arcs"
                    arcPrint("Defined street parameters for row number {0}".format(str(counter)))
                    if RandomCompStr and CompStAttr:
                        stopChoice = random.choice(
                                ["line only", "with stop marking", "arrows on all lanes", "arrows on side lanes",
                                 "arrows for right turn"])
                        crswlkChoice = random.choice(
                                ["none", "continental", "ladder", "transverse", "custom", "ladder custom"])
                        compLaneWidth = random.choice([3.3528, 3.6576])
                        TranLaneWidth = 3.3528
                        bikeChoice = random.choice([0, 0, 0, 1.4, 1.4, 1.8, 2])
                        buffChoice = buffDist(bikeChoice)
                        prkChoice = random.choice(["None", "None", "Parallel"])
                        parkWidth = parkingWidth(prkChoice)
                        stopGap = random.randint(1, 2) + .4
                        buffType = random.choice(["Painted Stripes", "Painted Stripes", "Curb Buffer with Plantings",
                                                  "Cycle Track With Planters", "Cycle Track With Tubular Markers"])
                        centerWidth = 0.1016 * 4
                        spareSpace = 0.3
                        compStrWidth = evenStreetWidth(random.randint(1, 8), (compLaneWidth),
                                                       ((parkWidth * 2) + (bikeChoice * 2) + (
                                                           buffChoice * 2) + centerWidth + spareSpace))
                        spRow[0] = compStrWidth
                        spRow[8] = stopChoice
                        spRow[9] = stopChoice
                        spRow[10] = compLaneWidth
                        spRow[11] = stopGap
                        spRow[12] = stopGap
                        spRow[13] = random.choice(["None", "None", "None", "None", "Bus Lane"])
                        spRow[14] = TranLaneWidth
                        spRow[15] = bikeChoice
                        spRow[16] = bikeChoice
                        spRow[17] = buffChoice
                        spRow[18] = buffChoice
                        spRow[19] = buffType
                        spRow[20] = prkChoice
                        spRow[21] = prkChoice
                        spRow[22] = random.choice(["None", "Standard Grass"])
                        spRow[23] = "Concrete Extrusion Only"
                        spRow[24] = crswlkChoice
                        spRow[25] = crswlkChoice
                        arcPrint("Defined Complete Street Attributes for row number {0}".format(str(counter)))
                    counter += 1
                    cursor.updateRow(spRow)
                except:
                    arcPrint("Skipped row on iteration {0}".format(str(counter)))
                    counter += 1
                    pass
            del cursor

    except arcpy.ExecuteError:
        print(arcpy.GetMessages(2))
    except Exception as e:
        print(e.args[0])


# End do_analysis function
# Main Script
if __name__ == "__main__":
    # Define Inputs
    inFeatureClass = arcpy.GetParameterAsText(0)
    AddCompleteStreetRuleAttributes = arcpy.GetParameter(1)
    CreateDefaultStreetParameters = arcpy.GetParameter(2)
    CreateRandomCompStAttr = arcpy.GetParameter(3)
    do_analysis(inFeatureClass, AddCompleteStreetRuleAttributes, CreateDefaultStreetParameters, CreateRandomCompStAttr)

