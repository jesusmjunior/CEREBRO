import sqlite3
import os
from datetime import datetime

# Define the database file path
# The database will be created in the same directory as this script, inside the 'db' folder.
# Ensure the 'db' directory exists before running.
DB_DIR = os.path.dirname(__file__)
DATABASE_PATH = os.path.join(DB_DIR, 'cerebro_jesus.db')

def create_connection(db_path=DATABASE_PATH):
    """Create a database connection to the SQLite database specified by db_path."""
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row # Allows accessing columns by name
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None

def initialize_database():
    """Create tables if they do not exist."""
    # Ensure the directory exists
    os.makedirs(DB_DIR, exist_ok=True)

    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()

            # Projects table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL UNIQUE,
                    description TEXT,
                    category TEXT, -- e.g., 'creative', 'business', 'analytical'
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
            """)

            # Artifacts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS artifacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    description TEXT,
                    scope TEXT,
                    main_artifacts_ref TEXT, -- Can store JSON or text references
                    task_list TEXT, -- Can store JSON or text list of tasks
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
                );
            """)

            # Tags table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE
                );
            """)

            # Artifact-Tag Many-to-Many table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS artifact_tags (
                    artifact_id INTEGER NOT NULL,
                    tag_id INTEGER NOT NULL,
                    PRIMARY KEY (artifact_id, tag_id),
                    FOREIGN KEY (artifact_id) REFERENCES artifacts (id) ON DELETE CASCADE,
                    FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE
                );
            """)

            # Relationships/Synapses table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS relationships (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    artifact_id_1 INTEGER NOT NULL,
                    artifact_id_2 INTEGER NOT NULL,
                    relationship_type TEXT, -- e.g., 'synapse', 'tree_branch', 'related'
                    fuzzy_score REAL, -- Score from fuzzy logic
                    description TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (artifact_id_1) REFERENCES artifacts (id) ON DELETE CASCADE,
                    FOREIGN KEY (artifact_id_2) REFERENCES artifacts (id) ON DELETE CASCADE,
                    -- Ensure relationships are unique regardless of artifact order
                    UNIQUE (artifact_id_1, artifact_id_2)
                );
            """)

            conn.commit()
            print("Database initialized successfully.")

        except sqlite3.Error as e:
            print(f"Database initialization error: {e}")
        finally:
            conn.close()
    else:
        print("Error! Cannot create the database connection.")

# --- CRUD Operations ---

# --- Projects ---

def create_project(title, description="", category=""):
    """Create a new project."""
    conn = create_connection()
    if conn:
        sql = """
            INSERT INTO projects (title, description, category, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """
        now = datetime.now().isoformat()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (title, description, category, now, now))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            print(f"Error: Project with title '{title}' already exists.")
            return None
        except sqlite3.Error as e:
            print(f"Error creating project: {e}")
            return None
        finally:
            conn.close()
    return None

def get_project(project_id):
    """Get a project by its ID."""
    conn = create_connection()
    if conn:
        sql = "SELECT * FROM projects WHERE id = ?"
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (project_id,))
            return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Error getting project: {e}")
            return None
        finally:
            conn.close()
    return None

def get_all_projects():
    """Get all projects."""
    conn = create_connection()
    if conn:
        sql = "SELECT * FROM projects ORDER BY updated_at DESC"
        try:
            cursor = conn.cursor()
            cursor.execute(sql)
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting all projects: {e}")
            return []
        finally:
            conn.close()
    return []

def update_project(project_id, title=None, description=None, category=None):
    """Update an existing project."""
    conn = create_connection()
    if conn:
        updates = []
        params = []
        if title is not None:
            updates.append("title = ?")
            params.append(title)
        if description is not None:
            updates.append("description = ?")
            params.append(description)
        if category is not None:
            updates.append("category = ?")
            params.append(category)

        if not updates:
            return False # Nothing to update

        updates.append("updated_at = ?")
        params.append(datetime.now().isoformat())
        params.append(project_id)

        sql = f"UPDATE projects SET {', '.join(updates)} WHERE id = ?"

        try:
            cursor = conn.cursor()
            cursor.execute(sql, tuple(params))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.IntegrityError:
            print(f"Error: Project with title '{title}' already exists.")
            return False
        except sqlite3.Error as e:
            print(f"Error updating project: {e}")
            return False
        finally:
            conn.close()
    return False

def delete_project(project_id):
    """Delete a project by its ID. Related artifacts, tags, and relationships will be deleted due to CASCADE."""
    conn = create_connection()
    if conn:
        sql = "DELETE FROM projects WHERE id = ?"
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (project_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error deleting project: {e}")
            return False
        finally:
            conn.close()
    return False

# --- Artifacts ---

def create_artifact(project_id, description="", scope="", main_artifacts_ref="", task_list=""):
    """Create a new artifact for a project."""
    conn = create_connection()
    if conn:
        sql = """
            INSERT INTO artifacts (project_id, description, scope, main_artifacts_ref, task_list, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        now = datetime.now().isoformat()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (project_id, description, scope, main_artifacts_ref, task_list, now, now))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error creating artifact: {e}")
            return None
        finally:
            conn.close()
    return None

def get_artifact(artifact_id):
    """Get an artifact by its ID."""
    conn = create_connection()
    if conn:
        sql = "SELECT * FROM artifacts WHERE id = ?"
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (artifact_id,))
            return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Error getting artifact: {e}")
            return None
        finally:
            conn.close()
    return None

def get_artifacts_by_project(project_id):
    """Get all artifacts belonging to a project."""
    conn = create_connection()
    if conn:
        sql = "SELECT * FROM artifacts WHERE project_id = ? ORDER BY created_at ASC"
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (project_id,))
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting artifacts for project {project_id}: {e}")
            return []
        finally:
            conn.close()
    return []

def update_artifact(artifact_id, description=None, scope=None, main_artifacts_ref=None, task_list=None):
    """Update an existing artifact."""
    conn = create_connection()
    if conn:
        updates = []
        params = []
        if description is not None:
            updates.append("description = ?")
            params.append(description)
        if scope is not None:
            updates.append("scope = ?")
            params.append(scope)
        if main_artifacts_ref is not None:
            updates.append("main_artifacts_ref = ?")
            params.append(main_artifacts_ref)
        if task_list is not None:
            updates.append("task_list = ?")
            params.append(task_list)

        if not updates:
            return False # Nothing to update

        updates.append("updated_at = ?")
        params.append(datetime.now().isoformat())
        params.append(artifact_id)

        sql = f"UPDATE artifacts SET {', '.join(updates)} WHERE id = ?"

        try:
            cursor = conn.cursor()
            cursor.execute(sql, tuple(params))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error updating artifact: {e}")
            return False
        finally:
            conn.close()
    return False

def delete_artifact(artifact_id):
    """Delete an artifact by its ID. Related tags and relationships will be deleted due to CASCADE."""
    conn = create_connection()
    if conn:
        sql = "DELETE FROM artifacts WHERE id = ?"
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (artifact_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error deleting artifact: {e}")
            return False
        finally:
            conn.close()
    return False

# --- Tags ---

def create_tag(name):
    """Create a new tag."""
    conn = create_connection()
    if conn:
        sql = "INSERT INTO tags (name) VALUES (?)"
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (name,))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            # Tag already exists, return its ID
            return get_tag_by_name(name)['id']
        except sqlite3.Error as e:
            print(f"Error creating tag: {e}")
            return None
        finally:
            conn.close()
    return None

def get_tag(tag_id):
    """Get a tag by its ID."""
    conn = create_connection()
    if conn:
        sql = "SELECT * FROM tags WHERE id = ?"
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (tag_id,))
            return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Error getting tag: {e}")
            return None
        finally:
            conn.close()
    return None

def get_tag_by_name(name):
    """Get a tag by its name."""
    conn = create_connection()
    if conn:
        sql = "SELECT * FROM tags WHERE name = ?"
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (name,))
            return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Error getting tag by name: {e}")
            return None
        finally:
            conn.close()
    return None


def get_all_tags():
    """Get all tags."""
    conn = create_connection()
    if conn:
        sql = "SELECT * FROM tags ORDER BY name ASC"
        try:
            cursor = conn.cursor()
            cursor.execute(sql)
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting all tags: {e}")
            return []
        finally:
            conn.close()
    return []

def delete_tag(tag_id):
    """Delete a tag by its ID. Related artifact_tags entries will be deleted due to CASCADE."""
    conn = create_connection()
    if conn:
        sql = "DELETE FROM tags WHERE id = ?"
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (tag_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error deleting tag: {e}")
            return False
        finally:
            conn.close()
    return False

# --- Artifact-Tag Relationships ---

def add_tag_to_artifact(artifact_id, tag_id):
    """Link a tag to an artifact."""
    conn = create_connection()
    if conn:
        sql = "INSERT OR IGNORE INTO artifact_tags (artifact_id, tag_id) VALUES (?, ?)"
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (artifact_id, tag_id))
            conn.commit()
            return cursor.rowcount > 0 # Returns 1 if inserted, 0 if ignored
        except sqlite3.Error as e:
            print(f"Error adding tag {tag_id} to artifact {artifact_id}: {e}")
            return False
        finally:
            conn.close()
    return False

def remove_tag_from_artifact(artifact_id, tag_id):
    """Remove a link between a tag and an artifact."""
    conn = create_connection()
    if conn:
        sql = "DELETE FROM artifact_tags WHERE artifact_id = ? AND tag_id = ?"
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (artifact_id, tag_id))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error removing tag {tag_id} from artifact {artifact_id}: {e}")
            return False
        finally:
            conn.close()
    return False

def get_tags_for_artifact(artifact_id):
    """Get all tags associated with an artifact."""
    conn = create_connection()
    if conn:
        sql = """
            SELECT t.* FROM tags t
            JOIN artifact_tags at ON t.id = at.tag_id
            WHERE at.artifact_id = ?
            ORDER BY t.name ASC
        """
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (artifact_id,))
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting tags for artifact {artifact_id}: {e}")
            return []
        finally:
            conn.close()
    return []

def get_artifacts_with_tag(tag_id):
    """Get all artifacts associated with a tag."""
    conn = create_connection()
    if conn:
        sql = """
            SELECT a.* FROM artifacts a
            JOIN artifact_tags at ON a.id = at.artifact_id
            WHERE at.tag_id = ?
            ORDER BY a.created_at DESC
        """
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (tag_id,))
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting artifacts with tag {tag_id}: {e}")
            return []
        finally:
            conn.close()
    return []


# --- Relationships (Synapses/Tree Branches) ---

def create_relationship(artifact_id_1, artifact_id_2, relationship_type="synapse", fuzzy_score=0.0, description=""):
    """Create a relationship between two artifacts."""
    # Ensure artifact_id_1 is always less than artifact_id_2 for the UNIQUE constraint
    if artifact_id_1 > artifact_id_2:
        artifact_id_1, artifact_id_2 = artifact_id_2, artifact_id_1

    conn = create_connection()
    if conn:
        sql = """
            INSERT OR IGNORE INTO relationships (artifact_id_1, artifact_id_2, relationship_type, fuzzy_score, description, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        now = datetime.now().isoformat()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (artifact_id_1, artifact_id_2, relationship_type, fuzzy_score, description, now))
            conn.commit()
            return cursor.lastrowid if cursor.rowcount > 0 else None # Return ID if inserted, None if ignored
        except sqlite3.Error as e:
            print(f"Error creating relationship between {artifact_id_1} and {artifact_id_2}: {e}")
            return None
        finally:
            conn.close()
    return None

def get_relationships_for_artifact(artifact_id):
    """Get all relationships involving a specific artifact."""
    conn = create_connection()
    if conn:
        sql = """
            SELECT * FROM relationships
            WHERE artifact_id_1 = ? OR artifact_id_2 = ?
            ORDER BY created_at DESC
        """
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (artifact_id, artifact_id))
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting relationships for artifact {artifact_id}: {e}")
            return []
        finally:
            conn.close()
    return []

def get_all_relationships():
    """Get all relationships in the database."""
    conn = create_connection()
    if conn:
        sql = "SELECT * FROM relationships ORDER BY created_at DESC"
        try:
            cursor = conn.cursor()
            cursor.execute(sql)
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting all relationships: {e}")
            return []
        finally:
            conn.close()
    return []


def delete_relationship(relationship_id):
    """Delete a relationship by its ID."""
    conn = create_connection()
    if conn:
        sql = "DELETE FROM relationships WHERE id = ?"
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (relationship_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error deleting relationship {relationship_id}: {e}")
            return False
        finally:
            conn.close()
    return False

# Example usage (for testing purposes, can be removed or commented out)
if __name__ == '__main__':
    print("Initializing database...")
    initialize_database()

    # Example CRUD operations
    print("\nCreating a project...")
    project_id = create_project("My First Project", "This is a test project.", "creative")
    if project_id:
        print(f"Project created with ID: {project_id}")

        print("\nGetting the project...")
        project = get_project(project_id)
        print(project)

        print("\nUpdating the project...")
        update_project(project_id, description="Updated description for the test project.")
        project = get_project(project_id)
        print(project)

        print("\nCreating artifacts for the project...")
        artifact1_id = create_artifact(project_id, "Initial Idea", "Brainstorming phase", "Sketch 1", "- Task A\n- Task B")
        artifact2_id = create_artifact(project_id, "Prototype Design", "Design phase", "Figma Link", "- Task C")
        if artifact1_id and artifact2_id:
            print(f"Artifact 1 created with ID: {artifact1_id}")
            print(f"Artifact 2 created with ID: {artifact2_id}")

            print("\nGetting artifacts for the project...")
            artifacts = get_artifacts_by_project(project_id)
            for art in artifacts:
                print(art)

            print("\nCreating tags...")
            tag1_id = create_tag("Concept")
            tag2_id = create_tag("UI/UX")
            if tag1_id and tag2_id:
                print(f"Tag 'Concept' ID: {tag1_id}")
                print(f"Tag 'UI/UX' ID: {tag2_id}")

                print("\nAdding tags to artifacts...")
                add_tag_to_artifact(artifact1_id, tag1_id)
                add_tag_to_artifact(artifact2_id, tag1_id) # Both have Concept
                add_tag_to_artifact(artifact2_id, tag2_id) # Artifact 2 also has UI/UX

                print(f"Tags for Artifact {artifact1_id}:")
                print(get_tags_for_artifact(artifact1_id))
                print(f"Tags for Artifact {artifact2_id}:")
                print(get_tags_for_artifact(artifact2_id))

                print(f"\nArtifacts with tag '{get_tag(tag1_id)['name']}':")
                arts_with_tag1 = get_artifacts_with_tag(tag1_id)
                for art in arts_with_tag1:
                    print(art['description'])

                print("\nCreating a relationship...")
                rel_id = create_relationship(artifact1_id, artifact2_id, "synapse", 0.75, "Ideas are related")
                if rel_id:
                    print(f"Relationship created with ID: {rel_id}")

                    print(f"\nRelationships for Artifact {artifact1_id}:")
                    rels = get_relationships_for_artifact(artifact1_id)
                    for rel in rels:
                        print(rel)

                    print(f"\nDeleting relationship {rel_id}...")
                    if delete_relationship(rel_id):
                        print("Relationship deleted.")
                    print(f"Relationships for Artifact {artifact1_id} after deletion:")
                    print(get_relationships_for_artifact(artifact1_id))


            print(f"\nDeleting artifact {artifact1_id}...")
            if delete_artifact(artifact1_id):
                print("Artifact deleted.")
            print(f"Artifacts for project {project_id} after deletion:")
            for art in get_artifacts_by_project(project_id):
                 print(art)


        print(f"\nDeleting project {project_id}...")
        if delete_project(project_id):
            print("Project deleted.")
        print("\nAll projects after deletion:")
        print(get_all_projects())

    else:
        print("Failed to create initial project.")

    print("\nGetting all tags:")
    print(get_all_tags())

    # Clean up test tag if it wasn't linked to anything
    tag_to_delete = get_tag_by_name("Concept")
    if tag_to_delete:
         print(f"\nDeleting tag '{tag_to_delete['name']}'...")
         if delete_tag(tag_to_delete['id']):
             print("Tag deleted.")
         print("\nAll tags after deletion:")
         print(get_all_tags())
