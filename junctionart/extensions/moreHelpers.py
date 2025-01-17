from pyodrx.opendrive import Road
import xml.etree.ElementTree as ET
import xml.dom.minidom as mini
import pyodrx


import os, re
import sys
import csv
import math
import matplotlib.pyplot as plt
from numpy.lib.function_base import append
from .ExtendedOpenDrive import ExtendedOpenDrive
from junctionart.junctions.LaneLinker import LaneLinker
from junctionart.junctions.RoadLinker import RoadLinker
from junctionart.junctions.Geometry import Geometry
from junctionart.extensions.ExtendedRoad import ExtendedRoad
import dill
import logging
import numpy as np

    
def createOdr(name, roads, junctions):

    laneLinker = LaneLinker()
    roadLinker = RoadLinker()
    
    
    
    odr = ExtendedOpenDrive(name, laneLinker=laneLinker)
    for r in roads:
        odr.add_road(r)
    
    for junction in junctions:
        odr.add_junction(junction)

    roadLinker.adjustLaneOffsetsForOdr(odr)
    logging.info(f"moreHelpers: createOdr: starting adjustment. May freeze!!!!!!!!!!!!!")
    odr.adjust_roads_and_lanes()

    return odr


def createOdrByPredecessor(name, roads, junctions, countryCode):

    
    laneLinker = LaneLinker(countryCode=countryCode)
    roadLinker = RoadLinker()
    
    odr = ExtendedOpenDrive(name, laneLinker=laneLinker)
    for r in roads:
        odr.add_road(r)
    
    for junction in junctions:
        odr.add_junction(junction)

    roadLinker.adjustLaneOffsetsForOdr(odr)
    logging.info(f"moreHelpers: createOdrByPredecessor: starting adjustment. May freeze!!!!!!!!!!!!!")
    odr.adjust_roads_and_lanesByPredecessor()

    return odr



def view_road(opendrive,esminipath = 'esmini', returnPlt=False):
    """ write a scenario and runs it in esminis OpenDriveViewer with some random traffic
        Parameters
        ----------
            opendrive (OpenDrive): the pyodrx road to run

            esminipath (str): the path to esmini 
                Default: pyoscx

        

    """
    _scenariopath = os.path.join(esminipath,'bin')
    opendrive.write_xml(os.path.join(_scenariopath,'pythonroad.xodr'),True)

    xodrPath =  os.path.join(esminipath,'bin','pythonroad.xodr')
    return viewRoadFromXODRFile(xodrPath, esminipath, returnPlt=returnPlt)


def view_road_odrviewer(opendrive,esminipath = 'esmini'):
    """ write a scenario and runs it in esminis OpenDriveViewer with some random traffic
        Parameters
        ----------
            opendrive (OpenDrive): the pyodrx road to run

            esminipath (str): the path to esmini 
                Default: pyoscx

        

    """
    _scenariopath = os.path.join(esminipath,'bin')
    opendrive.write_xml(os.path.join(_scenariopath,'pythonroad.xodr'),True)

    xodrPath =  os.path.join(esminipath,'bin','pythonroad.xodr')
    odrViewer = os.path.join(esminipath,'bin','odrviewer.exe')
    print(f"{odrViewer} --odr {xodrPath}")
    os.system(f"{odrViewer} --odr {xodrPath}")
    # viewRoadFromXODRFile(xodrPath, esminipath)

    pass


def viewRoadFromXODRFile(xodrPath, esminipath = 'esmini', returnPlt=False):

    xodrPath = xodrPath.replace("\\", "/")

    ordPlotPath = getODRPlotPath(esminipath)
    print(f"{ordPlotPath} {xodrPath}")

    


    os.system(f"{ordPlotPath} {xodrPath}")
    
    plt = None
    if returnPlt:
        plt = plotRoadFromCSV('track.csv', show=False)
    else:
        plotRoadFromCSV('track.csv')

    os.remove('track.csv')

    return plt



def saveRoadImageFromFile(xodrPath, esminipath = 'esmini', outputDir = ''):

    # raise Exception("not tested yet")


    # print(f"plotting xord: {xodrPath}")

    ordPlotPath = getODRPlotPath(esminipath)

    print(f"{ordPlotPath} {xodrPath}")

    os.system(f"{ordPlotPath} {xodrPath}")
    
    plt = plotRoadFromCSV('track.csv', False)
    os.remove('track.csv')

    outputFile = xodrPath + '-image.png'

    if outputDir != "":
        outputFile = os.path.join(outputDir, os.path.basename(xodrPath) + '-image.png' )

    print(f"saving image to {outputFile}")
    plt.savefig(outputFile)
    plt.close()
    return outputFile

    

def getODRPlotPath(esminipath):
    if os.name == 'posix':
        ordPlotPath = os.path.join(esminipath,'bin','odrplot')
    elif os.name == 'nt':
        ordPlotPath = os.path.join(esminipath,'bin','odrplot')
    return ordPlotPath


def plotRoadFromCSV(csvFile, show=True):
    

    with open(csvFile, 'r') as f:
        reader = csv.reader(f, skipinitialspace=True)
        positions = list(reader)

    ref_x = []
    ref_y = []
    ref_z = []
    ref_h = []

    lane_x = []
    lane_y = []
    lane_z = []
    lane_h = []

    ref = False
    for pos in positions:
        if pos[0] == 'lane':
            if pos[3] == '0':
                ref = True
                ref_x.append([])
                ref_y.append([])
                ref_z.append([])
                ref_h.append([])
            else:
                ref = False
                lane_x.append([])
                lane_y.append([])
                lane_z.append([])
                lane_h.append([])
        else:
            if ref:
                ref_x[-1].append(float(pos[0]))
                ref_y[-1].append(float(pos[1]))
                ref_z[-1].append(float(pos[2]))
                ref_h[-1].append(float(pos[3]) + math.pi/2.0)
            else:
                lane_x[-1].append(float(pos[0]))
                lane_y[-1].append(float(pos[1]))
                lane_z[-1].append(float(pos[2]))
                lane_h[-1].append(float(pos[3]) + math.pi / 2.0)

    p1 = plt.figure(1, figsize=(16,8))
    for i in range(len(ref_x)):
        plt.plot(ref_x[i], ref_y[i], linewidth=2.0, color='#BB5555')
    for i in range(len(lane_x)):
        plt.plot(lane_x[i], lane_y[i], linewidth=1.0, color='#3333BB')

    # hdg_lines = []
    # for i in range(len(h)):
    #     for j in range(len(h[i])):
    #         hx = x[i][j] + H_SCALE * math.cos(h[i][j])
    #         hy = y[i][j] + H_SCALE * math.sin(h[i][j])
    #         plt.plot([x[i][j], hx], [y[i][j], hy])


    p1.gca().set_aspect('equal', adjustable='box')

    if show:
        plt.show()
    return plt


def getJunctionSelection(isJunction):
    if isJunction:
        return 1
    return -1


def getConnectionRoads(roads, junction):
    """ Finds connection roads which exists in the junction only

    Args:
        roads (dictionary): key - id, value - road object
        junction ([type]): [description]
    """

    # print(roads)
    connectionRoads = []
    for connection in junction.connections:
        connectionRoadId = connection.connecting_road
        # print(f"getConnectionRoads connectionRoadId: {connectionRoadId}")
        connectionRoads.append(getRoadFromRoadDic(roads, connectionRoadId))
    
    return connectionRoads


def getRoadFromRoadDic(roads, roadId):
    return roads[str(roadId)]




def printRoadPositions(odr):
    """This method only works after roads has been adjusted.

    Args:
        odr ([type]): [description]
    """
    for road in odr.roads.values():
        print(f"roadId: {road.id}, \n  start_adj: {road.getAdjustedStartPosition()}\tend_adj: {road.getAdjustedEndPosition()}")




def headingToTangent(h, tangentMagnitude):

    # TODO tangent depends on maximum speed and heading. 

    xComponent = math.cos(h) * tangentMagnitude
    yComponent = math.sin(h) * tangentMagnitude

    return (xComponent, yComponent)


# change the XML tag with standalone attribute
def set_standalone_attribute(filename):
    if filename is None:
        return False
    else:
       f = open(filename, "r")
       content = f.readlines()
       f.close()
       f = open(filename, "w")
       content[0] = "<?xml version=\"1.0\" standalone=\"yes\"?> \n"
       for line in content:
           f.write(line)
       f.close()
       pass

"""
    change revMinor attribute to 4
"""

def change_revMinor(filepath):
    if filepath is None:
        return False
    else:
        f = open(filepath, "r", encoding="utf-8")
        content = f.readlines()
        f.close()
        f = open(filepath, "w")
        for line in content:
            if "header" in line:
                line = line.replace('revMinor="5"', 'revMinor="4"')
            f.write(line)
        f.close()
        pass


# create compitable file for road runner

def modify_xodr_for_roadrunner(filepath):
    set_standalone_attribute(filepath)
    change_revMinor(filepath)



def laneWidths(lane, laneLength):
    """[summary]

    Args:
        lane ([type]): [description]
        laneLength ([type]): [description]

    Returns:
        startWidth
        endWidth
    """

    coeffs = [lane.a, lane.b, lane.c, lane.d]
    pRange = [0, laneLength]
    return Geometry.evalPoly(coeffs, pRange)


def getObjectsFromDill(path):
    if not os.path.isfile(path):
        raise FileNotFoundError(f"{path} does not exist!")

    objects = None

    with open(path, "rb") as f:
        objects = dill.load(f)

    return objects


def reverseCP(cp):
        return pyodrx.ContactPoint.start if (cp == pyodrx.ContactPoint.end) else pyodrx.ContactPoint.end
