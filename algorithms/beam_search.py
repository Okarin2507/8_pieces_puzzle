import heapq
from copy import deepcopy

def solve(start, goal, beam_width=5):
    """
    Giải 8-Puzzle sử dụng thuật toán Beam Search.

    Args:
        start (tuple): Trạng thái ban đầu của puzzle.
        goal (tuple): Trạng thái đích của puzzle.
        beam_width (int): Độ rộng của beam (số lượng trạng thái tốt nhất được giữ lại).

    Returns:
        list: Danh sách các trạng thái từ trạng thái ban đầu đến trạng thái đích (nếu tìm thấy),
              hoặc None nếu không tìm thấy giải pháp.
    """

    def get_neighbors(state):
        """Tìm các trạng thái kế cận của một trạng thái."""
        empty_index = state.index(9)
        row, col = empty_index // 3, empty_index % 3
        neighbors = []

        moves = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for dr, dc in moves:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < 3 and 0 <= new_col < 3:
                new_index = new_row * 3 + new_col
                new_state = list(state)
                new_state[empty_index], new_state[new_index] = new_state[new_index], new_state[empty_index]
                neighbors.append(tuple(new_state))
        return neighbors

    def heuristic(state):
        """Tính heuristic (Manhattan distance) từ trạng thái hiện tại đến trạng thái đích."""
        distance = 0
        for i in range(9):
            if state[i] != 9:
                goal_index = goal.index(state[i])
                row1, col1 = i // 3, i % 3
                row2, col2 = goal_index // 3, goal_index % 3
                distance += abs(row1 - row2) + abs(col1 - col2)
        return distance

    beam = [(heuristic(start), start, [start])]
    visited = {start}

    while beam:
        new_beam = []
        for h, state, path in beam:
            if state == goal:
                return path

            neighbors = get_neighbors(state)
            for neighbor in neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)
                    new_path = path + [neighbor]
                    new_h = heuristic(neighbor)
                    heapq.heappush(new_beam, (new_h, neighbor, new_path))
        beam = heapq.nsmallest(beam_width, new_beam)
    return None