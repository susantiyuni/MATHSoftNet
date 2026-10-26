import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import seaborn as sns

if G.number_of_nodes() > 0 and G.number_of_edges() > 0:

    # Select the 250 highest-degree software nodes
    top_nodes = (
        degrees.sort_values(ascending=False)
        .head(min(250, len(degrees)))
        .index.tolist()
    )

    H = G.subgraph(top_nodes).copy()

    # Map software nodes to detected communities
    community_map = (
        community_assignments
        .set_index("software_id")["community_id"]
        .astype(str)
        .to_dict()
    )

    node_communities = {
        node: community_map.get(node, "Unassigned")
        for node in H.nodes()
    }

    # Sort community labels for reproducible color assignment
    unique_communities = sorted(set(node_communities.values()))

    # Colorblind-friendly categorical palette
    palette = sns.color_palette("colorblind", n_colors=max(
        len(unique_communities), 1
    ))

    community_colors = dict(zip(unique_communities, palette))

    node_colors = [
        community_colors[node_communities[node]]
        for node in H.nodes()
    ]

    pos = nx.spring_layout(
    H,
    seed=42,
    iterations=200,
    k=0.8 / np.sqrt(max(H.number_of_nodes(), 1)),
    weight=None,
    )
    
    # Expand node positions to use more of the canvas
    pos_array = np.array(list(pos.values()))
    xmin, ymin = pos_array.min(axis=0)
    xmax, ymax = pos_array.max(axis=0)
    
    center = np.array([(xmin + xmax) / 2, (ymin + ymax) / 2])
    scale = max(xmax - xmin, ymax - ymin)
    
    if scale > 0:
        pos = {
            node: (coord - center) / scale
            for node, coord in pos.items()
        }
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    nx.draw_networkx_edges(
        H, pos, ax=ax,
        edge_color="#8A8A8A",
        alpha=0.22,
        width=0.45,
    )
    
    nx.draw_networkx_nodes(
        H, pos, ax=ax,
        node_size=24,
        node_color=node_colors,
        edgecolors="white",
        linewidths=0.25,
        alpha=0.95,
    )
    
    ax.set_axis_off()
    ax.set_aspect("equal")
    ax.margins(0.01)
    
    # Remove excess whitespace around the axes
    fig.subplots_adjust(left=0, right=0.5, bottom=0, top=0.5)
    
    save_figure(fig, "network_high_degree_subgraph_2.pdf")
    
    fig.savefig(
        "network_high_degree_subgraph_2.png",
        dpi=600,
        bbox_inches="tight",
        pad_inches=0.02,
        facecolor="white",
    )
    
    plt.show()
    plt.close(fig)
