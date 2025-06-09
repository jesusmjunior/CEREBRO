import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

def render_brain_cubes(category_percentages):
    """
    Visualizes project category percentages as 'logical cubes' within a simplified
    representation of brain areas.

    Args:
        category_percentages (dict): A dictionary where keys are category names
                                     (e.g., 'Creative', 'Business') and values
                                     are their respective percentages (0-100).
                                     Example: {'Creative': 60, 'Business': 30, 'Other': 10}
    """
    st.subheader("Visualização do Cérebro de Dados")

    if not category_percentages or sum(category_percentages.values()) == 0:
        st.info("Nenhum dado de categoria disponível para visualização.")
        return

    # Ensure percentages sum to 100 (normalize if needed, though input is expected as percentages)
    # Simple check: if total is not 100, assume input was counts and calculate percentages
    total_sum = sum(category_percentages.values())
    if total_sum != 100 and total_sum > 0:
         normalized_percentages = {cat: (perc / total_sum) * 100 for cat, perc in category_percentages.items()}
    else:
         normalized_percentages = category_percentages


    # --- Matplotlib Figure Setup ---
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_xlim(0, 15) # Extended x-limit to place Metacarpus clearly outside
    ax.set_ylim(0, 10)
    ax.set_aspect('equal', adjustable='box')
    ax.axis('off') # Hide axes

    # --- Draw a very simplified brain outline (abstract) ---
    # This is just for visual context, not anatomically accurate
    brain_outline = patches.Ellipse((5, 5), width=8, height=9, angle=0, fc='lightblue', alpha=0.3, ec='darkblue', linewidth=2)
    ax.add_patch(brain_outline)

    # --- Define positions for brain areas (abstract coordinates) ---
    # These are relative positions within the 0-15 x 0-10 grid
    brain_areas = {
        'Lobo Pré-frontal': (5, 8), # Front-top
        'Giro do Cíngulo': (5, 6),  # Mid-central
        'Hipófise': (5, 2),         # Base-central
        'Lado Direito': (7.5, 5),   # Right half
        'Lado Esquerdo': (2.5, 5),  # Left half
        'Metacarpo': (12, 5)        # Outside the brain outline as requested
    }

    # --- Assign categories to areas conceptually (example mapping) ---
    # This mapping is arbitrary based on the prompt's hints (creativity area)
    # and general brain function associations (though simplified/abstracted).
    # The Metacarpus is included as requested, even if not brain.
    # Categories not explicitly mapped will be listed below or near the center.
    category_area_mapping = {
        'Creative': 'Lobo Pré-frontal', # Often associated with creativity
        'Analytic': 'Lado Direito',     # Often associated with logic/analysis (simplified)
        'Business': 'Lado Direito',     # Business projects might be analytic
        # Add more categories and map them as needed
    }

    # --- Place category 'cubes' (represented by text/labels) and percentages ---
    # We'll place the text near the designated brain area coordinates.
    # If a category isn't explicitly mapped, place it generally in the center or list it.

    placed_categories = set()
    y_offset_general = 0 # Offset for categories not mapped to specific areas, listed below

    for category, percentage in normalized_percentages.items():
        label_text = f"{category}: {percentage:.1f}%"
        color = 'black' # Default text color

        # Assign color based on category (optional)
        if category.lower() == 'creative':
            color = 'purple'
        elif category.lower() in ['business', 'analytic']:
            color = 'green'
        # Add more colors for other categories

        # Find the target area coordinates
        target_area_name = category_area_mapping.get(category)
        if target_area_name and target_area_name in brain_areas:
            x, y = brain_areas[target_area_name]
            # Simple placement near the area coordinate. Could add offsets for multiple categories per area.
            ax.text(x, y, label_text, fontsize=10, ha='center', va='center', color=color,
                    bbox=dict(boxstyle='round,pad=0.3', fc='white', alpha=0.7, ec=color)) # Add a background box
            placed_categories.add(category)
        # else: This category is not mapped to a specific brain area

    # --- List categories not mapped to specific areas below the brain ---
    unplaced_categories = {cat: perc for cat, perc in normalized_percentages.items() if cat not in placed_categories}
    if unplaced_categories:
        ax.text(5, 1.5, "Outras Categorias:", fontsize=10, ha='center', va='bottom', weight='bold')
        y_offset_general = 0
        for category, percentage in unplaced_categories.items():
             label_text = f"{category}: {percentage:.1f}%"
             color = 'gray' # Default color for unplaced
             # Assign color based on category if desired, even if unplaced
             if category.lower() == 'creative': color = 'purple'
             elif category.lower() in ['business', 'analytic']: color = 'green'

             ax.text(5, 1 - y_offset_general, label_text, fontsize=10, ha='center', va='top', color=color)
             y_offset_general += 0.4 # Move down for the next general category


    # --- Label the brain areas ---
    for area, (x, y) in brain_areas.items():
         # Place area labels slightly offset from the center of the area
         # Adjust position for Metacarpus as it's outside
         if area == 'Metacarpo':
              ax.text(x, y, area, fontsize=9, ha='left', va='center', color='darkred', weight='bold')
         else:
              ax.text(x, y + 0.7, area, fontsize=9, ha='center', va='bottom', color='darkred', weight='bold')


    # --- Add overall title ---
    ax.set_title("Distribuição de Projetos por Categoria em Áreas Conceituais do 'Cérebro'", fontsize=14)

    # --- Display the plot in Streamlit ---
    st.pyplot(fig)
    plt.close(fig) # Close the figure to free memory

# Example usage (for testing or demonstration within this file)
# if __name__ == '__main__':
#     # Sample data (example percentages)
#     sample_data_percentages = {
#         'Creative': 40,
#         'Business': 30,
#         'Analytic': 15,
#         'Research': 10,
#         'Personal': 5
#     }
#     st.title("Brain Cubes Visualization Test")
#     render_brain_cubes(sample_data_percentages)

#     st.write("---")
#     st.write("Example with different percentages:")
#     sample_data_percentages_2 = {
#         'Creative': 10,
#         'Business': 50,
#         'Planning': 20,
#         'Documentation': 20
#     }
#     render_brain_cubes(sample_data_percentages_2)

#     st.write("---")
#     st.write("Example with counts instead of percentages (should normalize):")
#     sample_data_counts = {
#         'Creative': 20,
#         'Business': 30,
#         'Personal': 5
#     }
#     render_brain_cubes(sample_data_counts)

#     st.write("---")
#     st.write("Example with no data:")
#     render_brain_cubes({})
