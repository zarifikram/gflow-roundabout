import unittest

import numpy as np
import os, dill
import pyodrx 

from junctions.JunctionHarvester import JunctionHarvester
from library.Configuration import Configuration


class test_JunctionHarvester(unittest.TestCase):
    
    def setUp(self):
        
        self.configuration = Configuration()
        self.esminiPath = self.configuration.get("esminipath")
        self.harvester = JunctionHarvester(outputDir="./output", outputPrefix="harvest-", lastId=0, esminiPath=self.esminiPath)
    

    def test_harvestByPainting2L(self):

        self.harvester.harvestByPainting2L(maxNumberOfRoadsPerJunction=4, triesPerRoadCount=3, show=True)