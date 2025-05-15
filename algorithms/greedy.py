from heapq import heappush, heappop

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

def reconstruct_path(state, parent):
    path = []
    while state is not None:
        path.append(state)
        state = parent[state]
    path.reverse()
    return path

def solve(start_state, goal_state):
    pq = [(manhattan_distance(start_state, goal_state), start_state)]
    parent = {start_state: None}
    visited = {start_state}
    visited_count = 0

    while pq:
        visited_count += 1
        h, current_state = heappop(pq)
        if current_state == goal_state:
            return reconstruct_path(current_state, parent), visited_count
        for next_state in get_neighbors(current_state):
            if next_state not in visited:
                visited.add(next_state)
                parent[next_state] = current_state
                heappush(pq, (manhattan_distance(next_state, goal_state), next_state))
    return None, visited_count