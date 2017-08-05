# --------------------------------
# Name: PopulateStreetParameters.py
# Purpose: This tool is designed to populate with default fields and values for street shapes and is designed
# to add core complete street rule fields.
# Current Owner: David Wasserman
# Last Modified: 8/5/17
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
def func_report(function=None, report_bool=False):
    """This decorator function is designed to be used as a wrapper with other functions to enable basic try and except
     reporting (if function fails it will report the name of the function that failed and its arguments. If a report
      boolean is true the function will report inputs and outputs of a function.-David Wasserman"""

    def func_report_decorator(function):
        def func_wrapper(*args, **kwargs):
            try:
                func_result = function(*args, **kwargs)
                if report_bool:
                    print("Function:{0}".format(str(function.__name__)))
                    print("     Input(s):{0}".format(str(args)))
                    print("     Ouput(s):{0}".format(str(func_result)))
                return func_result
            except Exception as e:
                print(
                    "{0} - function failed -|- Function arguments were:{1}.".format(str(function.__name__), str(args)))
                print(e.args[0])

        return func_wrapper

    if not function:  # User passed in a bool argument
        def waiting_for_function(function):
            return func_report_decorator(function)

        return waiting_for_function
    else:
        return func_report_decorator(function)


def arc_tool_report(function=None, arc_tool_message_bool=False, arc_progressor_bool=False):
    """This decorator function is designed to be used as a wrapper with other GIS functions to enable basic try and except
     reporting (if function fails it will report the name of the function that failed and its arguments. If a report
      boolean is true the function will report inputs and outputs of a function.-David Wasserman"""

    def arc_tool_report_decorator(function):
        def func_wrapper(*args, **kwargs):
            try:
                func_result = function(*args, **kwargs)
                if arc_tool_message_bool:
                    arcpy.AddMessage("Function:{0}".format(str(function.__name__)))
                    arcpy.AddMessage("     Input(s):{0}".format(str(args)))
                    arcpy.AddMessage("     Ouput(s):{0}".format(str(func_result)))
                if arc_progressor_bool:
                    arcpy.SetProgressorLabel("Function:{0}".format(str(function.__name__)))
                    arcpy.SetProgressorLabel("     Input(s):{0}".format(str(args)))
                    arcpy.SetProgressorLabel("     Ouput(s):{0}".format(str(func_result)))
                return func_result
            except Exception as e:
                arcpy.AddMessage(
                    "{0} - function failed -|- Function arguments were:{1}.".format(str(function.__name__),
                                                                                    str(args)))
                print(
                    "{0} - function failed -|- Function arguments were:{1}.".format(str(function.__name__), str(args)))
                print(e.args[0])

        return func_wrapper

    if not function:  # User passed in a bool argument
        def waiting_for_function(function):
            return arc_tool_report_decorator(function)

        return waiting_for_function
    else:
        return arc_tool_report_decorator(function)


@arc_tool_report
def arc_print(string, progressor_Bool=False):
    """ This function is used to simplify using arcpy reporting for tool creation,if progressor bool is true it will
    create a tool label."""
    casted_string = str(string)
    if progressor_Bool:
        arcpy.SetProgressorLabel(casted_string)
        arcpy.AddMessage(casted_string)
        print(casted_string)
    else:
        arcpy.AddMessage(casted_string)
        print(casted_string)

@arc_tool_report
def field_exist(featureclass, fieldname):
    """ Check if a field in a feature class field exists and return true it does, false if not."""
    fieldList = arcpy.ListFields(featureclass, fieldname)
    fieldCount = len(fieldList)
    if (fieldCount >= 1) and fieldname.strip():  # If there is one or more of this field return true
        return True
    else:
        return False


# CR: add comment describing functionality and parameter purposes (apply to all instances)
@arc_tool_report
def add_new_field(in_table, field_name, field_type, field_precision="#", field_scale="#", field_length="#",
                  field_alias="#", field_is_nullable="#", field_is_required="#", field_domain="#"):
    # Add a new field if it currently does not exist...add field alone is slower than checking first.
    if field_exist(in_table, field_name):
        print(field_name + " Exists")
        arcpy.AddMessage(field_name + " Exists")
    else:
        print("Adding " + field_name)
        arcpy.AddMessage("Adding " + field_name)
        arcpy.AddField_management(in_table, field_name, field_type, field_precision, field_scale,
                                  field_length,
                                  field_alias,
                                  field_is_nullable, field_is_required, field_domain)

@arc_tool_report
def buff_dist(bikelnWidth):
    if bikelnWidth > 1.6:
        return 1.2
    if bikelnWidth > 0:
        return random.randint(0, 1)
    else:
        return 0

@arc_tool_report
def if_below_thresh_zero(number, threshold):
    if number < threshold:
        return 0
    else:
        return 1

@arc_tool_report
def even_street_widths(lanesCount, lnWidth, additionalWidth=0):
    if lanesCount % 2 == 0:
        stWidth = (lnWidth * lanesCount) + additionalWidth
        return stWidth  # From bike lanes and other random features
    else:
        lanesCount += 1
        stWidth = ((lnWidth * lanesCount) + additionalWidth)
        return stWidth

@arc_tool_report
def parking_width(string):
    if string == "Parallel":
        return 2.44
    else:
        return 0

# Main Function

# Function Definitions
def populate_street_parameters(in_features, group_id,filter_query,comp_st_attr, default_st_param, rand_comp_str):
    # Populate a feature class with CityEngine street parameters and complete street rule attributes/values
    try:
        arc_print("Defining workspace strings and street parameter street names.")
        # String and path definitions
        #############################
        # Street Parameters
        name = os.path.split(in_features)[1]
        workspace = os.path.split(in_features)[0]
        spstreetWidth = arcpy.ValidateFieldName(streetWidth, workspace)
        spsidewalkWidthLeft = arcpy.ValidateFieldName(sidewalkWidthLeft, workspace)
        spsidewalkWidthRight = arcpy.ValidateFieldName(sidewalkWidthRight, workspace)
        spstoffset = arcpy.ValidateFieldName(streetOffset, workspace)
        spprecision = arcpy.ValidateFieldName(precision, workspace)
        splaneWidth = arcpy.ValidateFieldName(laneWidth, workspace)
        sptype = arcpy.ValidateFieldName(type, workspace)
        spcornerStyle = arcpy.ValidateFieldName(cornerStyle, workspace)

        arc_print("Adding Core Street Parameter Fields for: {0}".format(str(name)), True)
        add_new_field(in_features, spstreetWidth, "DOUBLE", field_alias=streetWidth)
        add_new_field(in_features, spsidewalkWidthLeft, "DOUBLE",
                      field_alias=sidewalkWidthLeft)
        add_new_field(in_features, spsidewalkWidthRight, "DOUBLE",
                      field_alias=sidewalkWidthRight)
        add_new_field(in_features, spstoffset, "DOUBLE", field_alias=streetOffset)
        add_new_field(in_features, spprecision, "DOUBLE", field_alias=precision)
        add_new_field(in_features, splaneWidth, "DOUBLE", field_alias=laneWidth)
        add_new_field(in_features, sptype, "TEXT", field_alias="Intersection type")
        add_new_field(in_features, spcornerStyle, "TEXT", field_alias=cornerStyle)

        if comp_st_attr:
            arc_print("Adding Core Complete Street Rule Attributes Fields for: {0}".format(str(name)), True)
            # Section 1
            add_new_field(in_features, arcpy.ValidateFieldName(Lane_Distribution, workspace), "DOUBLE",
                          field_alias=Lane_Distribution)
            add_new_field(in_features, arcpy.ValidateFieldName(Lane_Width, workspace), "DOUBLE",
                          field_alias=Lane_Width)
            add_new_field(in_features, arcpy.ValidateFieldName(Speed_Limit_in_MPH, workspace), "DOUBLE",
                          field_alias=Speed_Limit_in_MPH)
            add_new_field(in_features, arcpy.ValidateFieldName(Stop_Begin, workspace), "TEXT", field_alias=Stop_Begin)
            add_new_field(in_features, arcpy.ValidateFieldName(Stop_End, workspace), "TEXT", field_alias=Stop_End)
            # Section 2
            add_new_field(in_features, arcpy.ValidateFieldName(Crosswalk_Begin, workspace), "TEXT",
                          field_alias=Crosswalk_Begin)
            add_new_field(in_features, arcpy.ValidateFieldName(Crosswalk_End, workspace), "TEXT",
                          field_alias=Crosswalk_End)
            add_new_field(in_features, arcpy.ValidateFieldName(Begin_Crosswalk_To_Stop_Bar, workspace), "DOUBLE",
                          field_alias=Begin_Crosswalk_To_Stop_Bar)
            add_new_field(in_features, arcpy.ValidateFieldName(End_Crosswalk_To_Stop_Bar, workspace), "DOUBLE",
                          field_alias=End_Crosswalk_To_Stop_Bar)
            add_new_field(in_features, arcpy.ValidateFieldName(Crosswalk_Width, workspace), "DOUBLE",
                          field_alias=Crosswalk_Width)
            # Section 3
            add_new_field(in_features, arcpy.ValidateFieldName(Right_Parking_Type, workspace), "TEXT",
                          field_alias=Right_Parking_Type)
            add_new_field(in_features, arcpy.ValidateFieldName(Right_Parking_Width, workspace), "DOUBLE",
                          field_alias=Right_Parking_Width)
            add_new_field(in_features, arcpy.ValidateFieldName(Left_Parking_Type, workspace), "TEXT",
                          field_alias=Left_Parking_Type)
            add_new_field(in_features, arcpy.ValidateFieldName(Left_Parking_Width, workspace), "DOUBLE",
                          field_alias=Left_Parking_Width)
            # Section 4
            add_new_field(in_features, arcpy.ValidateFieldName(Center_Type, workspace), "TEXT",
                          field_alias=Center_Type)
            add_new_field(in_features, arcpy.ValidateFieldName(Center_Width, workspace), "DOUBLE",
                          field_alias=Center_Width)
            add_new_field(in_features, arcpy.ValidateFieldName(Planting_and_Walkway_Layout, workspace), "TEXT",
                          field_alias=Planting_and_Walkway_Layout)
            add_new_field(in_features, arcpy.ValidateFieldName(Boulevard_Inside_Width, workspace), "DOUBLE",
                          field_alias=Boulevard_Inside_Width)
            add_new_field(in_features, arcpy.ValidateFieldName(Boulevard_Configuration, workspace), "TEXT",
                          field_alias=Boulevard_Configuration)
            add_new_field(in_features, arcpy.ValidateFieldName(Median_Ground_Cover, workspace), "TEXT",
                          field_alias=Median_Ground_Cover)
            add_new_field(in_features, arcpy.ValidateFieldName(Median_Planting_Length, workspace), "DOUBLE",
                          field_alias=Median_Planting_Length)
            # Section 5
            add_new_field(in_features, arcpy.ValidateFieldName(Median_Bus_Stop, workspace), "TEXT",
                          field_alias=Median_Bus_Stop)
            add_new_field(in_features, arcpy.ValidateFieldName(Median_Bus_Stop_Location, workspace), "TEXT",
                          field_alias=Median_Bus_Stop_Location)
            # Section 6
            add_new_field(in_features, arcpy.ValidateFieldName(Transit_Lane, workspace), "TEXT",
                          field_alias=Transit_Lane)
            add_new_field(in_features, arcpy.ValidateFieldName(Transit_Lane_Sides, workspace), "TEXT",
                          field_alias=Transit_Lane_Sides)
            add_new_field(in_features, arcpy.ValidateFieldName(Transit_Lane_Width, workspace), "DOUBLE",
                          field_alias=Transit_Lane_Width)
            add_new_field(in_features, arcpy.ValidateFieldName(Transit_Lane_Position, workspace), "TEXT",
                          field_alias=Transit_Lane_Position)
            # Section 7
            add_new_field(in_features, arcpy.ValidateFieldName(Right_Bike_Lane_Width, workspace), "DOUBLE",
                          field_alias=Right_Bike_Lane_Width)
            add_new_field(in_features, arcpy.ValidateFieldName(Left_Bike_Lane_Width, workspace), "DOUBLE",
                          field_alias=Left_Bike_Lane_Width)
            add_new_field(in_features, arcpy.ValidateFieldName(Right_Buffer_Width, workspace), "DOUBLE",
                          field_alias=Right_Buffer_Width)
            add_new_field(in_features, arcpy.ValidateFieldName(Left_Buffer_Width, workspace), "DOUBLE",
                          field_alias=Left_Buffer_Width)
            add_new_field(in_features, arcpy.ValidateFieldName(Buffer_Type, workspace), "TEXT",
                          field_alias=Buffer_Type)
            add_new_field(in_features, arcpy.ValidateFieldName(Buffer_Protection, workspace), "TEXT",
                          field_alias=Buffer_Protection)
            add_new_field(in_features, arcpy.ValidateFieldName(Parking_Protection, workspace), "TEXT",
                          field_alias=Parking_Protection)
            add_new_field(in_features, arcpy.ValidateFieldName(Left_Bike_Box, workspace), "TEXT",
                          field_alias=Left_Bike_Box)
            add_new_field(in_features, arcpy.ValidateFieldName(Right_Bike_Box, workspace), "TEXT",
                          field_alias=Right_Bike_Box)
            add_new_field(in_features, arcpy.ValidateFieldName(Bike_Box_Color_Override, workspace), "TEXT",
                          field_alias=Bike_Box_Color_Override)
            # Section 8
            add_new_field(in_features, arcpy.ValidateFieldName(Sidewalk_Ground_Cover, workspace), "TEXT",
                          field_alias=Sidewalk_Ground_Cover)
            add_new_field(in_features, arcpy.ValidateFieldName(Sidewalk_Planting_Width, workspace), "DOUBLE",
                          field_alias=Sidewalk_Planting_Width)
            add_new_field(in_features, arcpy.ValidateFieldName(Sidewalk_Planting_Length, workspace), "DOUBLE",
                          field_alias=Sidewalk_Planting_Length)
            add_new_field(in_features, arcpy.ValidateFieldName(Sidewalk_Planting_Spacing, workspace), "DOUBLE",
                          field_alias=Sidewalk_Planting_Spacing)
            # Section 9
            add_new_field(in_features, arcpy.ValidateFieldName(Sidewalk_Bus_Stop, workspace), "TEXT",
                          field_alias=Sidewalk_Bus_Stop)
            add_new_field(in_features, arcpy.ValidateFieldName(Sidewalk_Bus_Stop_Location, workspace), "TEXT",
                          field_alias=Sidewalk_Bus_Stop_Location)
            add_new_field(in_features, arcpy.ValidateFieldName(Sidewalk_Benches, workspace), "TEXT",
                          field_alias=Sidewalk_Benches)
            add_new_field(in_features, arcpy.ValidateFieldName(Parking_Meters, workspace), "TEXT",
                          field_alias=Parking_Meters)
            add_new_field(in_features, arcpy.ValidateFieldName(Sidewalk_Street_Lamps, workspace), "TEXT",
                          field_alias=Sidewalk_Street_Lamps)
            add_new_field(in_features, arcpy.ValidateFieldName(Traffic_Lights, workspace), "TEXT",
                          field_alias=Traffic_Lights)
            # Section 10
            add_new_field(in_features, arcpy.ValidateFieldName(Bridge_Display, workspace), "TEXT",
                          field_alias=Bridge_Display)
        if default_st_param:
            arc_print("Calculating default street parameter values.", True)
            cursor = arcpy.da.UpdateCursor(in_features,
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
                    arc_print("Calculating row number {0}".format(str(counter)))
                    sidewalkWidth = random.choice([0,1.4,1.4,1.5,1.6,2,2.5,2.6,2.8,3,4,5])
                    lanesWidth = 3.5
                    strWidth = even_street_widths(random.randint(8, 35), (lanesWidth - .2))
                    spRow[0] = strWidth
                    spRow[1] = 0
                    spRow[2] = sidewalkWidth
                    spRow[3] = sidewalkWidth
                    spRow[4] = .5
                    spRow[5] = lanesWidth
                    spRow[6] = "Crossing"
                    spRow[7] = "Arcs"
                    arc_print("Defined street parameters for row number {0}".format(str(counter)))
                    if rand_comp_str and comp_st_attr:
                        stopChoice = random.choice(
                                ["line only", "with stop marking", "arrows on all lanes", "arrows on side lanes",
                                 "arrows for right turn"])
                        crswlkChoice = random.choice(
                                ["none", "continental", "ladder", "transverse", "custom", "ladder custom"])
                        compLaneWidth = random.choice([3.3528, 3.6576])
                        TranLaneWidth = 3.3528
                        bikeChoice = random.choice([0, 0, 0, 1.4, 1.4, 1.8, 2])
                        buffChoice = buff_dist(bikeChoice)
                        prkChoice = random.choice(["None", "None", "Parallel"])
                        parkWidth = parking_width(prkChoice)
                        stopGap = random.randint(1, 2) + .4
                        buffType = random.choice(["Painted Stripes", "Painted Stripes", "Curb Buffer with Plantings",
                                                  "Cycle Track With Planters", "Cycle Track With Tubular Markers"])
                        centerWidth = 0.1016 * 4
                        spareSpace = 0.3
                        compStrWidth = even_street_widths(random.randint(1, 8), (compLaneWidth),
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
                        arc_print("Defined Complete Street Attributes for row number {0}".format(str(counter)))
                    counter += 1
                    cursor.updateRow(spRow)
                except:
                    arc_print("Skipped row on iteration {0}".format(str(counter)))
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
    in_feature_class = arcpy.GetParameterAsText(0)
    add_cs_rule_attributes = arcpy.GetParameter(1)
    create_default_parameters = arcpy.GetParameter(2)
    create_random_attr = arcpy.GetParameter(3)
    populate_street_parameters(in_feature_class, add_cs_rule_attributes, create_default_parameters, create_random_attr)

