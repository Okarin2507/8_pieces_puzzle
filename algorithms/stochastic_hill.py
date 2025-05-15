import random

def manhattan_distance(state, goal_state):
    total = 0
    for i in range(9):
        if state[i] != 9:
            curr_row, curr_col = divmod(i, 3)
            goal_pos = goal_state.index(state[i])
            goal_row, goal_col = divmod(goal_pos, 3)
            total += abs(curr_row - goal_row) + abs(curr_col - goal_col)
    return total

def get_neighbors(state):
    neighbors = []
    s = list(state)
    blank_index = s.index(9)
    row, col = divmod(blank_index, 3)
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    for dr, dc in moves:
        new_row = row + dr
        new_col = col + dc
        if 0 <= new_row < 3 and 0 <= new_col < 3:
            new_index = new_row * 3 + new_col
            new_s = s[:]
            new_s[blank_index], new_s[new_index] = new_s[new_index], new_s[blank_index]
            neighbors.append(tuple(new_s))
    return neighbors

def is_solvable(state, goal_state):
    state_list = [num for num in state if num != 9]
    goal_list = [num for num in goal_state if num != 9]
    state_inversions = sum(1 for i in range(len(state_list)) for j in range(i + 1, len(state_list)) if state_list[i] > state_list[j])
    goal_inversions = sum(1 for i in range(len(goal_list)) for j in range(i + 1, len(goal_list)) if goal_list[i] > goal_list[j])
    return state_inversions % 2 == goal_inversions % 2


def solve(start_state, goal_state, max_iterations=5000, max_restarts=20):
    if not is_solvable(start_state, goal_state):
        return None, 0
        
    best_path_overall = None
    best_score_overall = float('inf')
    total_visited_nodes = 0

    for _ in range(max_restarts):
        current_state = start_state
        current_path = [current_state]
        current_score = manhattan_distance(current_state, goal_state)
        
        local_visited_in_restart = {current_state} # Avoid cycles in current restart
        restart_nodes_count = 1

        for i in range(max_iterations):
            if current_state == goal_state:
                if current_score < best_score_overall:
                    best_score_overall = current_score
                    best_path_overall = current_path
                total_visited_nodes += restart_nodes_count
                return best_path_overall, total_visited_nodes # Found solution

            neighbors = get_neighbors(current_state)
            uphill_neighbors = []
            
            # Consider unvisited neighbors for uphill moves
            for neighbor in neighbors:
                if neighbor not in local_visited_in_restart:
                    neighbor_score = manhattan_distance(neighbor, goal_state)
                    if neighbor_score < current_score:
                        uphill_neighbors.append(neighbor)
            
            if uphill_neighbors:
                next_state = random.choice(uphill_neighbors)
            else:
                # No uphill move, try a random unvisited neighbor to escape local optima
                unvisited_random = [n for n in neighbors if n not in local_visited_in_restart]
                if unvisited_random:
                    next_state = random.choice(unvisited_random)
                else: # No unvisited neighbors at all, stuck for this restart
                    break 
            
            current_state = next_state
            current_score = manhattan_distance(current_state, goal_state)
            current_path.append(current_state)
            local_visited_in_restart.add(current_state)
            restart_nodes_count +=1

        # After one restart's iterations, check if it's better than overall best
        if current_score < best_score_overall : # Even if not goal, update if path to a better state is found
            best_score_overall = current_score
            best_path_overall = current_path
        total_visited_nodes += restart_nodes_count


    if best_path_overall and best_path_overall[-1] == goal_state:
        return best_path_overall, total_visited_nodes
    return None, total_visited_nodes # No solution found after all restarts