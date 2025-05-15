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

def solve(start_state, goal_state, max_iterations=1000, max_restarts=10):
    if not is_solvable(start_state, goal_state):
        return None, 0
    best_path = None
    best_score = float('inf')
    total_visited = 0

    for _ in range(max_restarts):
        current_state = start_state
        current_path = [current_state]
        current_score = manhattan_distance(current_state, goal_state)
        visited_in_restart = {current_state}
        restart_visited_count = 1

        for i in range(max_iterations):
            if current_state == goal_state:
                if current_score < best_score:
                    best_score = current_score
                    best_path = current_path
                total_visited += restart_visited_count
                return best_path, total_visited
            
            neighbors = get_neighbors(current_state)
            best_next_state = None
            best_next_score = current_score
            
            unvisited_neighbors = [n for n in neighbors if n not in visited_in_restart]
            
            if not unvisited_neighbors: # No unvisited neighbors from this local state
                 if not neighbors: break # No neighbors at all
                 # Pick any neighbor if all are visited locally, to allow escaping very small loops
                 # This can lead to longer paths but helps escape strict local optima for simple HC
                 random_neighbor = random.choice(neighbors)
                 best_next_state = random_neighbor
                 best_next_score = manhattan_distance(random_neighbor, goal_state)

            else:
                for neighbor in unvisited_neighbors:
                    score = manhattan_distance(neighbor, goal_state)
                    if score < best_next_score:
                        best_next_score = score
                        best_next_state = neighbor
            
            if best_next_state is None or best_next_score >= current_score:
                break 
            
            current_state = best_next_state
            current_path.append(current_state)
            current_score = best_next_score
            visited_in_restart.add(current_state)
            restart_visited_count += 1

        if current_score < best_score:
            best_score = current_score
            best_path = current_path
        total_visited += restart_visited_count

    if best_path and best_path[-1] == goal_state:
        return best_path, total_visited
    return None, total_visited