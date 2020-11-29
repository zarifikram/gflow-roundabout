import pyodrx
import junctions
import extensions
from pyodrx.exceptions import NotSameAmountOfLanesError


class LaneLinker:


    def createLaneLinks(self, road1,road2):
        """ create_lane_links takes to roads and if they are connected, match their lanes 
            and creates lane links. 
            NOTE: now only works for roads/connecting roads with the same amount of lanes

            Parameters
            ----------
                road1 (Road): first road to be lane linked

                road2 (Road): second road to be lane linked
        """
        if self.bothNormalRoads(road1, road2):
            #both are roads
            if self.are_roads_consecutive(road1, road2): 
                self._create_links_roads(road1,road2)
            elif self.are_roads_consecutive(road2, road1): 
                self._create_links_roads(road2,road1)

        elif road1.road_type != -1:
            self._create_links_connecting_road(road1,road2)
        elif road2.road_type != -1:
            self._create_links_connecting_road(road2,road1)

    def bothNormalRoads(self, road1, road2):
        return road1.road_type == -1 and road2.road_type == -1


    def are_roads_consecutive(self, road1, road2): 

        if road1.successor is not None and road2.predecessor is not None: 
            if road1.successor.element_type == pyodrx.ElementType.road and road2.predecessor.element_type == pyodrx.ElementType.road:
                if road1.successor.element_id == road2.id and road2.predecessor.element_id == road1.id: 
                    return True 

        return False

        
    def _create_links_connecting_road(self, connecting, road):
        """ _create_links_connecting_road will create lane links between a connecting road and a normal road

            Parameters
            ----------
                connecting (Road): a road of type connecting road (not -1)

                road (Road): a that connects to the connecting road

        """
        linktype, sign, connecting_lanesec =  self._get_related_lanesection(connecting,road)
        _, _, road_lanesection_id =  self._get_related_lanesection(road,connecting) 

        if connecting_lanesec != None:
            laneSectionForConnection = connecting.lanes.lanesections[connecting_lanesec]
            laneSectionForRoad = road.lanes.lanesections[road_lanesection_id]
            if laneSectionForConnection.leftlanes:
                # do left lanes
                if len(laneSectionForConnection.leftlanes) == len(laneSectionForRoad.leftlanes):
                    for i in range(len(laneSectionForRoad.leftlanes)):
                        linkid = laneSectionForRoad.leftlanes[i].lane_id*sign
                        laneSectionForConnection.leftlanes[i].add_link(linktype,linkid)
                else:
                    raise NotSameAmountOfLanesError('Connecting road ',connecting.id, ' and road ', road.id, 'do not have the same number of left lanes.')
            if laneSectionForConnection.rightlanes:
                # do right lanes
                if len(laneSectionForConnection.rightlanes) == len(laneSectionForRoad.rightlanes):
                    for i in range(len(laneSectionForRoad.rightlanes)):
                        linkid = laneSectionForRoad.rightlanes[i].lane_id*sign
                        laneSectionForConnection.rightlanes[i].add_link(linktype,linkid)
                else:
                    raise NotSameAmountOfLanesError('Connecting road ',connecting.id, ' and road ', road.id, 'do not have the same number of right lanes.')


    def _get_related_lanesection(self, road,connected_road):
        """ _get_related_lanesection takes to roads, and gives the correct lane section to use
            the type of link and if the sign of lanes should be switched

            This function is very poorly written.

            Parameters
            ----------
                road (Road): the road that you want the information about

                connected_road (Road): the connected road

            Returns
            -------
                linktype (str): the linktype of road to connected road (successor or predecessor)

                sign (int): +1 or -1 depending on if the sign should change in the linking

                road_lanesection_id (int): what lanesection in the road that should be used to link
        """
        linktype = None
        sign = None
        road_lanesection_id = None
    
        if road.successor and road.successor.element_id == connected_road.id:
            linktype = 'successor'
            if road.successor.contact_point == pyodrx.ContactPoint.start:
                sign = 1
            else:
                sign = -1
            road_lanesection_id = -1

            # TODO return here?

        elif road.predecessor and road.predecessor.element_id == connected_road.id:
            linktype = 'predecessor'
            if road.predecessor.contact_point == pyodrx.ContactPoint.start:
                sign = -1
            else:
                sign = 1
            road_lanesection_id = 0
            # TODO return here?

        if connected_road.road_type != -1:
            # treat connecting road in junction differently ? Why is it different?
            sign, road_lanesection_id = self.getRelatedLaneSectionGivenSecondIsAConnection(road, connected_road, road_lanesection_id, sign)
        return linktype, sign, road_lanesection_id


    def getRelatedLaneSectionGivenSecondIsAConnection(self, road, connected_road, road_lanesection_id, sign):
        if connected_road.predecessor.element_id == road.id:
            if connected_road.predecessor.link_type == pyodrx.ContactPoint.start: # TODO wtf is link type here.
                road_lanesection_id = -1
                sign = -1
            else:
                road_lanesection_id = 0
                sign = 1
        elif connected_road.successor.element_id == road.id:
            if connected_road.predecessor.link_type == pyodrx.ContactPoint.start: # TODO wtf is link type here.
                road_lanesection_id = 0
                sign = 1
            else:
                road_lanesection_id = -1
                sign = -1
        return sign, road_lanesection_id

    
    def _create_links_roads(self, pre_road,suc_road):
        """ _create_links_roads takes two roads and connect the lanes with links, if they have the same amount. 

            Parameters
            ----------
                pre_road (Road): the predecessor road 

                suc_road (Road): the successor road

        """
        pre_linktype, pre_sign, pre_connecting_lanesec =  self._get_related_lanesection(pre_road,suc_road)
        suc_linktype, _, suc_connecting_lanesec =  self._get_related_lanesection(suc_road,pre_road)
        preLaneSection = pre_road.lanes.lanesections[pre_connecting_lanesec]
        # TODO it may be wrong. shouldn't it be suc_connecting_lanesec
        # sucLaneSection = suc_road.lanes.lanesections[-1] 
        sucLaneSection = suc_road.lanes.lanesections[suc_connecting_lanesec] 


        if len(preLaneSection.leftlanes) == len(sucLaneSection.leftlanes):
            for i in range(len(preLaneSection.leftlanes)):
                linkid = preLaneSection.leftlanes[i].lane_id*pre_sign
                preLaneSection.leftlanes[i].add_link(pre_linktype,linkid)
                

                suc_road.lanes.lanesections[suc_connecting_lanesec].leftlanes[i].add_link(suc_linktype,linkid*pre_sign)
        else:
            raise NotSameAmountOfLanesError('Road ' + str(pre_road.id) + ' and road ' + str(suc_road.id) + ' does not have the same number of right lanes.')


        if len(preLaneSection.rightlanes) == len(sucLaneSection.rightlanes):
            for i in range(len(preLaneSection.rightlanes)):
                linkid = preLaneSection.rightlanes[i].lane_id
                preLaneSection.rightlanes[i].add_link(pre_linktype,linkid)
                suc_road.lanes.lanesections[suc_connecting_lanesec].rightlanes[i].add_link(suc_linktype,linkid)
        else:
            raise NotSameAmountOfLanesError('Road ' + str(pre_road.id) + ' and road ' + str(suc_road.id) + ' does not have the same number of right lanes.')


