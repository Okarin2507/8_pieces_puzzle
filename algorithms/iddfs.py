def get_neighbors(state):
    neighbors = []
    s = list(state)
    blank_index = s.index(9)
    row, col = divmod(blank_index, 3)
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    for dr, dc in moves:
        new_row, new_col = row + dr, col + dc
        if 0 <= new_row < 3 and 0 <= new_col < 3:
            new_index = new_row * 3 + new_col
            new_s = s[:]
            new_s[blank_index], new_s[new_index] = new_s[new_index], new_s[blank_index]
            neighbors.append(tuple(new_s))
    return neighbors

def reconstruct_path(state, parent):
    path = []
    while state is not None:
        path.append(state)
        state = parent[state]
    path.reverse()
    return path

def depth_limited_search(start_state, goal_state, depth_limit, visited_count):
    stack = [(start_state, [start_state])]
    visited_in_dls = {start_state: 0} # Store depth for path reconstruction

    while stack:
        visited_count[0] +=1
        current_state, path = stack.pop()
        current_path_depth = len(path) - 1

        if current_state == goal_state:
            return path, visited_count

        if current_path_depth >= depth_limit:
            continue

        for next_state in reversed(get_neighbors(current_state)): # Reverse for more natural DFS order
            new_path_depth = current_path_depth + 1
            # Pruning: if already visited at a shallower or equal depth in this DLS call
            if next_state in visited_in_dls and visited_in_dls[next_state] <= new_path_depth:
                continue
            
            visited_in_dls[next_state] = new_path_depth
            stack.append((next_state, path + [next_state]))
            
    return None, visited_count


def solve(start_state, goal_state, max_depth=30): # Max depth for 8-puzzle usually around 30
    visited_count_total = [0] # Use a list to pass by reference

    for depth in range(max_depth + 1):
        # print(f"IDDFS: Trying depth {depth}")
        path, visited_count_total = depth_limited_search(start_state, goal_state, depth, visited_count_total)
        if path:
            # print(f"IDDFS: Solution found at depth {depth}")
            return path, visited_count_total[0]
            
    # print(f"IDDFS: No solution found within max depth {max_depth}")
    return None, visited_count_total[0]