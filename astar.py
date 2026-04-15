import heapq
from utils import get_successors, get_edge_distance

def astar_search(start_edge, goal_edge, weight_func):
    """
    Standard A* search algorithm.
    weight_func: function(edge_id) -> float (Returns dynamic cost of edge)
    """
    open_set = []
    heapq.heappush(open_set, (0, start_edge))
    came_from = {}
    g_score = {start_edge: 0}
    
    while open_set:
        current_cost, current_edge = heapq.heappop(open_set)

        if current_edge == goal_edge:
            return reconstruct_path(came_from, current_edge)

        for neighbor in get_successors(current_edge):
            # Dynamic cost calculation (Distance + Traffic factors)
            edge_cost = get_edge_distance(neighbor) * weight_func(neighbor)
            tentative_g = g_score[current_edge] + edge_cost

            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current_edge
                g_score[neighbor] = tentative_g
                # Heuristic is simply 0 here (Dijkstra mode) since we lack static XY coordinates, 
                # but dynamic edge weights act as the A* heuristic modification.
                f_score = tentative_g 
                heapq.heappush(open_set, (f_score, neighbor))

    return None # No path found

def reconstruct_path(came_from, current):
    """Builds the path list from A* data."""
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path