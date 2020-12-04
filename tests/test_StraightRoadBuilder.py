import unittest, os
from junctions.StraightRoadBuilder import StraightRoadBuilder
from scipy.interpolate import CubicHermiteSpline
from junctions.JunctionHarvester import JunctionHarvester
import numpy as np
import pyodrx, extensions
from junctions.JunctionBuilder import JunctionBuilder
from library.Configuration import Configuration
import junctions

from junctions.Direction import CircularDirection
from junctions.RoadLinker import RoadLinker
from junctions.LaneSides import LaneSides


class test_StraightRoadBuilder(unittest.TestCase):

    def setUp(self):
        
        self.configuration = Configuration()

        self.straightRoadBuilder = StraightRoadBuilder()
        self.roadLinker = RoadLinker()

    

    def test_LeftTurnLanes(self):
        
        roads = []
        roads.append(self.straightRoadBuilder.createStraightRoad(0, length = 10, isLeftTurnLane=True))

        odrName = "test_LeftTurnLane"
        odr = extensions.createOdrByPredecessor(odrName, roads, [])
        
        extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))

        xmlPath = f"output/test-LeftTurnLane.xodr"
        odr.write_xml(xmlPath)

    def test_RightTurnLanes(self):
        
        roads = []
        roads.append(self.straightRoadBuilder.createStraightRoad(0, length = 10, isRightTurnLane=True))

        odrName = "test_RightTurnLane"
        odr = extensions.createOdrByPredecessor(odrName, roads, [])
        
        extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))

        xmlPath = f"output/test-RightTurnLane.xodr"
        odr.write_xml(xmlPath)


    def test_TurnLanes(self):
        
        roads = []
        roads.append(self.straightRoadBuilder.createStraightRoad(0, length = 10, isRightTurnLane=True, isLeftTurnLane=True))
        roads.append(self.straightRoadBuilder.createStraightRoad(1, length = 10, n_lanes=2))

        roads[0].updateSuccessor(pyodrx.ElementType.road, roads[1].id, pyodrx.ContactPoint.start)
        roads[1].updatePredecessor(pyodrx.ElementType.road, roads[0].id, pyodrx.ContactPoint.end)

        odrName = "test_RightTurnLane"
        odr = extensions.createOdrByPredecessor(odrName, roads, [])
        
        extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))

        xmlPath = f"output/test-TurnLanes.xodr"
        odr.write_xml(xmlPath)


    def test_MergeLanes(self):
        
        roads = []
        roads.append(self.straightRoadBuilder.createStraightRoad(0, length = 10, isLeftMergeLane=True))

        odrName = "test_RightTurnLane"
        odr = extensions.createOdrByPredecessor(odrName, roads, [])
        
        extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))

        xmlPath = f"output/test-LeftMergeLane.xodr"
        odr.write_xml(xmlPath)

        roads = []
        roads.append(self.straightRoadBuilder.createStraightRoad(0, length = 10, isRightMergeLane=True))

        odrName = "test_RightTurnLane"
        odr = extensions.createOdrByPredecessor(odrName, roads, [])
        
        extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))

        xmlPath = f"output/test-RightMergeLanes.xodr"
        odr.write_xml(xmlPath)

        roads = []
        roads.append(self.straightRoadBuilder.createStraightRoad(0, length = 10, n_lanes=2))
        roads.append(self.straightRoadBuilder.createStraightRoad(1, length = 10, isLeftMergeLane=True, isRightMergeLane=True))

        roads[0].updateSuccessor(pyodrx.ElementType.road, roads[1].id, pyodrx.ContactPoint.start)
        roads[1].updatePredecessor(pyodrx.ElementType.road, roads[0].id, pyodrx.ContactPoint.end)

        odrName = "test_RightTurnLane"
        odr = extensions.createOdrByPredecessor(odrName, roads, [])
        
        extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))

        xmlPath = f"output/test-MergeLanes.xodr"
        odr.write_xml(xmlPath)


    def test_mergeAndTurns(self):

        roads = []
        roads.append(self.straightRoadBuilder.createStraightRoad(0, length = 10, n_lanes=2))
        roads.append(self.straightRoadBuilder.createStraightRoad(1, length = 10, isLeftMergeLane=True, isRightMergeLane=True))
        roads.append(self.straightRoadBuilder.createStraightRoad(2, length = 10))
        roads.append(self.straightRoadBuilder.createStraightRoad(3, length = 10, isRightTurnLane=True, isLeftTurnLane=True))
        roads.append(self.straightRoadBuilder.createStraightRoad(4, length = 10, n_lanes=2))

        self.roadLinker.linkConsequtiveRoadsWithNoBranches(roads)
        odrName = "test_RightTurnLane"
        odr = extensions.createOdrByPredecessor(odrName, roads, [])
        
        extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))

        xmlPath = f"output/test-MergeAndTurns.xodr"
        odr.write_xml(xmlPath)



    def test_LeftTurnLaneOnRight(self):
        roads = []
        roads.append(self.straightRoadBuilder.createStraightRoad(0, length = 10, laneSides=LaneSides.RIGHT,
                                                                     isLeftTurnLane=True))

        odrName = "test_RightTurnLane"
        odr = extensions.createOdrByPredecessor(odrName, roads, [])
        
        extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))

        xmlPath = f"output/test_LeftTurnLaneOnRight.xodr"
        odr.write_xml(xmlPath)



    def test_RightTurnLaneOnLeft(self):
        roads = []
        roads.append(self.straightRoadBuilder.createStraightRoad(0, length = 10, laneSides=LaneSides.LEFT,
                                                                     isRightTurnLane=True))

        odrName = "test_RightTurnLane"
        odr = extensions.createOdrByPredecessor(odrName, roads, [])
        
        extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))

        xmlPath = f"output/test_RightTurnLaneOnLeft.xodr"
        odr.write_xml(xmlPath)


    def test_createStraightRoadWithLeftTurnLanesOnRight(self):
        roads = []

        roads.append(self.straightRoadBuilder.createStraightRoadWithLeftTurnLanesOnRight(1, length = 10, n_lanes=1, 
                                                                                        numberOfLeftTurnLanesOnRight=2))
        self.roadLinker.linkConsequtiveRoadsWithNoBranches(roads)

        odrName = "test_RightTurnLane"
        odr = extensions.createOdrByPredecessor(odrName, roads, [])
        
        extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))

        xmlPath = f"output/test_createStraightRoadWithLeftTurnLanesOnRight1.xodr"
        odr.write_xml(xmlPath)
        roads = []

        roads.append(self.straightRoadBuilder.createStraightRoadWithDifferentLanes(0, length=10, junction=-1, n_lanes_left=3, n_lanes_right=1))
        roads.append(self.straightRoadBuilder.createStraightRoadWithLeftTurnLanesOnRight(1, length = 10, n_lanes=1, 
                                                                                        isLeftTurnLane=True, 
                                                                                        isRightTurnLane=True,
                                                                                        numberOfLeftTurnLanesOnRight=2))
        roads.append(self.straightRoadBuilder.createStraightRoadWithDifferentLanes(2, length=10, junction=-1, n_lanes_left=2, n_lanes_right=4))
        self.roadLinker.linkConsequtiveRoadsWithNoBranches(roads)

        odrName = "test_RightTurnLane"
        odr = extensions.createOdrByPredecessor(odrName, roads, [])
        
        extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))

        xmlPath = f"output/test_createStraightRoadWithLeftTurnLanesOnRight2.xodr"
        odr.write_xml(xmlPath)
