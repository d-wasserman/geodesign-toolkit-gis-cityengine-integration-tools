# --------------------------------
# Name: PrepareStreetAssociations.py
# Purpose: This scripting tool is designed to prepare a feature class's records for CityEngine by associating it with
# an optional target geometry or a default geometry based around the centroid of the input feature class.
# Current Owner: David Wasserman
# Last Modified: 3/5/2016
# Copyright:   (c) Co-Adaptive- David Wasserman
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
import os, sys, arcpy, math

# Define Inputs
inFeatureClass = arcpy.GetParameterAsText(0)
outFeatureClass = arcpy.GetParameterAsText(1)
StreetLength_LotArea = arcpy.GetParameter(2)  # Units of current feature class
SizeField = arcpy.GetParameterAsText(3)  # Field is used to get size of output sanitized geometries.
referenceFeatureClassCentroid=arcpy.GetParameterAsText(4) #optional reference FC to get centroid from

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
    except:
        arcpy.AddMessage("Could not create message, bad arguments.")

@arcToolReport
def FieldExist(featureclass, fieldname):
    # Check if a field in a feature class field exists and return true it does, false if not.
    fieldList = arcpy.ListFields(featureclass, fieldname)
    fieldCount = len(fieldList)
    if (fieldCount >= 1):  # If there is one or more of this field return true
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
def CreateMainStreetCEGeometry(pointObj, translationDistance, nodalShift=0):
    # Create a polyline object consisting of a simple line based on the location of a passed point
    firstPt = pointObj.getPart(0)
    firstPt.X += nodalShift
    secondPt = pointObj.getPart(0)
    secondPt.Y += translationDistance
    secondPt.X += nodalShift
    array = arcpy.Array()
    array.add(firstPt)
    array.add(secondPt)
    MainStreet = arcpy.Polyline(array)
    return MainStreet  # CR: return arcpy.Polyline(arcpy.Array(pointObj))


# TODO: Integrate block generation into tool. Not a priority.
@arcToolReport
def CreateMainStreetBlockCEGeometry(pointObj, translationDistance, sideBlockWidth=50):
    # Create a dictionary of polyline objects consisting of a simple line based on the location of a passed point
    # This function in the future will be used to create a center street with two side blocks for the purpose
    # of lot creation in CityEngine.
    firstPt = pointObj.getPart(0)
    secondPt = pointObj.getPart(0)
    secondPt.Y += translationDistance
    leftTopCornerPt = pointObj.getPart(0)
    leftTopCornerPt.Y += translationDistance
    leftTopCornerPt.X += -sideBlockWidth
    rightTopCornerPt = pointObj.getPart(0)
    rightTopCornerPt.Y += translationDistance
    rightTopCornerPt.X += sideBlockWidth
    leftBottomCornerPt = pointObj.getPart(0)
    leftBottomCornerPt.X += -sideBlockWidth
    rightBottomCornerPt = pointObj.getPart(0)
    rightBottomCornerPt.X += sideBlockWidth
    mainArray = arcpy.Array()
    mainArray.add(firstPt)
    mainArray.add(secondPt)
    MainStreet = arcpy.Polyline(mainArray)
    leftMainArray = arcpy.Array()
    leftMainArray.add(leftBottomCornerPt)
    leftMainArray.add(leftTopCornerPt)
    leftMainStreet = arcpy.Polyline(leftMainArray)
    rightMainArray = arcpy.Array()
    rightMainArray.add(rightBottomCornerPt)
    rightMainArray.add(rightTopCornerPt)
    rightMainStreet = arcpy.Polyline(rightMainArray)
    botLeftSideArray = arcpy.Array()
    botLeftSideArray.add(firstPt)
    botLeftSideArray.add(leftBottomCornerPt)
    botLeftSideStreet = arcpy.Polyline(botLeftSideArray)
    botRightSideArray = arcpy.Array()
    botRightSideArray.add(firstPt)
    botRightSideArray.add(rightBottomCornerPt)
    botRightSideStreet = arcpy.Polyline(botRightSideArray)
    topLeftSideArray = arcpy.Array()
    topLeftSideArray.add(secondPt)
    topLeftSideArray.add(leftTopCornerPt)
    topLeftSideStreet = arcpy.Polyline(topLeftSideArray)
    topRightSideArray = arcpy.Array()
    topRightSideArray.add(secondPt)
    topRightSideArray.add(rightTopCornerPt)
    topRightSideStreet = arcpy.Polyline(topRightSideArray)
    return {"MainStreet": MainStreet, "LeftMainStreet": leftMainStreet, "RightMainStreet": rightMainStreet,
            "BottomLeftSideSt": botLeftSideStreet, "BottomRightSideSt": botRightSideStreet,
            "TopLeftSideSt": topLeftSideStreet, "TopRightSideSt": topRightSideStreet}

@arcToolReport
def handleFailedStreetUpdate(cursor, row, pointGeo, Length):
    # TODO: This is a hack, why the error occurs will be addressed in future iterations
    # If at first you don't succeed, TRY and TRY again...This function literally tries the same update row,
    # and if the second attempt fails...it just deletes the row.
    try:
        row[0] = CreateMainStreetCEGeometry(pointGeo, abs(Length))
        cursor.updateRow(row)
        arcpy.AddWarning(
                "Nested Try statement triggered at OID {0}. Updated Geometry, but QAQC suggested.".format(
                        str(row[1])))
    except:
        arcpy.AddWarning("Passed and deleted line at OID {0}.".format(str(row[1])))
        cursor.deleteRow()

@arcToolReport
def lineLength(row, Field, constantLen, rowIndex):
    # returns the appropriate length type  based on the options selected: retrieved form field or uses a constant
    if Field and Field != "#":
        return abs(row[rowIndex])
    else:
        return abs(constantLen)


# Main Function
@arcToolReport
def do_analysis(inFeatureClass, outFeatureClass, Length, Field,referenceFeatureClass):
    # This function will execute the main tool, steps are 1. Make a copy 2. Make a centroid 3. Use point centroid of
    # FC within a cursor to construct new geometry 4. Project into Web Mercator 5. Delete intermediates
    try:
        # Delete Existing Output
        arcpy.env.overwriteOutput = True
        if arcpy.Exists(outFeatureClass):
            arcPrint("Deleting existing output feature.", True)
            arcpy.Delete_management(outFeatureClass)
        # Copy/Project feature class to get outputFC
        arcPrint("Making a copy of input feature class for output.", True)
        OutPut = arcpy.CopyFeatures_management(inFeatureClass)
        arcPrint("Gathering feature information.", True)
        # Get feature description and spatial reference information for tool use
        desc = arcpy.Describe(OutPut)
        SpatialRef = desc.spatialReference
        shpType = desc.shapeType
        srName = SpatialRef.name
        arcPrint(
                "The shape type is {0}, and the current spatial reference is: {1}".format(str(shpType), str(srName)),
                True)
        # Get mean center of feature class (for pointGeo)
        if arcpy.Exists(referenceFeatureClass) and referenceFeatureClass != "#":
            arcPrint("Calculating the mean center of the reference feature class.", True)
            meanCenter = arcpy.MeanCenter_stats(referenceFeatureClass)
        else:
            arcPrint("Calculating the mean center of the copied feature.", True)
            meanCenter = arcpy.MeanCenter_stats(OutPut)

        arcPrint("Getting point geometry from copied center.", True)
        pointGeo = arcpy.da.SearchCursor(meanCenter, ["SHAPE@"]).next()[0]  # Only one center, so one record
        # Check if the optional Street Length/ Lot Area field is used.
        if Field and Field != "#":
            arcPrint("Using size field to create output geometries.", True)
            cursorFields = ["SHAPE@", "OID@", Field]
        else:
            arcPrint("Using size input value to create same sized output geometries.", True)
            cursorFields = ["SHAPE@", "OID@"]

        with arcpy.da.UpdateCursor(OutPut, cursorFields) as cursor:
            arcPrint("Replacing existing input geometry.", True)
            count = 1
            if desc.shapeType == "Polyline":
                for row in cursor:
                    # Use two try statements, one time to try to catch the error
                    count += 1
                    try:
                        print("A Line at OID: {0}.".format(str(row[1])))
                        row[0] = CreateMainStreetCEGeometry(pointGeo, lineLength(row, Field, Length, 2))
                        cursor.updateRow(row)
                    except:
                        handleFailedStreetUpdate(cursor, row, pointGeo, lineLength(row, Field, Length, 2))
            else:
                arcPrint("Input geometry is not a polyline. Check arguments.", True)
                arcpy.AddError("Input geometry is not a polyline. Check arguments.")

            arcPrint("Projecting data into Web Mercator Auxiliary Sphere (a CityEngine compatible projection).", True)
            webMercatorAux = arcpy.SpatialReference(3857)
            arcpy.Project_management(OutPut, outFeatureClass, webMercatorAux)  # No preserve shape, keeps 2 vertices
            arcPrint("Cleaning up intermediates.", True)
            arcpy.Delete_management(meanCenter)
            arcpy.Delete_management(OutPut)
            del SpatialRef, desc, cursor, webMercatorAux

    except arcpy.ExecuteError:
        print arcpy.GetMessages(2)
    except Exception as e:
        print e.args[0]


# End do_analysis function
do_analysis(inFeatureClass, outFeatureClass, StreetLength_LotArea, SizeField,referenceFeatureClassCentroid)
