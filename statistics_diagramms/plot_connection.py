import networkx as nx
import matplotlib.pyplot as plt
import polars as pl
import numpy as np

df = pl.read_parquet("../data/statistic/reactions_compounds_list.csv")

# Filter out rows with empty lists
df_filtered = df.filter((pl.col("starting_compounds").list.len() > 0) & (pl.col("predicted_compounds").list.len() > 0))

# Ensure both columns have matching element counts
df_exploded = df_filtered.explode(['starting_compounds']).explode(['predicted_compounds'])

# Create a directed graph
G = nx.DiGraph()

# Convert the DataFrame to a list of dictionaries
rows = df_exploded.to_dicts()

# Add edges to the graph
for row in rows:
        starting_compound = row['starting_compounds']
        predicted_compound = row['predicted_compounds']
        G.add_edge(starting_compound, predicted_compound)

# Draw the graph
plt.figure(figsize=(12, 8))
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, node_size=3000, node_color="skyblue", font_size=10, font_color="black", font_weight="bold", edge_color="gray")
plt.title('Compound Prediction Network')
plt.savefig('compound_prediction_network.png', format='png', bbox_inches='tight')

# Optionally, close the plot to free up memory
plt.close()

