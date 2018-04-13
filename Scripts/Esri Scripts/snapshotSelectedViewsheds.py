'''
Created on Oct 31, 2017
Modified on Apr 6, 2018
@author: Esri R&D Zurich
Written by: Thomas Fuchs
Edited by: David Wasserman
License
Copyright Esri R&D Zurich, David Wasserman

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
from scripting import *
import math

hRes = 1240
nameBase = "360 "
ext = ".png"

# get a CityEngine instance
ce = CE()

def getCamera(view):
    camPos      = view.getCameraPosition()
    camRot      = view.getCameraRotation()
    camAoV      = view.getCameraAngleOfView()
    camPoI      = view.getCameraPoI()
    camPoIDist  = math.sqrt(math.pow(camPoI[0]-camPos[0],2)+ \
                            math.pow(camPoI[1]-camPos[1],2)+ \
                            math.pow(camPoI[2]-camPos[2],2))
    camPersp    = view.getCameraPerspective()
    return camPos,camRot,camAoV,camPoIDist,camPersp

def setCamera(view,camPos,camRot,camAoV,camPoIDist,camPersp = True):
    view.setCameraPosition(camPos[0],camPos[1],camPos[2])
    view.setCameraRotation(camRot[0],camRot[1],camRot[2])
    view.setPoIDistance(camPoIDist)
    view.setCameraAngleOfView(min(160.0,camAoV))
    view.setCameraPerspective(camPersp)
    print("Camera set.")

def getViewshed(viewshed):
    vsPos   = ce.getObserverPoint(viewshed)
    vsRot   = [0.0, 0.0, 0.0]
    if ce.isViewshed(viewshed):
        print("Working with view shed.")
        vsRot[0]    = ce.getTiltAndHeadingAngles(viewshed)[0]
        vsRot[1]    = -ce.getTiltAndHeadingAngles(viewshed)[1]
        vsAoV       = ce.getAnglesOfView(viewshed)[0]
        vsPoIDist   = ce.getViewDistance(viewshed)
        vsRatio     = vsAoV/ce.getAnglesOfView(viewshed)[1]
    elif ce.isViewDome(viewshed):
        vsAoV       = 360.0
        vsPoIDist   = ce.getViewDistance(viewshed)
        vsRatio     = 1
        print("Working with view dome.")
    elif ce.isViewCorridor(viewshed):
        vsPoI       = ce.getPOI(viewshed)
        vsRot[0]    = math.atan2(vsPoI[1]-vsPos[1], \
                                math.sqrt(math.pow(vsPoI[0]-vsPos[0],2)+ \
                                math.pow(vsPoI[2]-vsPos[2],2)))*180/math.pi
        vsRot[1]    = -math.atan2(vsPoI[0]-vsPos[0], \
                                  -(vsPoI[2]-vsPos[2]))*180/math.pi
        vsAoV       = ce.getAnglesOfView(viewshed)[0]
        vsPoIDist   = math.sqrt(math.pow(vsPoI[0]-vsPos[0],2)+ \
                                math.pow(vsPoI[1]-vsPos[1],2)+ \
                                math.pow(vsPoI[2]-vsPos[2],2))
        vsRatio     = vsAoV/ce.getAnglesOfView(viewshed)[1]
        print("Working with view corridor.")
    else:
        return
    vsName  = ce.getName(viewshed)
    return vsPos,vsRot,vsAoV,vsPoIDist,vsRatio,vsName

def snapshot360(view,vsName,extension=".png",prefix="",res=1080):
    # make six square snapshots
    view.setCameraAngleOfView(90.0)
    vdAoV = [(0,0),(0,90),(0,180),(0,-90),(90,0),(-90,0)]
    suffixes = ["_f","_l","_b","_r","_u","_d"]
    for i, suffix in enumerate(suffixes):
        view.setCameraRotation(vdAoV[i][0],vdAoV[i][1],0)
        view.snapshot(ce.toFSPath('images/'+prefix+vsName+suffix+extension),res,res)

def snapshotViewshed(view,viewshed,extension=".png",prefix="",res=1080):
    # get initial camera parameters
    camPos,camRot,camAoV,camPoIDist,camPersp = getCamera(view)
    # get viewshed parameters
    vsPos,vsRot,vsAoV,vsPoIDist,vsRatio,vsName = getViewshed(viewshed)
    if ce.isViewDome(viewshed):
        setCamera(view,vsPos,vsRot,vsAoV,vsPoIDist)
        snapshot360(view,vsName,extension,prefix,res)
    else:
        # set camera to viewshed parameters
        setCamera(view,vsPos,vsRot,vsAoV,vsPoIDist)
        # make a snapshot
        view.snapshot(ce.toFSPath('images/'+prefix+vsName+extension),res*vsRatio,res)
    # reset camera to initial camera parameters
    setCamera(view,camPos,camRot,camAoV,camPoIDist,camPersp)
    
if __name__ == '__main__':
    
    # get selected viewsheds, view domes and view corridors
    view            = ce.getObjectsFrom(ce.get3DViews())[0]
    viewsheds       = ce.getObjectsFrom(ce.selection(),ce.isViewshed)
    viewdomes       = ce.getObjectsFrom(ce.selection(),ce.isViewDome)
    viewCorridors   = ce.getObjectsFrom(ce.selection(),ce.isViewCorridor)
    
    # preparations
    initialSelection = ce.selection()
    ce.setSelection([])
    for al in ce.getObjectsFrom(ce.scene,ce.isAnalysisLayer):
        ce.setLayerPreferences(al,"Visible",False)
    tmpLayer = ce.addAnalysisLayer('TEMP Analysis Layer')
    
    # make snapshots
    for viewshed in (viewsheds+viewdomes+viewCorridors):
        if ce.isViewCorridor(viewshed):
            ce.setLayerPreferences(tmpLayer,"Visible",True)
        else:
            ce.setLayerPreferences(tmpLayer,"Visible",False)
        tmpViewshed = ce.copy(viewshed,False,tmpLayer)
        snapshotViewshed(view,tmpViewshed[0],ext,nameBase,hRes)
        ce.delete(tmpViewshed)
    
    # clean up
    ce.delete(tmpLayer)
    for al in ce.getObjectsFrom(ce.scene,ce.isAnalysisLayer):
        ce.setLayerPreferences(al,"Visible",True)
    ce.setSelection(initialSelection)
    