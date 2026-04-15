import traci
from perception import Perception
from pso import PSO
from astar import astar_search
from utils import get_edge_traffic_data

class DecisionMaker:
    def __init__(self, agent_id, goal_edge):
        self.agent_id = agent_id
        self.goal_edge = goal_edge
        self.perception = Perception(agent_id)
        self.pso = PSO()
        self.current_route = []
        self.w1, self.w2 = 1.0, 1.0 
        self.last_reroute_time = -100 
        self.current_state = "NORMAL" 
        self.route_markers = [] 

    def draw_path(self, route, color, marker_prefix, size=8):
        markers = []
        if not route: return markers
        for i, edge in enumerate(route):
            try:
                shape = traci.lane.getShape(edge + "_0")
                x, y = shape[len(shape) // 2]
                box = [(x-size, y-size), (x+size, y-size), (x+size, y+size), (x-size, y+size)]
                marker_id = f"{marker_prefix}_{i}_{traci.simulation.getTime()}"
                traci.polygon.add(marker_id, box, color, fill=True, layer=100) 
                markers.append(marker_id)
            except: pass
        return markers

    def clear_markers(self, markers):
        for m in markers:
            try: traci.polygon.remove(m)
            except: pass
        markers.clear()

    def showcase_to_professor(self):
        start_edge = self.perception.get_current_edge()
        if start_edge.startswith(":") or start_edge == self.goal_edge:
            return [], [], []

        path_distance = astar_search(start_edge, self.goal_edge, lambda e: 1.0)
        path_traffic = astar_search(start_edge, self.goal_edge, lambda e: 1 + (get_edge_traffic_data(e)[0] * 10))
        
        sample_edges = traci.edge.getIDList()[:20] 
        self.w1, self.w2 = self.pso.optimize_weights(sample_edges)
        def dynamic_weight(edge):
            density, wait = get_edge_traffic_data(edge)
            return 1 + (density * self.w1) + (wait * self.w2)
        
        path_pso = astar_search(start_edge, self.goal_edge, dynamic_weight)

        m1 = self.draw_path(path_distance, (255, 0, 0, 180), "eval_red", 6)
        m2 = self.draw_path(path_traffic, (0, 255, 255, 180), "eval_cyan", 6)
        
        return m1, m2, path_pso

    def draw_planned_route(self):
        self.clear_markers(self.route_markers)
        self.route_markers = self.draw_path(self.current_route, (255, 255, 0, 180), f"route_{self.agent_id}", size=8)

    def generate_path(self):
        start_edge = self.perception.get_current_edge()
        if start_edge.startswith(":") or start_edge == self.goal_edge: return 
        
        sample_edges = traci.edge.getIDList()[:20] 
        self.w1, self.w2 = self.pso.optimize_weights(sample_edges)
        
        def dynamic_weight(edge):
            density, wait = get_edge_traffic_data(edge)
            return 1 + (density * self.w1) + (wait * self.w2)

        new_route = astar_search(start_edge, self.goal_edge, dynamic_weight)
        
        if new_route and new_route != self.current_route:
            self.current_route = new_route
            traci.vehicle.setRoute(self.agent_id, new_route)
            self.draw_planned_route() 

    def execute_driving_logic(self):
        try:
            current_edge = self.perception.get_current_edge()
            
            # ==============================================================
            # THE FIX: Wait until the car drives over the center of the road
            # ==============================================================
            if current_edge == self.goal_edge:
                # Get the total length of this street
                lane_len = traci.lane.getLength(current_edge + "_0")
                # Get exactly how far the car has driven down it
                car_pos = traci.vehicle.getLanePosition(self.agent_id)

                # The blue square is at the halfway mark. Only stop if car is past it!
                if car_pos >= (lane_len * 0.95):
                    return "SUCCESS! DESTINATION REACHED.", (0, 255, 0)
            # ==============================================================

            lane_idx, total_lanes = self.perception.get_lane_info()
            leader = self.perception.detect_leader(50.0) 
            density = self.perception.get_edge_density()
            current_time = traci.simulation.getTime()

            new_state = "NORMAL"
            decision_text = None
            action_color = None

            if density > 4 and (current_time - self.last_reroute_time > 10): 
                self.last_reroute_time = current_time
                self.generate_path()
                new_state = "REROUTE"
                decision_text = f"HIGH CONGESTION ({density} vehicles) -> Rerouting via PSO+A*"
                action_color = (255, 0, 255) 

            elif leader:
                veh_id, dist, v_class = leader
                if dist < 50.0: 
                    if total_lanes > 1:
                        target_lane = 1 if lane_idx == 0 else 0
                        traci.vehicle.changeLane(self.agent_id, target_lane, 2)
                        new_state = "LANE_CHANGE"
                        decision_text = f"OBSTACLE AHEAD ({dist:.1f}m) -> Changing Lane"
                        action_color = (0, 255, 255) 
                    else:
                        traci.vehicle.slowDown(self.agent_id, 3.0, 2)
                        new_state = "BRAKING"
                        decision_text = f"OBSTACLE AHEAD ({dist:.1f}m) -> Braking"
                        action_color = (255, 255, 0) 
                else:
                    traci.vehicle.setSpeed(self.agent_id, -1)
            else:
                traci.vehicle.setSpeed(self.agent_id, -1) 

            if new_state != self.current_state and new_state != "NORMAL":
                self.current_state = new_state
                return decision_text, action_color
            elif new_state == "NORMAL":
                self.current_state = "NORMAL"

            return None, None
        except traci.exceptions.TraCIException:
            return None, None