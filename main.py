import sys
import traci
import time
import random
from decision import DecisionMaker

SUMO_CMD = ["sumo-gui", "-c", "config.sumocfg"]

def highlight_edge(edge_id, color, label):
    try:
        shape = traci.lane.getShape(edge_id + "_0")
        x, y = shape[len(shape) // 2]
        s = 15 
        box = [(x-s, y-s), (x+s, y-s), (x+s, y+s), (x-s, y+s)]
        traci.polygon.add(f"marker_{label}", box, color, fill=True, layer=100)
    except: pass

def get_edge_coords(edge_id):
    try: return traci.lane.getShape(edge_id + "_0")[0]
    except: return (0, 0)

def spawn_random_trip(valid_start_edges, all_edges):
    """Spawns traffic and tries multiple times to find a valid start/end."""
    print("Injecting initial background traffic...")
    spawned_bg = 0
    for _ in range(1000): 
        if spawned_bg >= 150: break 
        start = random.choice(valid_start_edges)
        end = random.choice(all_edges)
        v_type = "car_type" if random.random() < 0.8 else "bike_type"
        
        route = traci.simulation.findRoute(start, end, vType=v_type)
        if route and len(route.edges) > 0:
            route_id = f"bg_{spawned_bg}"
            traci.route.add(route_id, route.edges)
            traci.vehicle.add(f"veh_{spawned_bg}", route_id, typeID=v_type)
            spawned_bg += 1

    # Give it 10 chances to find a connected Start and Goal
    for _ in range(10):
        random.shuffle(valid_start_edges)
        start_edge = valid_start_edges[0]
        goal_edge = valid_start_edges[-1] 

        agent_route = traci.simulation.findRoute(start_edge, goal_edge, vType="agent_type")
        if agent_route and len(agent_route.edges) > 1:
            traci.route.add("agent_route", agent_route.edges)
            traci.vehicle.add("agent_1", "agent_route", typeID="agent_type", departSpeed="max")
            return start_edge, goal_edge 
            
    return None, None

def throw_obstacle_in_path(decision_maker, all_edges):
    """SABOTAGE: Forces a slow vehicle to spawn directly in front of the AI!"""
    try:
        route = decision_maker.current_route
        
        # --- FIX: Prevent NoneType Crash ---
        if not route: 
            return 
            
        curr_edge = decision_maker.perception.get_current_edge()
        
        if curr_edge in route:
            idx = route.index(curr_edge)
            # Pick a road 1 to 2 edges AHEAD of the agent
            if idx + 2 < len(route):
                target_edge = route[idx + random.randint(1, 2)]
                
                # Spawn a very slow bike to force an obstacle detection
                end_edge = random.choice(all_edges)
                obs_route = traci.simulation.findRoute(target_edge, end_edge, vType="bike_type")
                
                if obs_route and len(obs_route.edges) > 0:
                    veh_id = f"target_obs_{traci.simulation.getTime()}"
                    traci.route.add(f"r_{veh_id}", obs_route.edges)
                    traci.vehicle.add(veh_id, f"r_{veh_id}", typeID="bike_type", departSpeed="0")
    except: pass

def run_simulation():
    print("Starting SUMO Simulation...")
    traci.start(SUMO_CMD)
    
    try:
        traci.simulationStep()
        all_edges = [e for e in traci.edge.getIDList() if not e.startswith(":")]
        valid_start_edges = [e for e in all_edges if len(traci.lane.getLinks(e + "_0")) > 0]
        
        start_edge, goal_edge = spawn_random_trip(valid_start_edges, all_edges)
        if not goal_edge: raise Exception("Failed to find a valid route after 10 attempts.")

        highlight_edge(start_edge, (0, 255, 0, 255), "SOURCE")
        highlight_edge(goal_edge, (0, 150, 255, 255), "DESTINATION")

        agent_id = "agent_1"
        agent_active = False
        decision_maker = None
        
        simulation_running = True
        step = 0

        while simulation_running:
            
            # --- PROFESSOR SHOWCASE ---
            if goal_edge and agent_id in traci.vehicle.getIDList() and not agent_active:
                traci.gui.trackVehicle("View #0", agent_id)
                traci.gui.setZoom("View #0", 1200) 
                traci.vehicle.setSpeed(agent_id, 0.0) 
                
                decision_maker = DecisionMaker(agent_id, goal_edge)
                
                print("\n" + "="*60)
                
                print("RED PATH  : Shortest physical distance")
                print("CYAN PATH : Maximum traffic avoidance")
                print("="*60)
                
                m1, m2, final_pso_path = decision_maker.showcase_to_professor()
                traci.simulationStep() 
                time.sleep(3) 
                
                decision_maker.clear_markers(m1)
                decision_maker.clear_markers(m2)
                
                # --- FIX: Fallback if PSO fails to find a path ---
                if not final_pso_path:
                    final_pso_path = list(traci.vehicle.getRoute(agent_id))
                    print("PSO A* isolated. Falling back to default routing.")

                decision_maker.current_route = final_pso_path
                traci.vehicle.setRoute(agent_id, final_pso_path)
                decision_maker.draw_planned_route() 
                
                print("\n" + "="*60)
                print("SELECTING YELLOW PATH: PSO-Optimized Route")
                print("="*60 + "\n")
                
                traci.simulationStep() 
                time.sleep(2) 
                
                traci.vehicle.setSpeed(agent_id, -1) 
                agent_active = True

            # --- MAIN DRIVING LOGIC ---
            traci.simulationStep()
            
            if agent_active:
                
                # Sabotage: Every 30 steps, drop an obstacle
                if step % 30 == 0:
                    throw_obstacle_in_path(decision_maker, all_edges)

                if agent_id in traci.vehicle.getIDList():
                    decision_text, action_color = decision_maker.execute_driving_logic()
                    
                    if decision_text:
                        print("\n" + "="*60)
                        print(f"AI DECISION: {decision_text}")
                        print("="*60 + "\n")
                        
                        traci.vehicle.setColor(agent_id, action_color)
                        traci.simulationStep()
                        time.sleep(1.0) 
                        traci.vehicle.setColor(agent_id, (255, 0, 0)) 
                        
                        if "SUCCESS" in decision_text:
                            simulation_running = False
                            
                else:
                    simulation_running = False

            step += 1
            time.sleep(0.05) 

    except Exception as e:
        print(f"\nPYTHON CRASHED: {e}")
        time.sleep(5) 
    finally:
        print("\n SIMULATION COMPLETE. Shutting down gracefully...")
        try:
            traci.close()
        except Exception:
            pass # Ignore the final shutdown hiccup
        sys.stdout.flush()

if __name__ == "__main__":
    run_simulation()