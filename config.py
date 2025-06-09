import os

# --- Application Settings ---
APP_NAME = "Cérebro Sináptico" # Default app name
SPECIAL_APP_NAME = "Cérebro do Jesus" # Special name to activate cocreator mode
SPECIAL_PASSWORD = "jesus" # Special password to activate cocreator mode

# --- Database Settings ---
DATABASE_PATH = "db/cerebro_sinaptico.db" # Path to the SQLite database file

# --- API Keys (Read from Environment Variables for Security) ---
# It's recommended to set these environment variables outside the code.
# Example: export GOOGLE_GEMINI_API_KEY='your_key_here'
GOOGLE_GEMINI_API_KEY = os.getenv("GOOGLE_GEMINI_API_KEY")
# Note: Google Drive API typically uses OAuth, not direct key/password.
# This placeholder is for potential future API needs.
GOOGLE_DRIVE_API_KEY = os.getenv("GOOGLE_DRIVE_API_KEY") # Placeholder, likely not used for standard auth

# --- Other Constants ---
# Define categories for project classification (used in brain cubes viz)
PROJECT_CATEGORIES = ["Criativo", "Negócios", "Acadêmico", "Pessoal", "Outro"]

# --- Fuzzy Logic Settings ---
# Threshold for considering two artifacts/tags/etc. a match (0-100)
FUZZY_MATCH_THRESHOLD = 70

# --- AI Settings (Megamini) ---
# Placeholder for settings related to real-time correction
# Might include confidence thresholds or specific model parameters

# --- Visualization Settings ---
# Colors, sizes, etc. for graphs and brain cubes

# --- Security Settings ---
# Note: The special login "Cérebro do Jesus" / "jesus" is hardcoded as per requirements.
# For production systems, more secure authentication methods are recommended.

# --- Feature Flags (Optional) ---
# Use these to easily enable/disable features during development
ENABLE_GOOGLE_DRIVE_INTEGRATION = False # Based on architectural note about auth difficulty
ENABLE_GEMINI_COCREATOR = True # Controlled by special login

# --- Debug Settings ---
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() in ('true', '1', 't')

# Print a warning if API keys are not set in debug mode
if DEBUG_MODE and not GOOGLE_GEMINI_API_KEY:
    print("WARNING: GOOGLE_GEMINI_API_KEY environment variable not set.")
if DEBUG_MODE and not GOOGLE_DRIVE_API_KEY and ENABLE_GOOGLE_DRIVE_INTEGRATION:
     print("WARNING: GOOGLE_DRIVE_API_KEY environment variable not set, or integration disabled.")
