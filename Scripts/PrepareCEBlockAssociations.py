# --------------------------------
# Name:PrepareCEBlockAssociations.py
# Purpose: This scripting tool is designed to prepare a feature class's records for CityEngine by associating it with
# a geometry used to create CE Blocks with curb extension supporting geometry class.
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
import os, sys, arcpy, math, copy

# Define Inputs
inFeatureClass = arcpy.GetParameterAsText(0)
outFeatureClass = arcpy.GetParameterAsText(1)
StreetLength_LotArea = arcpy.GetParameter(2)  # Units of projection
SizeField = arcpy.GetParameterAsText(3)  # CR: more descriptive
BlockWidth = arcpy.GetParameter(4)
referenceFeatureClassCentroid = arcpy.GetParameterAsText(5)  # optional reference FC to get centroid from


# Function Definitions
def funcReport(function=None, reportBool=False):
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
                print(
                "{0} - function failed -|- Function arguments were:{1}.".format(str(function.__name__), str(args)))
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
                        "{0} - function failed -|- Function arguments were:{1}.".format(str(function.__name__),
                                                                                        str(args)))
                print(
                "{0} - function failed -|- Function arguments were:{1}.".format(str(function.__name__), str(args)))
                print(e.args[0])

        return funcWrapper

    if not function:  # User passed in a bool argument
        def waiting_for_function(function):
            return arcToolReport_Decorator(function)

        return waiting_for_function
    else:
        return arcToolReport_Decorator(function)


def getFIndex(field_names, field_name):
    """Will get the index for a  arcpy da.cursor based on a list of field names as an input.
    Assumes string will match if all the field names are made lower case."""
    try:
        return [str(i).lower() for i in field_names].index(str(field_name).lower())
        # Make iter items lower case to get right time field index.
    except:
        print("Couldn't retrieve index for {0}, check arguments.".format(str(field_name)))
        return None


def getFields(featureClass, excludedTolkens=["OID", "Geometry"], excludedFields=["shape_area", "shape_length"]):
    try:
        fcName = os.path.split(featureClass)[1]
        field_list = [f.name for f in arcpy.ListFields(featureClass) if f.type not in excludedTolkens
                      and f.name.lower() not in excludedFields]
        arcPrint("The field list for {0} is:{1}".format(str(fcName), str(field_list)), True)
        return field_list
    except:
        arcPrint("Could not get fields for the following input {0}, returned an empty list.".format(str(featureClass)),
                 True)
        arcpy.AddWarning(
                "Could not get fields for the following input {0}, returned an empty list.".format(str(featureClass)))
        field_list = []
        return field_list


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
        print("Could not create message, bad arguments.")
        pass


@arcToolReport()
def FieldExist(featureclass, fieldname):
    """ Check if a field in a feature class field exists and return true it does, false if not."""
    fieldList = arcpy.ListFields(featureclass, fieldname)
    fieldCount = len(fieldList)
    if (fieldCount >= 1) and fieldname.strip():  # If there is one or more of this field return true
        return True
    else:
        return False


@arcToolReport()
def AddNewField(in_table, field_name, field_type, field_precision="#", field_scale="#", field_length="#",
                field_alias="#", field_is_nullable="#", field_is_required="#", field_domain="#"):
    """Add a new field if it currently does not exist...add field alone is slower than checking first."""
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
def CreateMainStreetBlockCEGeometry(pointObj, translationDistance, sideBlockWidth=50):
    """ Create a dictionary of polyline objects consisting of a simple line based on the location of a passed point
     This function in the future will be used to create a center street with two side blocks for the purpose
     of lot creation in CityEngine."""
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


def copyAlteredRow(row, fieldList, replacementDict):
    """Copy a row from a cursor based on a past list of fields in field list. If replacement dictionary has a key,
    replace the row value copied with the replacement."""
    try:
        newRow = []
        keyList = replacementDict.keys()
        for field in fieldList:
            try:
                if field in keyList:
                    newRow.append(replacementDict[field])
                else:
                    newRow.append(row[getFIndex(fieldList, field)])
            except:
                arcPrint("Could not replace field {0} with its accepted value. Check field names for match.".format(
                        str(field)), True)
                newRow.append(None)  # Append a null value where it cannot find a value to the list.
        return newRow
    except:
        arcPrint("Could not get row fields for the following input {0}, returned an empty list.".format(str(row)), True)
        arcpy.AddWarning(
                "Could not get row fields for the following input {0}, returned an empty list.".format(str(row)))
        newRow = []
        return newRow


@arcToolReport
def lineLength(row, Field, constantLen, fNames):
    """Returns the appropriate value type  based on the options selected:
    retrieved form field or uses a constant"""
    if Field and getFIndex(fNames, str(Field)):
        return abs(row[getFIndex(fNames, Field)])
    else:
        return abs(constantLen)


# Main Function
@arcToolReport
def do_analysis(inFeatureClass, outFeatureClass, lengthNum, lengthField, blockWidthValue, referenceFeatureClass):
    """This function will create blocks in one location based on the incoming reference centroid for the
    purpose of being used for data driven design applications in CityEngine."""
    # try:
    # Delete Existing Output
    arcpy.env.overwriteOutput = True
    if arcpy.Exists(outFeatureClass):
        arcPrint("Deleting existing output feature.", True)
        arcpy.Delete_management(outFeatureClass)
    workspace = os.path.dirname(outFeatureClass)
    tempOutName = arcpy.ValidateTableName("TempBlockFC_1", workspace)
    tempOutFeature = os.path.join(workspace, tempOutName)
    # Add New Fields
    arcPrint("Adding new fields for old object IDs and geometry name.", True)
    OldObjectIDName = "UniqueFeatID"
    GeometryName = "CEStreetName"
    AddNewField(inFeatureClass, OldObjectIDName, "LONG")
    AddNewField(inFeatureClass, GeometryName, "TEXT")
    # Create feature class to get outputFC
    arcPrint("Making a new output feature class using the input as a template", True)
    OutPut = arcpy.CreateFeatureclass_management(workspace, tempOutName, "POLYLINE", template=inFeatureClass,
                                                 spatial_reference=inFeatureClass)

    arcPrint("Gathering feature information.", True)
    # Get feature description and spatial reference information for tool use
    desc = arcpy.Describe(inFeatureClass)
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

    fieldNames = getFields(inFeatureClass)
    arcPrint("Getting point geometry from copied center.", True)
    pointGeo = copy.deepcopy(arcpy.da.SearchCursor(meanCenter, ["SHAPE@"]).next()[0])  # Only one center, so one recor

    # Check if the optional Street Length/ Lot Area field is used.
    idsAndFieldSearchNames = ["SHAPE@"] + fieldNames
    arcPrint("The search cursor's fields and tags are:{0}".format(str(idsAndFieldSearchNames)), True)
    records = []
    with arcpy.da.SearchCursor(inFeatureClass, idsAndFieldSearchNames) as cursorSearch:
        arcPrint("Loading input feature classes rows into a new record list.", True)
        for search_row in cursorSearch:
            records.append(search_row)
    arcPrint("Inserting new rows and geometries to new feature class.", True)
    count = 0
    with arcpy.da.InsertCursor(tempOutFeature, idsAndFieldSearchNames) as cursorInsert:
        if desc.shapeType == "Polyline":
            for row in records:
                # Use two try statements, one time to try to catch the error
                count += 1
                try:
                    arcPrint("A creating geometry dictionary for feature iteration: {0}.".format(str(count)))
                    geoDict = CreateMainStreetBlockCEGeometry(pointGeo, lineLength(row, lengthField, lengthNum,
                                                                                   idsAndFieldSearchNames),
                                                              blockWidthValue)
                    # print geoDict
                    for key in geoDict.keys():
                        try:
                            # arcPrint(key)
                            rowList = copyAlteredRow(row, idsAndFieldSearchNames,
                                                     {"SHAPE@": geoDict[key], OldObjectIDName: count,
                                                      GeometryName: str(key)})
                            cursorInsert.insertRow(rowList)
                        except:
                            arcpy.AddWarning("Passed line at iteration {0}.".format(str(count)))
                            pass
                except:
                    arcpy.GetMessage(2)
                    arcPrint("Failed on iteration {0}.".format(str(count)), True)
                    pass
        else:
            arcPrint("Input geometry is not a polyline. Check arguments.", True)
            arcpy.AddError("Input geometry is not a polyline. Check arguments.")

    arcPrint("Projecting data into Web Mercator Auxiliary Sphere (a CityEngine compatible projection).", True)
    webMercatorAux = arcpy.SpatialReference(3857)
    arcpy.Project_management(OutPut, outFeatureClass, webMercatorAux)
    arcPrint("Cleaning up intermediates.", True)
    arcpy.Delete_management(meanCenter)
    arcpy.Delete_management(OutPut)
    arcpy.DeleteField_management(inFeatureClass, OldObjectIDName)
    arcpy.DeleteField_management(inFeatureClass, GeometryName)
    del SpatialRef, desc, cursorSearch, webMercatorAux, cursorInsert

    # except arcpy.ExecuteError:
    #     print(arcpy.GetMessages(2))
    # except Exception as e:
    #     print(e.args[0])


# End do_analysis function
# Main Script
if __name__ == "__main__":
    do_analysis(inFeatureClass, outFeatureClass, StreetLength_LotArea, SizeField, BlockWidth,
                referenceFeatureClassCentroid)
