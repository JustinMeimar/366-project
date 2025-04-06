import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D  # Fixed import
from typing import Dict  # Added import for type hint
from allocator import InterferenceGraph  # Changed from main to allocator

def num_to_hex_color(num: int):
    if num == -1:
        return "#ffffff" # white (spilled)

    hex_colors = [
        "#FF0000",  # red
        "#00FF00",  # green
        "#0000FF",  # blue
        "#FFFF00",  # yellow
        "#FF00FF",  # magenta
        "#00FFFF",  # cyan
        "#FFA500",  # orange
        "#800080",  # purple
        "#008000",  # dark green
        "#000080",  # navy
        "#8B4513",  # brown
        "#FF6347",  # tomato
        "#4682B4",  # steel blue
        "#32CD32"   # lime green
    ]
    return hex_colors[num % len(hex_colors)]

def visualize_interference_graph(graph: InterferenceGraph,
                                 colors: Dict[str, int],
                                 save_path: str):
    """
    Pass in the interference graph, and the chosen coloring by
    the algorithm.
    """
    G = nx.Graph()
    print("vars: ", graph.variables)
    for var in graph.variables:
        G.add_node(var)
    
    for i in range(graph.size):
        for j in range(i+1, graph.size):
            if graph.adj_matrix[i][j] == 1:
                G.add_edge(graph.variables[i], graph.variables[j])
    
    plt.figure(figsize=(10, 8))
    layout = nx.spring_layout(G, seed=42) # seed for reproducibility
    if colors:
        node_colors = [num_to_hex_color(colors.get(var, 0)) for var in G.nodes()] 
        cmap = plt.cm.get_cmap('tab10') 
        nx.draw_networkx_nodes(G, layout,
                               node_color=node_colors,
                               node_size=700)
    else:
        nx.draw_networkx_nodes(G, layout, node_color='lightblue', node_size=700)
    
    nx.draw_networkx_edges(G, layout, width=1.5, alpha=0.7)
    nx.draw_networkx_labels(G, layout, font_weight='bold')
    unique_colors = sorted(set(colors.values()))
    cmap = plt.cm.get_cmap('tab10') 
    color_legend = [Line2D([0], [0],
                marker='o',
                color='w', 
                markerfacecolor=num_to_hex_color(color),
                markersize=10,
                label=f'Register {color}' if color != -1 else f'Spilled: {color}'
               ) for color in unique_colors]
   

    plt.legend(handles=color_legend, loc='upper right') 
    plt.title("Register Interference Graph")
    plt.axis('off') 
    plt.tight_layout()
    plt.savefig(save_path, bbox_inches='tight', dpi=300)
    plt.close()  
    
    print(f"Graph Statistics:")
    print(f"Number of variables: {graph.size}")
    print(f"Number of interference edges: {sum(sum(row) for row in graph.adj_matrix) // 2}")
    
    if colors:
        print(f"Number of registers used: {len(set(colors.values()))}")
        max_degree = max(graph.get_degree(var) for var in graph.variables)
        print(f"Maximum degree: {max_degree}")

