import dataclasses
from typing import List, Optional, Any

# Define data models using dataclasses for clarity and simplicity

@dataclasses.dataclass
class User:
    """Represents a user for login."""
    id: Optional[int] = None  # Database primary key
    username: str
    password_hash: str # Store hashed password

@dataclasses.dataclass
class Project:
    """Represents a project."""
    id: Optional[int] = None  # Database primary key
    title: str
    description: str
    category: Optional[str] = None # e.g., 'creative', 'business', 'analytical' - linked to brain cube visualization
    user_id: int # Foreign key linking to User

@dataclasses.dataclass
class Artifact:
    """Represents a data artifact within a project."""
    id: Optional[int] = None  # Database primary key
    project_id: int          # Foreign key linking to Project
    description: str
    scope: Optional[str] = None
    # These fields might store serialized data (e.g., JSON strings) in the DB
    # and be loaded as Python objects (lists, dicts) by the DB layer.
    main_artifacts_refs: Optional[List[int]] = None # References to other artifact IDs
    task_list: Optional[List[str]] = None        # List of task strings or descriptions
    # Content for spell/code check? Maybe stored separately or within description/scope

@dataclasses.dataclass
class Tag:
    """Represents a classification tag."""
    id: Optional[int] = None  # Database primary key
    name: str
    type: Optional[str] = None # e.g., 'nominal', 'verbal'
    # Tags are linked to artifacts, and artifacts are linked to projects.
    # Direct link to project theme/axis might be implicit via project category
    # or managed through logic, not a direct FK here unless needed.

@dataclasses.dataclass
class ArtifactTag:
    """Represents the many-to-many relationship between Artifacts and Tags."""
    artifact_id: int
    tag_id: int

@dataclasses.dataclass
class Relationship:
    """Represents a connection (synapse/tree link) between two artifacts."""
    id: Optional[int] = None # Database primary key
    artifact_id_1: int
    artifact_id_2: int
    type: str              # e.g., 'tree', 'synapse'
    fuzzy_score: float     # Score from fuzzy logic, indicating strength/relevance

# Note: The database module (db/database.py) will be responsible for
# mapping these dataclasses to database rows and handling CRUD operations.
# It will also handle serialization/deserialization for fields like
# main_artifacts_refs and task_list if they are stored as text/blob (e.g., JSON).
# The fuzzy logic (logic/fuzzy_organizer.py) will determine fuzzy_score and type.
# The tagging logic (logic/tagging.py) will manage Tags and ArtifactTag relationships.
# The AI modules (ai/megamini.py, ai/gemini_cocreator.py) will interact with
# these data structures via the database layer.
