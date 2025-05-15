from collections import deque
from typing import List, Tuple, Optional, Set, Dict

State = Tuple[int, ...]

def get_neighbors_with_double_moves(state: State) -> List[State]:
    """
    Tạo ra các trạng thái hàng xóm có thể có, bao gồm cả di chuyển đơn và kép.
    Trả về danh sách các trạng thái duy nhất.
    """
    neighbors: Set[State] = set()
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
            neighbors.add(neighbor_state)
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
                neighbors.add(neighbor2_state)
    return list(neighbors)

def reconstruct_path(state: State, parent: Dict[State, Optional[State]]) -> List[State]:
    """
    Xây dựng lại đường đi từ trạng thái đích ngược về trạng thái bắt đầu.
    """
    path: List[State] = []
    current: Optional[State] = state
    while current is not None:
        path.append(current)
        current = parent.get(current)
    path.reverse()
    return path

def solve(start_state: State, goal_state: State) -> Optional[List[State]]:
    """
    Tìm kiếm theo chiều rộng (BFS) với khả năng di chuyển kép.
    Tìm đường đi có số lượng hành động (di chuyển đơn hoặc kép) ít nhất.

    Args:
        start_state (tuple): Trạng thái bắt đầu.
        goal_state (tuple): Trạng thái đích.

    Returns:
        list: Đường đi (list các tuple trạng thái) nếu tìm thấy, None nếu không.
    """
    start_state = tuple(start_state)
    goal_state = tuple(goal_state)

    if start_state == goal_state:
        return [start_state]

    queue: deque[State] = deque([start_state])
    visited: Set[State] = {start_state}
    parent: Dict[State, Optional[State]] = {start_state: None}

    while queue:
        current_state = queue.popleft()

        for next_state in get_neighbors_with_double_moves(current_state):
            if next_state not in visited:
                visited.add(next_state)
                parent[next_state] = current_state
                queue.append(next_state)

                if next_state == goal_state:
                    return reconstruct_path(goal_state, parent)
    return None