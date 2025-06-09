```python
import streamlit as st
import sqlite3
import os
import sys

# Add parent directory to sys.path to allow importing modules from other directories
# This assumes app.py is at the root and other modules are in subdirectories like db/, models/, etc.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

# Import project modules
try:
    import config
    from db import database
    from models import data_models
    from logic import fuzzy_organizer # Placeholder import
    from logic import tagging # Placeholder import
    from viz import graph_forest # Placeholder import
    from viz import brain_cubes # Placeholder import
    from integrations import google_drive # Placeholder import
    from ai import megamini # Placeholder import
    from ai import gemini_cocreator # Placeholder import
except ImportError as e:
    st.error(f"Error importing project modules: {e}")
    st.stop() # Stop execution if core modules cannot be imported

# --- Session State Management ---
def init_session_state():
    """Initializes Streamlit session state variables."""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'current_view' not in st.session_state:
        st.session_state.current_view = 'login' # 'login', 'dashboard', 'project_detail'
    if 'selected_project_id' not in st.session_state:
        st.session_state.selected_project_id = None
    if 'cocreator_mode' not in st.session_state:
        st.session_state.cocreator_mode = False

def navigate_to(view, project_id=None):
    """Changes the current view and updates selected project ID."""
    st.session_state.current_view = view
    st.session_state.selected_project_id = project_id
    st.rerun()

# --- Database Initialization ---
def setup_database():
    """Ensures the database and tables are initialized."""
    try:
        database.init_db()
    except Exception as e:
        st.error(f"Error initializing database: {e}")
        st.stop()

# --- Login View ---
def render_login():
    """Renders the login form."""
    st.title(config.APP_NAME)
    st.header("Login")

    with st.form("login_form"):
        # The prompt mentions email/password login for Google Drive, but the app login
        # is described as simple password "jesus". We'll implement the simple app login here.
        # A username field is added for completeness, though validation might be minimal.
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")

        if submit_button:
            # Simple password check as per description
            if password == "jesus":
                st.session_state.logged_in = True
                # Check for special cocreator mode condition
                if config.APP_NAME == "Cérebro do Jesus":
                    st.session_state.cocreator_mode = True
                    st.success("Login successful! Cocreator mode activated.")
                else:
                    st.session_state.cocreator_mode = False
                    st.success("Login successful!")

                navigate_to('dashboard')
            else:
                st.error("Invalid username or password.")

# --- Dashboard View ---
def render_dashboard():
    """Renders the main dashboard showing projects and options."""
    st.title(config.APP_NAME)

    if st.session_state.cocreator_mode:
        st.subheader("Cocreator Mode Active")

    st.header("Your Projects")

    # --- Sidebar Navigation ---
    with st.sidebar:
        st.header("Navigation")
        if st.button("Dashboard", key="nav_dashboard"):
             navigate_to('dashboard')
        st.markdown("---")
        st.header("Visualizations")
        # Add buttons/links to visualization views
        if st.button("Graph Forest (Synapses)", key="nav_graph"):
             st.info("Graph Forest visualization coming soon!") # Placeholder
             # navigate_to('graph_viz') # Example navigation
        if st.button("Brain Cubes (Categories)", key="nav_brain"):
             st.info("Brain Cubes visualization coming soon!") # Placeholder
             # navigate_to('brain_viz') # Example navigation
        st.markdown("---")
        st.header("Actions")
        if st.button("Create New Project", key="nav_new_project"):
             navigate_to('create_project') # Navigate to a creation form view
        # Add other actions like Google Drive sync (placeholder)
        # if st.button("Sync with Google Drive", key="nav_gdrive"):
        #     st.info("Google Drive integration coming soon!") # Placeholder
        #     # google_drive.sync_data() # Example call
        st.markdown("---")
        if st.button("Logout", key="nav_logout"):
            st.session_state.logged_in = False
            st.session_state.cocreator_mode = False
            navigate_to('login')


    # --- Main Dashboard Content ---
    conn = database.get_db_connection()
    projects = database.get_all_projects(conn)
    conn.close()

    if not projects:
        st.info("No projects found. Create a new one to get started!")
    else:
        for project in projects:
            st.subheader(project['title'])
            st.write(f"**Description:** {project['description']}")
            # Display creation date or other relevant info
            # st.write(f"Created: {project['created_at']}") # Assuming a created_at field

            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.button("View Details", key=f"view_project_{project['id']}"):
                    navigate_to('project_detail', project['id'])
            with col2:
                 # Add Edit button - will navigate to a similar form as create
                 if st.button("Edit", key=f"edit_project_{project['id']}"):
                      navigate_to('edit_project', project['id']) # Navigate to edit form view
            with col3:
                 # Add Delete button
                 if st.button("Delete", key=f"delete_project_{project['id']}"):
                      # Implement delete logic (maybe with confirmation)
                      if st.warning(f"Are you sure you want to delete project '{project['title']}'?"):
                           if st.button("Confirm Delete", key=f"confirm_delete_{project['id']}"):
                                try:
                                    conn = database.get_db_connection()
                                    database.delete_project(conn, project['id'])
                                    conn.close()
                                    st.success(f"Project '{project['title']}' deleted.")
                                    st.rerun() # Refresh the dashboard
                                except Exception as e:
                                    st.error(f"Error deleting project: {e}")


            st.markdown("---")

# --- Create/Edit Project View ---
def render_project_form(project_id=None):
    """Renders a form to create or edit a project."""
    is_editing = project_id is not None
    st.title("Project Details")

    conn = database.get_db_connection()
    project_data = None
    if is_editing:
        project_data = database.get_project(conn, project_id)
        if not project_data:
            st.error("Project not found.")
            conn.close()
            navigate_to('dashboard')
            return
        st.header(f"Edit Project: {project_data['title']}")
    else:
        st.header("Create New Project")

    with st.form("project_form", clear_on_submit=not is_editing):
        title = st.text_input("Project Title", value=project_data['title'] if is_editing else "")
        description = st.text_area("Project Description", value=project_data['description'] if is_editing else "")
        # Add fields for other project-level data if needed later (e.g., category)

        submit_button_text = "Save Changes" if is_editing else "Create Project"
        submit_button = st.form_submit_button(submit_button_text)
        cancel_button = st.form_submit_button("Cancel")

        if submit_button:
            if not title:
                st.warning("Project title is required.")
            else:
                try:
                    if is_editing:
                        database.update_project(conn, project_id, title, description)
                        st.success("Project updated successfully!")
                    else:
                        new_project_id = database.create_project(conn, title, description)
                        st.success("Project created successfully!")
                        project_id = new_project_id # Set ID for potential immediate view

                    conn.commit() # Commit changes
                    conn.close()
                    navigate_to('project_detail', project_id) # Go to details after save
                except Exception as e:
                    conn.rollback() # Rollback in case of error
                    conn.close()
                    st.error(f"Error saving project: {e}")

        if cancel_button:
            conn.close()
            if is_editing:
                 navigate_to('project_detail', project_id) # Go back to details
            else:
                 navigate_to('dashboard') # Go back to dashboard

    # --- Sidebar Navigation ---
    with st.sidebar:
        st.header("Navigation")
        if st.button("Back to Dashboard", key="form_nav_dashboard"):
             navigate_to('dashboard')
        if is_editing and st.button("Back to Project Details", key="form_nav_details"):
             navigate_to('project_detail', project_id)


# --- Project Detail View ---
def render_project_detail(project_id):
    """Renders the details of a specific project, including artifacts and tasks."""
    conn = database.get_db_connection()
    project = database.get_project(conn, project_id)

    if not project:
        st.error("Project not found.")
        conn.close()
        navigate_to('dashboard')
        return

    st.title(f"Project: {project['title']}")
    st.subheader("Description")
    st.write(project['description'])

    # --- Sidebar Navigation ---
    with st.sidebar:
        st.header("Navigation")
        if st.button("Back to Dashboard", key="detail_nav_dashboard"):
             navigate_to('dashboard')
        st.markdown("---")
        st.header("Project Actions")
        if st.button("Edit Project Info", key="detail_edit_project"):
             navigate_to('edit_project', project_id)
        # Add button to add new artifact
        if st.button("Add New Artifact", key="detail_add_artifact"):
             st.session_state.show_add_artifact_form = True # Use session state to show/hide form
             st.rerun() # Rerun to show the form
        # Add button to add new task
        if st.button("Add New Task", key="detail_add_task"):
             st.session_state.show_add_task_form = True # Use session state to show/hide form
             st.rerun() # Rerun to show the form
        st.markdown("---")
        # Add Cocreator button if mode is active
        if st.session_state.cocreator_mode:
             st.header("Cocreator")
             if st.button("Ask Cocreator about this Project", key="detail_cocreator"):
                  st.session_state.show_cocreator_input = True # Use session state
                  st.rerun() # Rerun to show input/output area


    # --- Main Project Detail Content ---

    # Add New Artifact Form (shown conditionally)
    if st.session_state.get('show_add_artifact_form', False):
        st.subheader("Add New Artifact")
        with st.form("add_artifact_form", clear_on_submit=True):
            artifact_description = st.text_area("Artifact Description")
            artifact_scope = st.text_area("Artifact Scope")
            # Add fields for tags, etc. later
            submit_artifact = st.form_submit_button("Save Artifact")
            cancel_artifact = st.form_submit_button("Cancel")

            if submit_artifact:
                if not artifact_description:
                    st.warning("Artifact description is required.")
                else:
                    try:
                        # Use Megamini for spelling/grammar correction on description/scope before saving
                        corrected_description = megamini.correct_text(artifact_description)
                        corrected_scope = megamini.correct_text(artifact_scope)

                        database.create_artifact(conn, project_id, corrected_description, corrected_scope)
                        conn.commit()
                        st.success("Artifact added successfully!")
                        st.session_state.show_add_artifact_form = False # Hide form
                        st.rerun() # Refresh view
                    except Exception as e:
                        conn.rollback()
                        st.error(f"Error adding artifact: {e}")

            if cancel_artifact:
                st.session_state.show_add_artifact_form = False # Hide form
                st.rerun() # Refresh view
        st.markdown("---") # Separator after form

    # Add New Task Form (shown conditionally)
    if st.session_state.get('show_add_task_form', False):
        st.subheader("Add New Task")
        with st.form("add_task_form", clear_on_submit=True):
            task_description = st.text_area("Task Description")
            # Add fields for status, due date, etc. later
            submit_task = st.form_submit_button("Save Task")
            cancel_task = st.form_submit_button("Cancel")

            if submit_task:
                if not task_description:
                    st.warning("Task description is required.")
                else:
                    try:
                        # Use Megamini for spelling/grammar correction on task description
                        corrected_task_description = megamini.correct_text(task_description)

                        database.create_task(conn, project_id, corrected_task_description) # Assuming create_task exists
                        conn.commit()
                        st.success("Task added successfully!")
                        st.session_state.show_add_task_form = False # Hide form
                        st.rerun() # Refresh view
                    except Exception as e:
                        conn.rollback()
                        st.error(f"Error adding task: {e}")

            if cancel_task:
                st.session_state.show_add_task_form = False # Hide form
                st.rerun() # Refresh view
        st.markdown("---") # Separator after form

    # Cocreator Input/Output Area (shown conditionally)
    if st.session_state.get('show_cocreator_input', False) and st.session_state.cocreator_mode:
         st.subheader("Cocreator Assistant")
         cocreator_prompt = st.text_area("Ask the Cocreator about this project:", key="cocreator_prompt_input")
         if st.button("Get Assistance", key="run_cocreator_button"):
              if cocreator_prompt:
                   with st.spinner("Cocreator is thinking..."):
                        try:
                             # Fetch project data and related artifacts/tasks for context
                             project_data_for_ai = database.get_project(conn, project_id)
                             artifacts_for_ai = database.get_artifacts_by_project(conn, project_id)
                             tasks_for_ai = database.get_tasks_by_project(conn, project_id) # Assuming get_tasks_by_project exists

                             # Pass data and prompt to the cocreator module
                             response = gemini_cocreator.get_assistance(
                                  prompt=cocreator_prompt,
                                  project=project_data_for_ai,
                                  artifacts=artifacts_for_ai,
                                  tasks=tasks_for_ai
                                  # Add other relevant data like tags, relationships if needed
                             )
                             st.subheader("Cocreator Response:")
                             st.write(response)
                        except Exception as e:
                             st.error(f"Error getting assistance from Cocreator: {e}")
              else:
                   st.warning("Please enter a prompt for the Cocreator.")
         st.markdown("---") # Separator

    # Display Artifacts
    st.subheader("Artifacts")
    artifacts = database.get_artifacts_by_project(conn, project_id) # Assuming this function exists

    if not artifacts:
        st.info("No artifacts added yet.")
    else:
        for artifact in artifacts:
            st.write(f"**Description:** {artifact['description']}")
            st.write(f"**Scope:** {artifact['scope']}")
            # Add buttons to edit/delete artifact
            col_art1, col_art2 = st.columns([1, 1])
            with col_art1:
                 if st.button("Edit Artifact", key=f"edit_artifact_{artifact['id']}"):
                      # Navigate to an artifact edit form (similar logic to project form)
                      st.info("Artifact editing coming soon!") # Placeholder
                      # navigate_to('edit_artifact', artifact['id'])
            with col_art2:
                 if st.button("Delete Artifact", key=f"delete_artifact_{artifact['id']}"):
                      # Implement delete logic (maybe with confirmation)
                      if st.warning(f"Are you sure you want to delete this artifact?"):
                           if st.button("Confirm Delete Artifact", key=f"confirm_delete_artifact_{artifact['id']}"):
                                try:
                                    database.delete_artifact(conn, artifact['id']) # Assuming delete_artifact exists
                                    conn.commit()
                                    st.success("Artifact deleted.")
                                    st.rerun() # Refresh the view
                                except Exception as e:
                                    conn.rollback()
                                    st.error(f"Error deleting artifact: {e}")

            st.markdown("---") # Separator

    # Display Tasks
    st.subheader("Tasks")
    tasks = database.get_tasks_by_project(conn, project_id) # Assuming this function exists

    if not tasks:
        st.info("No tasks added yet.")
    else:
        for task in tasks:
            st.write(f"- {task['description']}")
            # Add buttons to edit/delete task
            col_task1, col_task2 = st.columns([1, 1])
            with col_task1:
                 if st.button("Edit Task", key=f"edit_task_{task['id']}"):
                      # Navigate to a task edit form
                      st.info("Task editing coming soon!") # Placeholder
                      # navigate_to('edit_task', task['id'])
            with col_task2:
                 if st.button("Delete Task", key=f"delete_task_{task['id']}"):
                      # Implement delete logic (maybe with confirmation)
                      if st.warning(f"Are you sure you want to delete this task?"):
                           if st.button("Confirm Delete Task", key=f"confirm_delete_task_{task['id']}"):
                                try:
                                    database.delete_task(conn, task['id']) # Assuming delete_task exists
                                    conn.commit()
                                    st.success("Task deleted.")
                                    st.rerun() # Refresh the view
                                except Exception as e:
                                    conn.rollback()
                                    st.error(f"Error deleting task: {e}")
            st.markdown("---") # Separator

    # Close connection
    conn.close()

    # --- Placeholder for other sections like Main Artifacts, Tags, Relationships ---
    st.subheader("Main Artifacts (Placeholder)")
    st.info("Section for highlighting key artifacts coming soon.")

    st.subheader("Tags (Placeholder)")
    st.info("Section for managing tags associated with this project and its artifacts coming soon.")

    st.subheader("Relationships / Synapses (Placeholder)")
    st.info("Section for visualizing artifact relationships using fuzzy logic coming soon.")


# --- Main Application Flow ---
def main():
    """Main function to run the Streamlit application."""
    init_session_state()
    setup_database() # Ensure DB is ready on startup

    if not st.session_state.logged_in:
        render_login()
    else:
        # Logged in, render different views based on session state
        if st.session_state.current_view == 'dashboard':
            render_dashboard()
        elif st.session_state.current_view == 'create_project':
             render_project_form(project_id=None)
        elif st.session_state.current_view == 'edit_project':
             render_project_form(project_id=st.session_state.selected_project_id)
        elif st.session_state.current_view == 'project_detail' and st.session_state.selected_project_id is not None:
            render_project_detail(st.session_state.selected_project_id)
        # Add other view renderings here (e.g., 'graph_viz', 'brain_viz', 'edit_artifact', etc.)
        else:
            # Default to dashboard if state is inconsistent
            navigate_to('dashboard')


if __name__ == "__main__":
    main()
```
