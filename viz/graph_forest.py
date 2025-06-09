import networkx as nx
import matplotlib.pyplot as plt
import sqlite3
from db import database # Assuming db.database exists and has functions to fetch data
from models import data_models # Assuming data_models exists for data structures

# Define node colors and styles based on artifact type or other attributes
NODE_COLORS = {
    'Project': 'skyblue',
    'Artifact': 'lightgreen',
    'Tag': 'orange',
    'Relationship': 'red' # Maybe relationships aren't nodes, but types of edges
}

EDGE_COLORS = {
    'Parent-Child': 'gray',
    'Related': 'purple',
    'FuzzyLink': 'blue'
}

def fetch_graph_data(project_id=None):
    """
    Fetches artifact and relationship data from the database, optionally filtered by project.

    Args:
        project_id (int, optional): The ID of the project to filter by. Defaults to None (fetch all).

    Returns:
        tuple: A tuple containing two lists: artifacts and relationships.
    """
    conn = database.get_db_connection()
    cursor = conn.cursor()

    # Fetch artifacts
    if project_id:
        cursor.execute("SELECT id, title, type, description FROM artifacts WHERE project_id = ?", (project_id,))
    else:
        cursor.execute("SELECT id, title, type, description FROM artifacts")
    artifacts_data = cursor.fetchall()
    artifacts = [{'id': row[0], 'title': row[1], 'type': row[2], 'description': row[3]} for row in artifacts_data]

    # Fetch relationships
    # Assuming relationships table links artifact_id_source to artifact_id_target
    # and includes type and score.
    # Need to ensure relationships fetched are relevant to the selected project's artifacts
    if project_id:
        # Fetch relationships where both source and target artifacts belong to the project
        cursor.execute("""
            SELECT r.artifact_id_source, r.artifact_id_target, r.type, r.score
            FROM relationships r
            JOIN artifacts a_source ON r.artifact_id_source = a_source.id
            JOIN artifacts a_target ON r.artifact_id_target = a_target.id
            WHERE a_source.project_id = ? AND a_target.project_id = ?
        """, (project_id, project_id))
    else:
         cursor.execute("SELECT artifact_id_source, artifact_id_target, type, score FROM relationships")

    relationships_data = cursor.fetchall()
    relationships = [{'source': row[0], 'target': row[1], 'type': row[2], 'score': row[3]} for row in relationships_data]

    conn.close()
    return artifacts, relationships

def build_artifact_graph(artifacts, relationships):
    """
    Builds a NetworkX graph object from artifact and relationship data.

    Args:
        artifacts (list): List of artifact dictionaries.
        relationships (list): List of relationship dictionaries.

    Returns:
        nx.Graph: The NetworkX graph object.
    """
    G = nx.Graph() # Using a simple graph for now, could be DiGraph if relationships are directed

    # Add nodes
    for artifact in artifacts:
        G.add_node(artifact['id'],
                   title=artifact['title'],
                   type=artifact['type'],
                   description=artifact['description'],
                   color=NODE_COLORS.get(artifact['type'], 'lightgray')) # Assign color based on type

    # Add edges
    for rel in relationships:
        # Ensure both source and target nodes exist in the graph before adding edge
        if rel['source'] in G and rel['target'] in G:
             G.add_edge(rel['source'], rel['target'],
                       type=rel['type'],
                       score=rel['score'],
                       color=EDGE_COLORS.get(rel['type'], 'black')) # Assign color based on type
        else:
            # This might happen if fetching relationships globally but artifacts by project
            # Or if data integrity issues exist
            print(f"Warning: Skipping edge between {rel['source']} and {rel['target']} as one or both nodes not found.")


    return G

def draw_artifact_graph(G, layout='spring'):
    """
    Draws the NetworkX graph using Matplotlib.

    Args:
        G (nx.Graph): The NetworkX graph object.
        layout (str): The layout algorithm to use ('spring', 'circular', 'random', etc.).

    Returns:
        matplotlib.figure.Figure: The Matplotlib figure containing the graph.
    """
    if not G or G.number_of_nodes() == 0:
        print("Graph is empty, cannot draw.")
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, "No data to display graph.", horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
        ax.axis('off')
        return fig

    fig, ax = plt.subplots(figsize=(12, 8))

    # Define node positions based on layout
    if layout == 'spring':
        pos = nx.spring_layout(G, k=0.5, iterations=50) # k regulates distance between nodes
    elif layout == 'circular':
        pos = nx.circular_layout(G)
    elif layout == 'random':
        pos = nx.random_layout(G)
    else: # Default to spring
        pos = nx.spring_layout(G)

    # Get node and edge attributes for drawing
    node_colors = [G.nodes[node].get('color', 'lightgray') for node in G.nodes()]
    node_labels = {node: G.nodes[node].get('title', str(node)) for node in G.nodes()}
    edge_colors = [G.edges[edge].get('color', 'black') for edge in G.edges()]
    # edge_labels = {(u, v): G.edges[(u, v)].get('type', '') for u, v in G.edges()} # Optional: label edges

    # Draw nodes
    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=3000, node_color=node_colors, alpha=0.9)

    # Draw edges
    nx.draw_networkx_edges(G, pos, ax=ax, edge_color=edge_colors, width=2.0, alpha=0.7)

    # Draw labels
    nx.draw_networkx_labels(G, pos, ax=ax, labels=node_labels, font_size=10, font_weight='bold')

    # Optional: Draw edge labels
    # nx.draw_networkx_edge_labels(G, pos, ax=ax, edge_labels=edge_labels, font_color='red')

    ax.set_title("Artifact Relationship Graph")
    ax.axis('off') # Hide axes
    plt.tight_layout() # Adjust layout to prevent labels overlapping

    return fig

if __name__ == '__main__':
    # Example Usage (for testing purposes)
    # In a real Streamlit app, this would be called from app.py

    # --- Create a dummy database and data for demonstration ---
    # This part simulates fetching data; in the actual app,
    # db.database should handle connection and schema.
    try:
        conn = sqlite3.connect(':memory:') # Use in-memory DB for test
        cursor = conn.cursor()

        # Create dummy tables
        cursor.execute("""
            CREATE TABLE projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE artifacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                title TEXT NOT NULL,
                type TEXT, -- e.g., 'Project', 'Artifact', 'Task', 'Note'
                description TEXT,
                FOREIGN KEY (project_id) REFERENCES projects(id)
            )
        """)
        cursor.execute("""
            CREATE TABLE relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                artifact_id_source INTEGER,
                artifact_id_target INTEGER,
                type TEXT, -- e.g., 'Parent-Child', 'Related', 'FuzzyLink'
                score REAL, -- Fuzzy score or strength
                FOREIGN KEY (artifact_id_source) REFERENCES artifacts(id),
                FOREIGN KEY (artifact_id_target) REFERENCES artifacts(id)
            )
        """)
        conn.commit()

        # Insert dummy data
        cursor.execute("INSERT INTO projects (title, description) VALUES (?, ?)", ("Project Alpha", "A test project"))
        project_id = cursor.lastrowid

        cursor.execute("INSERT INTO artifacts (project_id, title, type, description) VALUES (?, ?, ?, ?)", (project_id, "Main Project Node", "Project", "The central node"))
        node_p = cursor.lastrowid
        cursor.execute("INSERT INTO artifacts (project_id, title, type, description) VALUES (?, ?, ?, ?)", (project_id, "Artifact 1", "Artifact", "First related artifact"))
        node_a1 = cursor.lastrowid
        cursor.execute("INSERT INTO artifacts (project_id, title, type, description) VALUES (?, ?, ?, ?)", (project_id, "Artifact 2", "Artifact", "Second related artifact"))
        node_a2 = cursor.lastrowid
        cursor.execute("INSERT INTO artifacts (project_id, title, type, description) VALUES (?, ?, ?, ?)", (project_id, "Artifact 3", "Artifact", "Another artifact"))
        node_a3 = cursor.lastrowid
         # Add an artifact not in this project to test filtering
        cursor.execute("INSERT INTO projects (title, description) VALUES (?, ?)", ("Project Beta", "Another project"))
        project_beta_id = cursor.lastrowid
        cursor.execute("INSERT INTO artifacts (project_id, title, type, description) VALUES (?, ?, ?, ?)", (project_beta_id, "Artifact Beta", "Artifact", "From another project"))
        node_beta = cursor.lastrowid


        cursor.execute("INSERT INTO relationships (artifact_id_source, artifact_id_target, type, score) VALUES (?, ?, ?, ?)", (node_p, node_a1, "Parent-Child", 1.0))
        cursor.execute("INSERT INTO relationships (artifact_id_source, artifact_id_target, type, score) VALUES (?, ?, ?, ?)", (node_p, node_a2, "Parent-Child", 1.0))
        cursor.execute("INSERT INTO relationships (artifact_id_source, artifact_id_target, type, score) VALUES (?, ?, ?, ?)", (node_a1, node_a2, "Related", 0.8))
        cursor.execute("INSERT INTO relationships (artifact_id_source, artifact_id_target, type, score) VALUES (?, ?, ?, ?)", (node_a1, node_a3, "FuzzyLink", 0.6))
         # Add a relationship involving the artifact from another project (should be filtered out)
        cursor.execute("INSERT INTO relationships (artifact_id_source, artifact_id_target, type, score) VALUES (?, ?, ?, ?)", (node_a1, node_beta, "Related", 0.5))

        conn.commit()

        # Replace the actual fetch_graph_data with a mock for this test
        def mock_fetch_graph_data(project_id=None):
             cursor.execute("SELECT id, title, type, description FROM artifacts WHERE project_id = ?", (project_id,))
             artifacts_data = cursor.fetchall()
             artifacts = [{'id': row[0], 'title': row[1], 'type': row[2], 'description': row[3]} for row in artifacts_data]

             cursor.execute("""
                SELECT r.artifact_id_source, r.artifact_id_target, r.type, r.score
                FROM relationships r
                JOIN artifacts a_source ON r.artifact_id_source = a_source.id
                JOIN artifacts a_target ON r.artifact_id_target = a_target.id
                WHERE a_source.project_id = ? AND a_target.project_id = ?
            """, (project_id, project_id))
             relationships_data = cursor.fetchall()
             relationships = [{'source': row[0], 'target': row[1], 'type': row[2], 'score': row[3]} for row in relationships_data]
             return artifacts, relationships

        # --- End of dummy data setup ---

        # Use the mock function to get data for Project Alpha
        artifacts_alpha, relationships_alpha = mock_fetch_graph_data(project_id)

        # Build the graph
        G_alpha = build_artifact_graph(artifacts_alpha, relationships_alpha)

        # Draw the graph
        fig_alpha = draw_artifact_graph(G_alpha)

        # Display the graph (in a real app, Streamlit would handle this)
        plt.show()

        # Example of fetching data for Project Beta (should be empty graph)
        artifacts_beta, relationships_beta = mock_fetch_graph_data(project_beta_id)
        G_beta = build_artifact_graph(artifacts_beta, relationships_beta)
        fig_beta = draw_artifact_graph(G_beta)
        plt.show()


    except Exception as e:
        print(f"An error occurred during test setup or execution: {e}")
    finally:
        # Clean up dummy database connection
        if 'conn' in locals() and conn:
            conn.close()
