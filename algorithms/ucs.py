from heapq import heappush, heappop

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
    pq = [(0, start_state)]
    parent = {start_state: None}
    cost = {start_state: 0}
    visited_count = 0

    while pq:
        visited_count += 1
        g, current_state = heappop(pq)
        if current_state == goal_state:
            return reconstruct_path(current_state, parent), visited_count
        for next_state in get_neighbors(current_state):
            new_cost = g + 1
            if next_state not in cost or new_cost < cost[next_state]:
                cost[next_state] = new_cost
                parent[next_state] = current_state
                heappush(pq, (new_cost, next_state))
    return None, visited_count