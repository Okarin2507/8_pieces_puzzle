import heapq
from typing import List, Tuple, Optional, Set, Dict

State = Tuple[int, ...]

def manhattan_distance(state: State, goal_state: State) -> int:
    """
    Tính tổng khoảng cách Manhattan cho tất cả các ô (trừ ô trống)
    đến vị trí mục tiêu của chúng. (Heuristic)
    """
    total = 0
    try:
        size = int(len(state)**0.5)
        if size * size != len(state) or len(goal_state) != len(state):
             return float('inf')
        blank_tile = size * size
    except TypeError:
        return float('inf')

    goal_map = {tile: i for i, tile in enumerate(goal_state)}

    for i in range(len(state)):
        tile = state[i]
        if tile != blank_tile:
            current_row, current_col = divmod(i, size)
            goal_pos = goal_map.get(tile)
            if goal_pos is None:
                return float('inf')
            goal_row, goal_col = divmod(goal_pos, size)
            total += abs(current_row - goal_row) + abs(current_col - goal_col)
    return total

def get_neighbors_with_double_moves(state: State) -> List[State]:
    """
    Tạo ra các trạng thái hàng xóm có thể có, bao gồm cả di chuyển đơn và kép.
    Không trả về chi phí, chỉ trả về danh sách các trạng thái.
    """
    neighbors: List[State] = []
    s_list = list(state)
    try:
        size = int(len(state)**0.5)
        if size * size != len(state):
             return []
        blank_tile = size * size
        blank_index = s_list.index(blank_tile)
    except (ValueError, TypeError):
        return []

    row, col = divmod(blank_index, size)
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    single_move_intermediates: List[Tuple[State, int]] = []
    for dr, dc in moves:
        new_row, new_col = row + dr, col + dc
        if 0 <= new_row < size and 0 <= new_col < size:
            new_index = new_row * size + new_col
            new_s = s_list[:]
            new_s[blank_index], new_s[new_index] = new_s[new_index], new_s[blank_index]
            neighbor_state = tuple(new_s)
            neighbors.append(neighbor_state)
            single_move_intermediates.append((neighbor_state, new_index))

    for intermediate_state, intermediate_blank_index in single_move_intermediates:
        s_intermediate = list(intermediate_state)
        row1, col1 = divmod(intermediate_blank_index, size)
        for dr, dc in moves:
            new_row2, new_col2 = row1 + dr, col1 + dc
            if 0 <= new_row2 < size and 0 <= new_col2 < size:
                new_index2 = new_row2 * size + new_col2
                if new_index2 == blank_index:
                    continue

                new_s2 = s_intermediate[:]
                new_s2[intermediate_blank_index], new_s2[new_index2] = new_s2[new_index2], new_s2[intermediate_blank_index]
                neighbor2_state = tuple(new_s2)
                neighbors.append(neighbor2_state)
    return neighbors

def solve(start_state: State, goal_state: State, beam_width: int = 10) -> Optional[List[State]]:
    """
    Giải 8-Puzzle sử dụng thuật toán Beam Search với di chuyển kép.

    Args:
        start_state (tuple): Trạng thái ban đầu của puzzle.
        goal_state (tuple): Trạng thái đích của puzzle.
        beam_width (int): Độ rộng của beam (số lượng trạng thái tốt nhất được giữ lại).

    Returns:
        list: Danh sách các trạng thái (tuples) từ trạng thái ban đầu đến trạng thái đích
              (nếu tìm thấy), hoặc None nếu không tìm thấy giải pháp.
              Lưu ý: Đường đi có thể không tối ưu về số bước tuyệt đối do bản chất của Beam Search.
    """
    start_state = tuple(start_state)
    goal_state = tuple(goal_state)

    start_h = manhattan_distance(start_state, goal_state)
    if start_h == float('inf'):
        print("Lỗi: Trạng thái bắt đầu hoặc kết thúc không hợp lệ.")
        return None

    beam: List[Tuple[int, State, List[State]]] = [(start_h, start_state, [start_state])]
    visited: Set[State] = {start_state}

    max_depth = 100
    depth = 0

    while beam and depth < max_depth:
        depth += 1
        new_beam_candidates: List[Tuple[int, State, List[State]]] = []

        for h_current, current_state, current_path in beam:
            if current_state == goal_state:
                print(f"Tìm thấy giải pháp ở độ sâu {len(current_path) - 1} (số hành động)")
                return current_path

            neighbors = get_neighbors_with_double_moves(current_state)

            for neighbor in neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)
                    neighbor_h = manhattan_distance(neighbor, goal_state)
                    if neighbor_h != float('inf'):
                        new_path = current_path + [neighbor]
                        heapq.heappush(new_beam_candidates, (neighbor_h, neighbor, new_path))
        beam = heapq.nsmallest(beam_width, new_beam_candidates)

        if not beam:
             break

    print("Không tìm thấy giải pháp trong giới hạn độ sâu hoặc beam bị trống.")
    return None