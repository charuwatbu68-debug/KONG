from collections import deque

def find_shortest_path(graph):
    start_node = 0
    end_node = 1

    # Queue เก็บ (node, path)
    queue = deque([(start_node, [start_node])])

    # Set เก็บ node ที่เคยไปแล้ว
    visited = set()
    visited.add(start_node)

    while queue:
        current_node, path = queue.popleft()

        # ถ้าถึงปลายทาง
        if current_node == end_node:
            return path

        # ดูเพื่อนบ้าน
        for neighbor in graph.get(current_node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                new_path = path + [neighbor]
                queue.append((neighbor, new_path))

    return []  # หาไม่เจอ
