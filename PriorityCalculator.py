from Node import Node
from OP import OP

def calculatePriorities(nodes, roots, leaves):
    # Dictionary to store the latency calculated for each node
    latency_cache = {}

    # Iterative DFS function with memoization to update latencies
    def iterative_dfs(starting_nodes):
        stack = []
        for node in starting_nodes:
            stack.append((node, 0))  # Tuple of node and its current latency

        while stack:
            node, current_latency = stack.pop()
            if node in latency_cache and current_latency <= latency_cache[node]:
                continue
            latency_cache[node] = current_latency
            node.latency = current_latency

            for child in node.getChildren():
                edge_latency = node.getEdgeLatency(child)
                stack.append((child, node.latency + edge_latency))

    iterative_dfs(roots)

    # Dictionary to store the number of descendants calculated for each node
    descendants_cache = {}

    # Iterative function with memoization to count descendants
    def iterative_count_descendants(nodes):
        for node in nodes:
            stack = [node]
            while stack:
                current = stack[-1]
                if current in descendants_cache:
                    stack.pop()
                    continue

                children = current.getChildren()
                if not children or all(child in descendants_cache for child in children):
                    # Count this node and all its descendants
                    count = 1  # Count the node itself
                    for child in children:
                        count += descendants_cache[child]
                    descendants_cache[current] = count - 1  # Subtract 1 to exclude the node itself
                    stack.pop()
                else:
                    stack.extend(children)

    iterative_count_descendants(nodes)

    for node in nodes:
        node.priority = 10 * node.latency + descendants_cache[node]

    sorted_nodes = sorted(nodes, key=lambda x: x.priority, reverse=True)
    sorted_roots = sorted(roots, key=lambda x: x.priority, reverse=True)
    sorted_leaves = sorted(leaves, key=lambda x: x.priority, reverse=True)

    return sorted_nodes, sorted_roots, sorted_leaves

# from Node import Node
# from OP import OP


# def calculatePriorities(nodes, roots, leaves):
#     # Max latency for each node
#     latency_cache = {}

#     # Function to recursively update latencies with memoization
#     def dfs(node, current_latency):
#         if node in latency_cache and current_latency <= latency_cache[node]:
#             return
#         latency_cache[node] = current_latency
#         node.latency = current_latency

#         for child in node.getChildren():
#             edge_latency = node.getEdgeLatency(child)
#             dfs(child, node.latency + edge_latency)

#     for root in roots:
#         dfs(root, 0)

#     # Dictionary to store the number of descendants calculated for each node
#     descendants_cache = {}

#     # After DFS, calculate the number of descendants for each node with memoization
#     def count_descendants(node):
#         if node in descendants_cache:
#             return descendants_cache[node]
#         count = 1  # Count the node itself
#         for child in node.getChildren():
#             count += count_descendants(child)
#         descendants_cache[node] = count - 1  # Subtract 1 to exclude the node itself
#         return descendants_cache[node]

#     for node in nodes:
#         node.priority = 10 * node.latency + count_descendants(node)

#     sorted_nodes = sorted(nodes, key=lambda x: x.priority, reverse=True)
#     sorted_roots = sorted(roots, key=lambda x: x.priority, reverse=True)
#     sorted_leaves = sorted(leaves, key=lambda x: x.priority, reverse=True)

#     return sorted_nodes, sorted_roots, sorted_leaves
