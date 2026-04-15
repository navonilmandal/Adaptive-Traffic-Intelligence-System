import traci

class Perception:
    def __init__(self, agent_id):
        self.agent_id = agent_id

    def get_current_edge(self):
        return traci.vehicle.getRoadID(self.agent_id)

    def get_lane_info(self):
        """Returns current lane, total lanes, and lane index."""
        current_lane_id = traci.vehicle.getLaneID(self.agent_id)
        lane_index = traci.vehicle.getLaneIndex(self.agent_id)
        edge_id = self.get_current_edge()
        if not edge_id or edge_id.startswith(":"): # Inside an intersection
            return lane_index, 1
        total_lanes = traci.edge.getLaneNumber(edge_id)
        return lane_index, total_lanes

    def detect_leader(self, threshold=30.0):
        """Detects vehicle ahead within distance threshold."""
        leader = traci.vehicle.getLeader(self.agent_id, threshold)
        if leader:
            veh_id, distance = leader
            v_class = traci.vehicle.getVehicleClass(veh_id)
            return veh_id, distance, v_class
        return None

    def get_edge_density(self):
        """Measures congestion on the current edge."""
        edge = self.get_current_edge()
        if edge and not edge.startswith(":"):
            return traci.edge.getLastStepVehicleNumber(edge)
        return 0