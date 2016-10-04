# --------------------------------
# Name: PrepareLotAssociations.py
# Purpose: This scripting tool is designed to prepare a feature class's records for CityEngine by associating it with
# an optional target geometry or a default geometry based around the centroid of the input feature class.
# Current Owner: David Wasserman
# Last Modified: 5/15/2016
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
import os, sys, arcpy, math,copy

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
        pass
    except:
        print("Could not create message, bad arguments.")
        pass


def getFIndex(field_names, field_name):
    """Will get the index for a  arcpy da.cursor based on a list of field names as an input.
    Assumes string will match if all the field names are made lower case."""
    try:
        return [str(i).lower() for i in field_names].index(str(field_name).lower())
        # Make iter items lower case to get right time field index.
    except:
        print("Couldn't retrieve index for {0}, check arguments.".format(str(field_name)))
        return None

@arcToolReport
def FieldExist(featureclass, fieldname):
    """ Check if a field in a feature class field exists and return true it does, false if not."""
    fieldList = arcpy.ListFields(featureclass, fieldname)
    fieldCount = len(fieldList)
    if (fieldCount >= 1) and fieldname.strip():  # If there is one or more of this field return true
        return True
    else:
        return False

@arcToolReport
def AddNewField(in_table, field_name, field_type, field_precision="#", field_scale="#", field_length="#",
                field_alias="#",
                field_is_nullable="#", field_is_required="#", field_domain="#"):
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
def CreateLotCEGeometry(pointObj, translationDistance):
    # Create a polygon object consisting of a simple square based on the location of a passed point
    cornerOffset = (translationDistance) * .5
    firstCorner = pointObj.getPart(0)
    secondCorner = pointObj.getPart(0)
    thirdCorner = pointObj.getPart(0)
    fourthCorner = pointObj.getPart(0)
    firstCorner.Y += -cornerOffset
    firstCorner.X += -cornerOffset
    secondCorner.Y += cornerOffset
    secondCorner.X += -cornerOffset
    thirdCorner.Y += cornerOffset
    thirdCorner.X += cornerOffset
    fourthCorner.Y += -cornerOffset
    fourthCorner.X += cornerOffset
    array = arcpy.Array()
    array.add(firstCorner)
    array.add(secondCorner)
    array.add(thirdCorner)
    array.add(fourthCorner)
    Lot = arcpy.Polygon(array)
    return Lot

@arcToolReport
def handleFailedLotUpdate(cursor, row, pointGeo, Length):
    """To deal with update cursor instability/script errors, this function will try update the row update
    a second time. If it fails, it will delete the row in question. """
    try:
        row[0] = CreateLotCEGeometry(pointGeo, abs(Length))
        cursor.updateRow(row)
        arcpy.AddWarning(
                "Nested Try statement triggered at OID {0}. Updated Geometry, but QAQC suggested.".format(
                        str(row[1])))

    except:
        arcpy.AddWarning("Passed and deleted line at OID {0}.".format(str(row[1])))
        cursor.deleteRow()

@arcToolReport
def lotArea(row, Field, constantArea, fNames):
    """Returns the appropriate area type  based on the options selected:
     retrieved form field or uses a constant"""
    if Field and getFIndex(fNames,str(Field)):
        return abs(row[getFIndex(fNames, Field)])
    else:
        return abs(constantArea)


# Main Function
@arcToolReport
def do_analysis(inFeatureClass, outFeatureClass, Area, Field,referenceFeatureClass):
    """This function will create lots in one location based on the incoming reference centroid for the
    purpose of being used for data driven design applications in CityEngine."""
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
            meanCenter = arcpy.MeanCenter_stats(inFeatureClass)

        arcPrint("Getting point geometry from copied center.", True)
        pointGeo = copy.deepcopy( arcpy.da.SearchCursor(meanCenter, ["SHAPE@"]).next()[0])  # Only one center, so one record


        # Check if the optional Street Length/ Lot Area field is used.
        if Field and FieldExist(OutPut,Field):
            arcPrint("Using size field to create output geometries.", True)
            cursorFields = ["SHAPE@", "OID@", Field]
        else:
            arcPrint("Using size input value to create same sized output geometries.", True)
            cursorFields = ["SHAPE@", "OID@"]

        with arcpy.da.UpdateCursor(OutPut, cursorFields) as cursor:
            arcPrint("Replacing existing input geometry.", True)
            count = 1
            if desc.shapeType == "Polygon":
                for row in cursor:
                    count += 1
                    try:
                        print("A Polygon at OID: {0}.".format(str(row[1])))
                        row[0] = CreateLotCEGeometry(pointGeo, math.sqrt(lotArea(row, Field, Area, cursorFields)))
                        cursor.updateRow(row)

                    except:
                        handleFailedLotUpdate(cursor, row, pointGeo, math.sqrt(lotArea(row, Field, Area, cursorFields)))
            else:
                arcPrint("Input geometry is not a polygon. Check arguments.")
                arcpy.AddError("Input geometry is not a polygon. Check arguments.")

            arcPrint("Projecting data into Web Mercator Auxiliary Sphere (a CityEngine compatible projection).", True)
            webMercatorAux = arcpy.SpatialReference(3857)
            arcpy.Project_management(OutPut, outFeatureClass, webMercatorAux)
            arcPrint("Cleaning up intermediates.", True)
            arcpy.Delete_management(meanCenter)
            arcpy.Delete_management(OutPut)
            del SpatialRef, desc, cursor, webMercatorAux
    except arcpy.ExecuteError:
        print(arcpy.GetMessages(2))
    except Exception as e:
        print(e.args[0])


# End do_analysis function
# Main Script
if __name__ == "__main__":
    do_analysis(inFeatureClass, outFeatureClass, StreetLength_LotArea, SizeField,referenceFeatureClassCentroid)
