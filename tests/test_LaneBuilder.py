import unittest

import numpy as np
import os, dill
from junctionart.extensions.CountryCodes import CountryCodes
import pyodrx as pyodrx 
from junctionart.junctions.JunctionMerger import JunctionMerger
import junctionart.extensions as extensions
from junctionart.library.Configuration import Configuration
from junctionart.junctions.JunctionBuilder import JunctionBuilder
from junctionart.junctions.RoadBuilder import RoadBuilder
from junctionart.junctions.LaneBuilder import LaneBuilder

from junctionart.junctions.LaneLinker import LaneLinker

from junctionart.junctions.StraightRoadBuilder import StraightRoadBuilder


class test_LaneBuilder(unittest.TestCase):

    def setUp(self):
        
        self.configuration = Configuration()
        self.esminiPath = self.configuration.get("esminipath")
        self.roadBuilder = RoadBuilder()
        self.laneBuilder = LaneBuilder()
        self.laneLinker = LaneLinker(CountryCodes.US)
        self.straightRoadBuilder = StraightRoadBuilder()


    
    def test_RightLane(self):
        # test scenario for connection road
        
        roads = []
        roads.append(pyodrx.create_straight_road(0, 10))
        # roads.append(self.roadBuilder.createSimpleCurve(1, np.pi/4, True, curvature = 0.2))
        # roads.append(pyodrx.create_straight_road(2, 10))


        # roads[0].add_successor(pyodrx.ElementType.junction,1)

        # roads[1].add_predecessor(pyodrx.ElementType.road,0,pyodrx.ContactPoint.end)
        # # roads[1].add_predecessor(pyodrx.ElementType.road,0,pyodrx.ContactPoint.start)
        # roads[1].add_successor(pyodrx.ElementType.road,2,pyodrx.ContactPoint.start)

        # roads[2].add_predecessor(pyodrx.ElementType.junction,1, pyodrx.ContactPoint.end)


        odrName = "test_connectionRoad"
        odr = extensions.createOdrByPredecessor(odrName, roads, [], CountryCodes.US)
        
        self.laneBuilder.addRightTurnLaneUS(roads[0], 3)
        # self.laneBuilder.addRightLaneUS(roads[1])

        odr.resetAndReadjust(byPredecessor=True)

        extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))

        
        xmlPath = f"output/test-RightLane.xodr"
        odr.write_xml(xmlPath)


    def test_DifferentLaneConfigurations(self):
        roads = []
        roads.append(self.straightRoadBuilder.createWithDifferentLanes(0, 10, n_lanes_left=1, n_lanes_right=1))
        connectionRoad = self.straightRoadBuilder.createWithDifferentLanes(1, 10, n_lanes_left=2, n_lanes_right=2)
        roads.append(connectionRoad)
        roads.append(self.straightRoadBuilder.createWithDifferentLanes(2, 10, n_lanes_left=1, n_lanes_right=2))

        roads[0].addExtendedSuccessor(roads[1], 0, pyodrx.ContactPoint.start)

        roads[1].addExtendedPredecessor(roads[0], 0, pyodrx.ContactPoint.end)
        roads[1].addExtendedSuccessor(roads[2], 0, pyodrx.ContactPoint.start)

        roads[2].addExtendedPredecessor(roads[1], 0, pyodrx.ContactPoint.end)

        self.laneBuilder.createLanesForConnectionRoad(connectionRoad, roads[0], roads[2])

        
        odrName = "test_DifferentLaneConfigurations"
        odr = extensions.createOdrByPredecessor(odrName, roads, [])
        
        extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))

        xmlPath = f"output/test_DifferentLaneConfigurations.xodr"
        odr.write_xml(xmlPath)


    def test_addMedianIslandsToAllSections(self):
        roads = []
        roads.append(self.straightRoadBuilder.createWithDifferentLanes(0, 10, n_lanes_left=1, n_lanes_right=1))
        self.laneBuilder.addMedianIslandsToAllSections(roads[0], self.configuration.get('default_lane_width'))
        odrName = "test_DifferentLaneConfigurations"
        odr = extensions.createOdrByPredecessor(odrName, roads, [])
        
        extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))

        xmlPath = f"output/test_addMedianIslandsToAllSections.xodr"
        odr.write_xml(xmlPath)


    def test_addMedianIslandsTo3Sections(self):

        road = self.straightRoadBuilder.create(1, n_lanes_left=1, n_lanes_right=1, length=20, force3Section=False)

        try:
            self.laneBuilder.addMedianIslandsTo2Of3Sections(road, 20, skipEndpoint=pyodrx.ContactPoint.start, width=3)
            assert False
        except:
            assert True

        road = self.straightRoadBuilder.create(1, n_lanes_left=1, n_lanes_right=1, length=20, force3Section=True)
        self.laneBuilder.addMedianIslandsTo2Of3Sections(road, 20, skipEndpoint=pyodrx.ContactPoint.start, width=3)

        assert len(road.lanes.lanesections[0].leftlanes) == 1
        assert len(road.lanes.lanesections[0].rightlanes) == 1
        assert len(road.lanes.lanesections[1].leftlanes) == 2
        assert len(road.lanes.lanesections[1].rightlanes) == 2
        assert len(road.lanes.lanesections[2].leftlanes) == 2
        assert len(road.lanes.lanesections[2].rightlanes) == 2

        road = self.straightRoadBuilder.create(1, n_lanes_left=1, n_lanes_right=1, length=20, force3Section=True)
        self.laneBuilder.addMedianIslandsTo2Of3Sections(road, 20, skipEndpoint=pyodrx.ContactPoint.end, width=3)

        assert len(road.lanes.lanesections[0].leftlanes) == 2
        assert len(road.lanes.lanesections[0].rightlanes) == 2
        assert len(road.lanes.lanesections[1].leftlanes) == 2
        assert len(road.lanes.lanesections[1].rightlanes) == 2
        assert len(road.lanes.lanesections[2].leftlanes) == 1
        assert len(road.lanes.lanesections[2].rightlanes) == 1

        odrName = "test_DifferentLaneConfigurations"
        odr = extensions.createOdrByPredecessor(odrName, [road], [])
        
        extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))

        xmlPath = f"output/test_addMedianIslandsTo3Sections.xodr"
        odr.write_xml(xmlPath)
        




    
        
