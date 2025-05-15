import random
import math
from typing import List, Tuple, Optional, Set, Dict

State = Tuple[int, ...]

def manhattan_distance(state: State, goal_state: State) -> int:
    total = 0
    try:
        size = int(len(state)**0.5)
        if size * size != len(state) or len(goal_state) != len(state): return float('inf')
        blank_tile = size * size
        goal_map = {tile: i for i, tile in enumerate(goal_state)}
    except (ValueError, TypeError): return float('inf')

    for i in range(len(state)):
        tile = state[i]
        if tile != blank_tile:
            curr_row, curr_col = divmod(i, size)
            goal_pos = goal_map.get(tile)
            if goal_pos is None: return float('inf')
            goal_row, goal_col = divmod(goal_pos, size)
            total += abs(curr_row - goal_row) + abs(curr_col - goal_col)
    return total

# --- Dán hàm get_neighbors_with_double_moves vào đây ---
def get_neighbors_with_double_moves(state: State) -> List[State]:
    neighbors: Set[State] = set(); s_list = list(state)
    try:
        size = int(len(state)**0.5);
        if size * size != len(state): return []
        blank_tile = size * size; blank_index = s_list.index(blank_tile)
    except (ValueError, TypeError): return []
    row, col = divmod(blank_index, size); moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    single_move_intermediates: List[Tuple[State, int]] = []
    for dr, dc in moves:
        new_row, new_col = row + dr, col + dc
        if 0 <= new_row < size and 0 <= new_col < size:
            new_index = new_row * size + new_col; new_s = s_list[:]; new_s[blank_index], new_s[new_index] = new_s[new_index], new_s[blank_index]
            neighbor_state = tuple(new_s); neighbors.add(neighbor_state); single_move_intermediates.append((neighbor_state, new_index))
    for intermediate_state, intermediate_blank_index in single_move_intermediates:
        s_intermediate = list(intermediate_state); row1, col1 = divmod(intermediate_blank_index, size)
        for dr, dc in moves:
            new_row2, new_col2 = row1 + dr, col1 + dc
            if 0 <= new_row2 < size and 0 <= new_col2 < size:
                new_index2 = new_row2 * size + new_col2
                if new_index2 == blank_index: continue
                new_s2 = s_intermediate[:]; new_s2[intermediate_blank_index], new_s2[new_index2] = new_s2[new_index2], new_s2[intermediate_blank_index]
                neighbor2_state = tuple(new_s2); neighbors.add(neighbor2_state)
    return list(neighbors)

def solve(start_state: State, goal_state: State, initial_temperature=100.0, cooling_rate=0.005, min_temperature=0.1, max_iterations=50000) -> Optional[List[State]]:
    """
    Giải 8-Puzzle bằng Simulated Annealing với di chuyển kép.

    Args:
        start_state (tuple): Trạng thái bắt đầu.
        goal_state (tuple): Trạng thái đích.
        initial_temperature (float): Nhiệt độ ban đầu.
        cooling_rate (float): Tốc độ làm mát (giảm nhiệt độ).
        min_temperature (float): Nhiệt độ dừng tối thiểu.
        max_iterations (int): Số lần lặp tối đa.

    Returns:
        list: Danh sách các trạng thái trên đường đi (có thể không tối ưu) nếu tìm thấy đích,
              hoặc None nếu không.
    """
    start_state = tuple(start_state)
    goal_state = tuple(goal_state)

    current_state = start_state
    current_heuristic = manhattan_distance(current_state, goal_state)

    if current_heuristic == float('inf'):
        print("SA (Double): Lỗi tính heuristic ban đầu.")
        return None
    if current_heuristic == 0:
        return [start_state]

    best_state = current_state
    best_heuristic = current_heuristic
    path = [current_state]

    temperature = initial_temperature
    iterations = 0

    while temperature > min_temperature and iterations < max_iterations:
        iterations += 1

        if current_state == goal_state:
            return path

        neighbors = get_neighbors_with_double_moves(current_state)
        if not neighbors:
             break

        next_state = random.choice(neighbors)
        next_heuristic = manhattan_distance(next_state, goal_state)

        if next_heuristic == float('inf'):
            continue

        delta_e = next_heuristic - current_heuristic

        if delta_e < 0 or random.random() < math.exp(-delta_e / temperature):
            current_state = next_state
            current_heuristic = next_heuristic
            path.append(current_state)

            if current_heuristic < best_heuristic:
                best_state = current_state
                best_heuristic = current_heuristic

        temperature *= (1 - cooling_rate)

    if best_state == goal_state:
         if current_state == goal_state:
              return path
         else:
              return None
    else:
        return None