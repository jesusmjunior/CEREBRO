import sqlite3
from db import database
# Assuming models/data_models.py defines data structures if needed,
# but for simple tag management, direct DB interaction might suffice.
# from models import data_models

def create_tag(name: str, description: str = None):
    """Creates a new tag in the database."""
    conn = database.get_db_connection()
    try:
        conn.execute("INSERT INTO tags (name, description) VALUES (?, ?)", (name, description))
        conn.commit()
        print(f"Tag '{name}' created successfully.")
        return conn.lastrowid
    except sqlite3.IntegrityError:
        print(f"Tag '{name}' already exists.")
        return None # Or return existing tag ID if needed
    except Exception as e:
        print(f"Error creating tag '{name}': {e}")
        return None
    finally:
        conn.close()

def get_tag_by_id(tag_id: int):
    """Retrieves a tag by its ID."""
    conn = database.get_db_connection()
    try:
        tag_data = conn.execute("SELECT id, name, description FROM tags WHERE id = ?", (tag_id,)).fetchone()
        if tag_data:
            # return data_models.Tag(*tag_data) # If using data models
            return {'id': tag_data[0], 'name': tag_data[1], 'description': tag_data[2]}
        return None
    except Exception as e:
        print(f"Error getting tag by ID {tag_id}: {e}")
        return None
    finally:
        conn.close()

def get_tag_by_name(name: str):
    """Retrieves a tag by its name."""
    conn = database.get_db_connection()
    try:
        tag_data = conn.execute("SELECT id, name, description FROM tags WHERE name = ?", (name,)).fetchone()
        if tag_data:
            # return data_models.Tag(*tag_data) # If using data models
            return {'id': tag_data[0], 'name': tag_data[1], 'description': tag_data[2]}
        return None
    except Exception as e:
        print(f"Error getting tag by name '{name}': {e}")
        return None
    finally:
        conn.close()

def get_all_tags():
    """Retrieves all tags from the database."""
    conn = database.get_db_connection()
    try:
        tags_data = conn.execute("SELECT id, name, description FROM tags").fetchall()
        # return [data_models.Tag(*tag) for tag in tags_data] # If using data models
        return [{'id': tag[0], 'name': tag[1], 'description': tag[2]} for tag in tags_data]
    except Exception as e:
        print(f"Error getting all tags: {e}")
        return []
    finally:
        conn.close()

def apply_tag_to_artifact(artifact_id: int, tag_id: int):
    """Links a tag to an artifact."""
    conn = database.get_db_connection()
    try:
        conn.execute("INSERT INTO artifact_tags (artifact_id, tag_id) VALUES (?, ?)", (artifact_id, tag_id))
        conn.commit()
        print(f"Tag {tag_id} applied to artifact {artifact_id}.")
        return True
    except sqlite3.IntegrityError:
        print(f"Tag {tag_id} already applied to artifact {artifact_id}.")
        return False # Tag already exists for this artifact
    except Exception as e:
        print(f"Error applying tag {tag_id} to artifact {artifact_id}: {e}")
        return False
    finally:
        conn.close()

def apply_tag_to_project(project_id: int, tag_id: int):
    """Links a tag to a project (theme)."""
    conn = database.get_db_connection()
    try:
        conn.execute("INSERT INTO project_tags (project_id, tag_id) VALUES (?, ?)", (project_id, tag_id))
        conn.commit()
        print(f"Tag {tag_id} applied to project {project_id}.")
        return True
    except sqlite3.IntegrityError:
        print(f"Tag {tag_id} already applied to project {project_id}.")
        return False # Tag already exists for this project
    except Exception as e:
        print(f"Error applying tag {tag_id} to project {project_id}: {e}")
        return False
    finally:
        conn.close()

def get_tags_for_artifact(artifact_id: int):
    """Retrieves all tags linked to an artifact."""
    conn = database.get_db_connection()
    try:
        query = """
        SELECT t.id, t.name, t.description
        FROM tags t
        JOIN artifact_tags at ON t.id = at.tag_id
        WHERE at.artifact_id = ?
        """
        tags_data = conn.execute(query, (artifact_id,)).fetchall()
        # return [data_models.Tag(*tag) for tag in tags_data] # If using data models
        return [{'id': tag[0], 'name': tag[1], 'description': tag[2]} for tag in tags_data]
    except Exception as e:
        print(f"Error getting tags for artifact {artifact_id}: {e}")
        return []
    finally:
        conn.close()

def get_tags_for_project(project_id: int):
    """Retrieves all tags linked to a project (theme)."""
    conn = database.get_db_connection()
    try:
        query = """
        SELECT t.id, t.name, t.description
        FROM tags t
        JOIN project_tags pt ON t.id = pt.tag_id
        WHERE pt.project_id = ?
        """
        tags_data = conn.execute(query, (project_id,)).fetchall()
        # return [data_models.Tag(*tag) for tag in tags_data] # If using data models
        return [{'id': tag[0], 'name': tag[1], 'description': tag[2]} for tag in tags_data]
    except Exception as e:
        print(f"Error getting tags for project {project_id}: {e}")
        return []
    finally:
        conn.close()

def remove_tag_from_artifact(artifact_id: int, tag_id: int):
    """Removes a tag link from an artifact."""
    conn = database.get_db_connection()
    try:
        conn.execute("DELETE FROM artifact_tags WHERE artifact_id = ? AND tag_id = ?", (artifact_id, tag_id))
        conn.commit()
        print(f"Tag {tag_id} removed from artifact {artifact_id}.")
        return True
    except Exception as e:
        print(f"Error removing tag {tag_id} from artifact {artifact_id}: {e}")
        return False
    finally:
        conn.close()

def remove_tag_from_project(project_id: int, tag_id: int):
    """Removes a tag link from a project."""
    conn = database.get_db_connection()
    try:
        conn.execute("DELETE FROM project_tags WHERE project_id = ? AND tag_id = ?", (project_id, tag_id))
        conn.commit()
        print(f"Tag {tag_id} removed from project {project_id}.")
        return True
    except Exception as e:
        print(f"Error removing tag {tag_id} from project {project_id}: {e}")
        return False
    finally:
        conn.close()

def analyze_and_suggest_tags(text: str):
    """
    Analyzes text content (e.g., artifact description) and suggests relevant tags.
    This is a simplified implementation based on keyword matching.
    A more advanced version would use NLP techniques (nominal/verbal cores).
    """
    if not text:
        return []

    # Get all existing tag names
    all_tags = get_all_tags()
    tag_names = {tag['name'].lower(): tag['id'] for tag in all_tags}

    # Simple keyword matching: split text and check if words match tag names
    # This is a very basic approach. Real NLP would be more sophisticated.
    words = text.lower().split()
    suggested_tag_ids = set()

    for word in words:
        # Remove punctuation for basic matching
        cleaned_word = ''.join(filter(str.isalnum, word))
        if cleaned_word in tag_names:
            suggested_tag_ids.add(tag_names[cleaned_word])

    # Return tag objects for suggested IDs
    suggested_tags = [get_tag_by_id(tag_id) for tag_id in suggested_tag_ids]
    return [tag for tag in suggested_tags if tag is not None]

def auto_tag_artifact(artifact_id: int):
    """
    Retrieves artifact content, analyzes it, and automatically applies suggested tags.
    Requires a function to get artifact details including its description.
    """
    # Placeholder: Need a function from db/database or models/data_models
    # to get artifact details by ID, including description.
    # Assuming such a function exists: get_artifact_details(artifact_id)
    # artifact = database.get_artifact_details(artifact_id) # Example call

    # For now, let's simulate getting artifact description
    # In a real scenario, you'd fetch this from the DB
    conn = database.get_db_connection()
    artifact_data = conn.execute("SELECT description FROM artifacts WHERE id = ?", (artifact_id,)).fetchone()
    conn.close()

    if not artifact_data:
        print(f"Artifact with ID {artifact_id} not found.")
        return False

    artifact_description = artifact_data[0]
    if not artifact_description:
        print(f"Artifact {artifact_id} has no description to analyze.")
        return False

    suggested_tags = analyze_and_suggest_tags(artifact_description)

    if not suggested_tags:
        print(f"No tags suggested for artifact {artifact_id}.")
        return False

    applied_count = 0
    for tag in suggested_tags:
        if apply_tag_to_artifact(artifact_id, tag['id']):
            applied_count += 1

    print(f"Automatically applied {applied_count} tags to artifact {artifact_id}.")
    return applied_count > 0

# Example Usage (for testing purposes, remove in final app)
if __name__ == '__main__':
    # Ensure the database and tables are initialized before running this
    # database.init_db() # Call this from app.py or setup script

    # Create some initial tags
    tag_id_creative = create_tag("Criatividade", "Tags related to creative projects/ideas")
    tag_id_business = create_tag("Negócios", "Tags related to business projects/tasks")
    tag_id_planning = create_tag("Planejamento", "Tags related to planning activities")
    tag_id_code = create_tag("Código", "Tags related to programming code")

    # Simulate creating a project and an artifact
    # In real app, get these IDs from DB operations
    simulated_project_id = 1
    simulated_artifact_id = 1

    # Simulate adding a project and artifact to the DB for testing auto-tagging
    conn = database.get_db_connection()
    try:
        conn.execute("INSERT OR IGNORE INTO projects (id, title, description) VALUES (?, ?, ?)", (simulated_project_id, "Meu Projeto Criativo", "Este é um projeto focado em brainstorming e ideias criativas."))
        conn.execute("INSERT OR IGNORE INTO artifacts (id, project_id, description) VALUES (?, ?, ?)", (simulated_artifact_id, simulated_project_id, "Descrição do artefato com foco em criatividade e planejamento."))
        conn.commit()
    except Exception as e:
        print(f"Error simulating project/artifact creation: {e}")
    finally:
        conn.close()


    # Apply tags manually
    if tag_id_creative:
        apply_tag_to_project(simulated_project_id, tag_id_creative)
    if tag_id_planning:
         apply_tag_to_project(simulated_project_id, tag_id_planning)


    # Get tags for the project
    project_tags = get_tags_for_project(simulated_project_id)
    print(f"\nTags for Project {simulated_project_id}: {project_tags}")

    # Auto-tag an artifact
    auto_tag_artifact(simulated_artifact_id)

    # Get tags for the artifact
    artifact_tags = get_tags_for_artifact(simulated_artifact_id)
    print(f"\nTags for Artifact {simulated_artifact_id}: {artifact_tags}")

    # Remove a tag from the artifact
    if tag_id_planning:
        remove_tag_from_artifact(simulated_artifact_id, tag_id_planning)

    # Get tags for the artifact again
    artifact_tags_after_removal = get_tags_for_artifact(simulated_artifact_id)
    print(f"Tags for Artifact {simulated_artifact_id} after removal: {artifact_tags_after_removal}")
