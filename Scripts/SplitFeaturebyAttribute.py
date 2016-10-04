# --------------------------------
# Name: SplitFeaturebyAttribute.py
# Purpose: Prepare a series of files from the prepare CEAssociations script or some custom geometry modification process
# to be separate layers for CityEngine manipulation
# Current Owner: David Wasserman
# Last Modified: 3/15/2016
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
import arcpy
import os
import numpy

# Define Inputs
inFeatureClass = arcpy.GetParameterAsText(0)
outWorkSpace = arcpy.GetParameterAsText(1)
uniqueField = arcpy.GetParameterAsText(2)
compactWorkspace = arcpy.GetParameter(3)


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
def unique_values(table, field):
    # Get an iterable with unique values
    data = arcpy.da.TableToNumPyArray(table, [field])
    return numpy.unique(data[field])

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
def arcPrint(string, progressor_Bool=False):
    # This function is used to simplify using arcpy reporting for tool creation,if progressor bool is true it wll
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

@arcToolReport
def constructSQLEqualityQuery(fieldName, value, dataSource):
    # Creates a workspace sensitive equality query to be used in arcpy.
    return "{0} = '{1}'".format(arcpy.AddFieldDelimiters(dataSource, fieldName), str(value))


# Main Function Definition
@arcToolReport
def do_analysis(inFeatureClass, outWorkSpace, explodeID, compactBool=True):
    # This tool will split a feature class into multiple feature classes based on a field
    try:
        if arcpy.Exists(outWorkSpace):
            arcpy.env.workspace = outWorkSpace
            arcpy.env.overwriteOutput = True
            arcPrint("The current work space is: {0}.".format(outWorkSpace), True)
            workSpaceTail = os.path.split(outWorkSpace)[1]
            newExplodeField = arcpy.ValidateFieldName("ExplodeID", outWorkSpace)
            arcPrint("Adding a text explode ID to cast the target field as text.", True)
            AddNewField(inFeatureClass, newExplodeField, "TEXT")
            arcPrint("Calculating an explode ID for the newly added field equal to the field selected.", True)
            arcpy.CalculateField_management(inFeatureClass, newExplodeField, "str(!" + str(explodeID) + "!)",
                                            "PYTHON_9.3")
            arcPrint("Generating unique values from the explode ID field.", True)
            explodeList = numpy.sort(unique_values(inFeatureClass, newExplodeField))
            arcPrint(
                    "Using explode field's unique values to generate new feature classes in {0}.".format(
                            str(workSpaceTail)))
            for newFeatureClassName in explodeList:
                try:
                    arcPrint("Determining name and constructing query for new feature class.", True)
                    newFCName = str(newFeatureClassName)
                    outExplodeFC = arcpy.ValidateTableName(newFCName, outWorkSpace)
                    expression = constructSQLEqualityQuery(newExplodeField, newFeatureClassName, inFeatureClass)
                    arcpy.Select_analysis(inFeatureClass, outExplodeFC, expression)
                    arcPrint(
                            "Selected out unique ID: {0} and created a new feature class in {1}".format(newFCName,
                                                                                                        workSpaceTail),
                            True)
                except:
                    arcPrint(
                            "The unique value ID {0}, could not be extracted. Check arguments of tool.".format(
                                    str(newFCName)))
                    pass
            if compactBool:
                arcPrint("Compacting workspace.", True)
                arcpy.Compact_management(outWorkSpace)
            arcPrint("Tool execution complete.", True)
            pass
        else:
            arcPrint("The desired workspace does not exist. Tool execution terminated.", True)
            arcpy.AddWarning("The desired workspace does not exist.")

    except arcpy.ExecuteError:
        print(arcpy.GetMessages(2))
    except Exception as e:
        print(e.args[0])

# Main Script
if __name__ == "__main__":
    do_analysis(inFeatureClass, outWorkSpace, uniqueField, compactWorkspace)
