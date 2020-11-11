import unittest, os
from junctions.RoadBuilder import RoadBuilder
from scipy.interpolate import CubicHermiteSpline
from junctions.JunctionHarvester import JunctionHarvester
import numpy as np
import pyodrx, extensions
from junctions.JunctionBuilder import JunctionBuilder
from library.Configuration import Configuration

class test_RoadBuilder(unittest.TestCase):

    def setUp(self):
        
        self.configuration = Configuration()

        self.roadBuilder = RoadBuilder()
        self.junctionBuilder = JunctionBuilder()
        outputDir= os.path.join(os.getcwd(), 'output')
        lastId = 0
        self.harvester = JunctionHarvester(outputDir=outputDir, 
                                        outputPrefix='test_', 
                                        lastId=lastId,
                                        minAngle = np.pi / 30, 
                                        maxAngle = np.pi)



    def test_ParamPoly(self):
        tangentX = np.array([
            3.09016992482654, -10.0
        ])

        t = np.array([0, 1])
        x = np.array([44.30602949438151, 40.0])
        y = np.array([-5.223206854241455, 0.0])
        hermiteX = CubicHermiteSpline(t, x, tangentX)

        tangentY = np.array([
        9.51056516909997, 1.2246467991473533e-15
        ])
        hermiteY = CubicHermiteSpline(t, y, tangentY)
        xCoeffs = hermiteX.c.flatten()
        yCoeffs = hermiteY.c.flatten()

        # scipy coefficient and open drive coefficents have opposite order.
        myRoad = self.roadBuilder.createParamPoly3(
                                                0, 
                                                isJunction=False,
                                                au=xCoeffs[3],
                                                bu=xCoeffs[2],
                                                cu=xCoeffs[1],
                                                du=xCoeffs[0],
                                                av=yCoeffs[3],
                                                bv=yCoeffs[2],
                                                cv=yCoeffs[1],
                                                dv=yCoeffs[0]

                                            )

        odr = pyodrx.OpenDrive("test")
        odr.add_road(myRoad)
        odr.adjust_roads_and_lanes()

        extensions.printRoadPositions(odr)

        extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))


    def test_getConnectionRoadBetween(self):
        # test scenario for connection road
        
        roads = []
        roads.append(pyodrx.create_straight_road(0, 10))
        roads.append(self.roadBuilder.createSimpleCurve(1, np.pi/1.5, True, curvature = 0.9))
        roads.append(pyodrx.create_straight_road(2, 10))
        roads.append(self.roadBuilder.createSimpleCurve(3, np.pi/1.5, True, curvature = 0.9))
        roads.append(pyodrx.create_straight_road(4, 10))

        roads[0].add_successor(pyodrx.ElementType.junction,1)

        roads[1].add_predecessor(pyodrx.ElementType.road,0,pyodrx.ContactPoint.end)
        roads[1].add_successor(pyodrx.ElementType.road,2,pyodrx.ContactPoint.start)

        roads[2].add_predecessor(pyodrx.ElementType.junction,1)
        roads[2].add_successor(pyodrx.ElementType.junction,3)

        roads[3].add_predecessor(pyodrx.ElementType.road,2,pyodrx.ContactPoint.start)
        roads[3].add_successor(pyodrx.ElementType.road,4,pyodrx.ContactPoint.start)

        roads[4].add_predecessor(pyodrx.ElementType.junction,3)

        junction = self.junctionBuilder.createJunctionForASeriesOfRoads(roads)
        
        odrName = "test_connectionRoad"
        odr = extensions.createOdr(odrName, roads, [junction])

        lastConnection = self.harvester.createLastConnectionForLastAndFirstRoad(5, roads, junction)
        odr.add_road(lastConnection)

        # odr.reset()
        # odr.add_road(lastConnection)
        # odr.adjust_roads_and_lanes()

        odr.resetAndReadjust()
        
        

        # pyodrx.prettyprint(odr.get_element())

        extensions.printRoadPositions(odr)

        extensions.view_road(odr,os.path.join('..', self.configuration.get("esminipath")))
        pass