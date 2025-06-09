# logic/fuzzy_organizer.py
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Assuming data models are available from models/data_models.py
# from models.data_models import Artifact, RelationshipType

# Assuming database functions are available from db/database.py
# from db.database import get_all_artifacts, add_relationship, update_relationship, delete_relationship

class FuzzyOrganizer:
    """
    Handles fuzzy logic for establishing and managing relationships between
    data artifacts based on their content, tags, and context.
    This module determines how artifacts are linked in the 'synapse' and 'tree' structure.
    """

    def __init__(self, title_weight=0.4, description_weight=0.3, content_weight=0.3, tag_weight=0.3):
        """
        Initializes the FuzzyOrganizer with weights for different artifact attributes.

        Args:
            title_weight (float): Weight for title similarity.
            description_weight (float): Weight for description similarity.
            content_weight (float): Weight for content similarity.
            tag_weight (float): Weight for tag similarity (based on matching tags).
            Weights should ideally sum up to 1.0. They will be normalized internally.
        """
        self.weights = {
            'title': title_weight,
            'description': description_weight,
            'content': content_weight,
            'tags': tag_weight
        }
        self._normalize_weights()
        logging.info(f"FuzzyOrganizer initialized with weights: {self.weights}")

    def _normalize_weights(self):
        """Normalizes the weights so they sum up to 1.0."""
        total_weight = sum(self.weights.values())
        if total_weight == 0:
            logging.warning("Total weight is zero. Setting default equal weights.")
            num_weights = len(self.weights)
            if num_weights > 0:
                equal_weight = 1.0 / num_weights
                for key in self.weights:
                    self.weights[key] = equal_weight
        else:
            for key in self.weights:
                self.weights[key] /= total_weight
        logging.debug(f"Normalized weights: {self.weights}")


    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculates fuzzy similarity between two text strings."""
        if not text1 or not text2:
            return 0.0
        # Using partial_ratio can be better for snippets or descriptions
        return fuzz.partial_ratio(text1, text2)

    def calculate_tag_similarity(self, tags1: list[str], tags2: list[str]) -> float:
        """Calculates similarity based on matching tags."""
        if not tags1 or not tags2:
            return 0.0
        set1 = set(tag.lower() for tag in tags1)
        set2 = set(tag.lower() for tag in tags2)
        common_tags = set1.intersection(set2)
        # Simple approach: percentage of common tags relative to the average number of tags
        # More complex: Jaccard index or weighted tag similarity
        if not set1 and not set2: # Both empty
             return 0.0
        # Jaccard Index
        union_size = len(set1.union(set2))
        if union_size == 0: return 0.0 # Should not happen if not set1 and not set2 is handled
        return (len(common_tags) / union_size) * 100.0


    def calculate_artifact_similarity(self, artifact1, artifact2) -> float:
        """
        Calculates a weighted fuzzy similarity score between two artifacts.

        Args:
            artifact1: The first artifact object (assuming it has id, title, description, content, tags).
            artifact2: The second artifact object.

        Returns:
            float: A similarity score between 0 and 100.
        """
        if artifact1.id == artifact2.id:
            return 0.0 # An artifact is not similar to itself for connection purposes

        title_sim = self.calculate_text_similarity(getattr(artifact1, 'title', ''), getattr(artifact2, 'title', ''))
        desc_sim = self.calculate_text_similarity(getattr(artifact1, 'description', ''), getattr(artifact2, 'description', ''))
        content_sim = self.calculate_text_similarity(getattr(artifact1, 'content', ''), getattr(artifact2, 'content', ''))
        tag_sim = self.calculate_tag_similarity(getattr(artifact1, 'tags', []), getattr(artifact2, 'tags', [])) # Assuming tags is a list of strings

        # Calculate weighted score
        weighted_score = (
            self.weights['title'] * title_sim +
            self.weights['description'] * desc_sim +
            self.weights['content'] * content_sim +
            self.weights['tags'] * tag_sim
        )

        logging.debug(f"Comparing Artifact {artifact1.id} and {artifact2.id}: "
                      f"Title={title_sim:.2f}, Desc={desc_sim:.2f}, Content={content_sim:.2f}, Tags={tag_sim:.2f} -> Weighted={weighted_score:.2f}")

        return weighted_score

    def find_potential_connections(self, target_artifact, all_artifacts, threshold: int = 70) -> list:
        """
        Finds potential connections for a target artifact among a list of all artifacts
        based on fuzzy similarity exceeding a threshold.

        Args:
            target_artifact: The artifact for which to find connections.
            all_artifacts (list): A list of all other artifact objects to compare against.
                                  These objects should have 'id', 'title', 'description', 'content', 'tags' attributes.
            threshold (int): The minimum similarity score (0-100) to consider a connection.

        Returns:
            list: A list of tuples (potential_artifact, similarity_score) where
                  similarity_score is >= threshold.
        """
        if not all_artifacts:
            logging.info("No artifacts provided to find connections against.")
            return []

        potential_connections = []
        logging.info(f"Finding potential connections for Artifact ID: {getattr(target_artifact, 'id', 'N/A')} (Threshold: {threshold})")

        for artifact in all_artifacts:
            # Ensure artifact is valid and not the target itself
            if artifact and getattr(artifact, 'id', None) is not None and artifact.id != getattr(target_artifact, 'id', None):
                try:
                    score = self.calculate_artifact_similarity(target_artifact, artifact)
                    if score >= threshold:
                        potential_connections.append((artifact, score))
                except Exception as e:
                    logging.error(f"Error calculating similarity between artifact {getattr(target_artifact, 'id', 'N/A')} and {getattr(artifact, 'id', 'N/A')}: {e}")


        # Optional: Sort by score
        potential_connections.sort(key=lambda item: item[1], reverse=True)

        logging.info(f"Found {len(potential_connections)} potential connections for Artifact ID: {getattr(target_artifact, 'id', 'N/A')}")

        return potential_connections

    # The following methods are placeholders demonstrating how this logic
    # would integrate with the database layer to persist relationships.
    # Actual implementation would require database connection and CRUD functions.

    # def establish_fuzzy_relationships_in_db(self, target_artifact, potential_connections):
    #     """
    #     Establishes or updates relationships in the database based on potential connections.
    #
    #     Args:
    #         target_artifact: The artifact for which connections were found.
    #         potential_connections (list): List of (artifact, score) tuples from find_potential_connections.
    #     """
    #     if not potential_connections:
    #         logging.info(f"No potential connections to establish for Artifact ID: {getattr(target_artifact, 'id', 'N/A')}")
    #         return
    #
    #     logging.info(f"Establishing relationships for Artifact ID: {getattr(target_artifact, 'id', 'N/A')}")
    #     for connected_artifact, score in potential_connections:
    #         try:
    #             # Assuming add_relationship takes source_id, target_id, score, type
    #             # And handles updates if relationship already exists
    #             # RelationshipType could be an Enum or string like 'fuzzy_similarity'
    #             # add_relationship(target_artifact.id, connected_artifact.id, score, 'fuzzy_similarity')
    #             logging.debug(f"  -> Attempting to add/update relationship: {target_artifact.id} -> {connected_artifact.id} with score {score:.2f}")
    #             pass # Placeholder for DB call
    #         except Exception as e:
    #             logging.error(f"Error establishing relationship between {target_artifact.id} and {connected_artifact.id}: {e}")

    # def update_all_fuzzy_relationships(self):
    #     """
    #     Recalculates and updates fuzzy relationships for all artifacts in the database.
    #     This can be a resource-intensive operation.
    #     """
    #     logging.info("Starting full fuzzy relationship update...")
    #     try:
    #         # Assuming get_all_artifacts() fetches all artifacts from the DB
    #         # all_artifacts = get_all_artifacts()
    #         all_artifacts = [] # Placeholder
    #         if not all_artifacts:
    #             logging.info("No artifacts found in the database.")
    #             return
    #
    #         # Optional: Clear existing fuzzy relationships before recalculating
    #         # delete_relationships_by_type('fuzzy_similarity') # Assuming such a function exists
    #
    #         for i, artifact in enumerate(all_artifacts):
    #             logging.info(f"Processing artifact {i+1}/{len(all_artifacts)} (ID: {artifact.id})...")
    #             # Find connections for the current artifact against all others
    #             potential_connections = self.find_potential_connections(artifact, all_artifacts)
    #             # Persist the found connections
    #             # self.establish_fuzzy_relationships_in_db(artifact, potential_connections)
    #
    #         logging.info("Full fuzzy relationship update finished.")
    #
    #     except Exception as e:
    #         logging.critical(f"Critical error during full fuzzy relationship update: {e}")

# Note: The actual database interaction logic (get_all_artifacts, add_relationship, etc.)
# should be implemented in db/database.py and imported here if needed for the
# establish_fuzzy_relationships_in_db or update_all_fuzzy_relationships methods.
# The current implementation focuses solely on the fuzzy logic calculation.
