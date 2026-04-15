import traci

def get_edge_distance(edge_id):
    """Returns the physical length of an edge."""
    try:
        return traci.lane.getLength(edge_id + "_0")
    except traci.exceptions.TraCIException:
        return 1.0 # Fallback safety

def get_successors(edge_id):
    """Gets outgoing edges from the current edge using lane links."""
    successors = set()
    try:
        # Check the first lane of the edge for outgoing connections
        links = traci.lane.getLinks(edge_id + "_0")
        for link in links:
            next_lane = link[0] # The connected lane ID (e.g., 'top1_0')
            next_edge = next_lane.rsplit('_', 1)[0] # Strip the '_0' to get the edge ID
            
            if not next_edge.startswith(":"): # Ignore internal intersection edges
                successors.add(next_edge)
    except traci.exceptions.TraCIException:
        pass
    
    return list(successors)

def get_edge_traffic_data(edge_id):
    """Fetches real-time density and waiting time."""
    try:
        density = traci.edge.getLastStepVehicleNumber(edge_id)
        wait_time = traci.edge.getWaitingTime(edge_id)
        return density, wait_time
    except traci.exceptions.TraCIException:
        return 0, 0