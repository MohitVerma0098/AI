INF = float('inf')

# Leaf values (as given in the diagram)
leaves = {
    'H': [41, 5],
    'I': [12, 90],
    'J': [101, 80],
    'K': [20, 30],
    'L': [34, 80],
    'M': [36, 35],
    'N': [50, 36],
    'O': [25, 3]
}

# Tree structure from diagram
tree = {
    'A': ['B', 'C'],
    'B': ['D', 'E'],
    'C': ['F', 'G'],
    'D': ['H', 'I'],
    'E': ['J', 'K'],
    'F': ['L', 'M'],
    'G': ['N', 'O']
}

# Node types
MAX = {'A', 'D', 'E', 'F', 'G'}
MIN = {'B', 'C', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O'}

pruned = []   # store pruned nodes


def alphabeta(node, alpha, beta):
    # If leaf node bottom layer
    if node in leaves:
        return min(leaves[node])     # all leaves are MIN nodes

    # MAX node
    if node in MAX:
        value = -INF
        for child in tree[node]:
            child_value = alphabeta(child, alpha, beta)
            value = max(value, child_value)
            alpha = max(alpha, value)

            # PRUNE for MAX
            if alpha >= beta:
                pruned.extend(tree[node][tree[node].index(child)+1:])
                break
        return value

    # MIN node
    else:
        value = INF
        for child in tree[node]:
            child_value = alphabeta(child, alpha, beta)
            value = min(value, child_value)
            beta = min(beta, value)

            # PRUNE for MIN
            if beta <= alpha:
                pruned.extend(tree[node][tree[node].index(child)+1:])
                break
        return value


# Run alpha-beta
root_value = alphabeta('A', -INF, INF)

print("Root Value =", root_value)
print("Pruned Nodes =", pruned)
