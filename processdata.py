import pandas as pd
import re

# Load the phi data
data_phi = pd.read_csv("final_merged_phi_ig_all_sizes_transposed.csv")

# Change the name of the first column to 'design'
data_phi.columns.values[0] = "design"

# Clean up gene names in column headers
# For sgRNA columns like "A1BG (1)_GGAAGTCTGGAGTCTCCAGG"
new_cols = [col if col == "design" else re.sub(r' \(\d+\)', '', col.split('_')[0]) + (('_' + '_'.join(col.split('_')[1:])) if '_' in col else '') 
           for col in data_phi.columns]
data_phi.columns = new_cols

# Extract size information from the design column
data_phi['size'] = data_phi['design'].str.extract(r'.*_size_([0-9]+).*').astype(int)

# Extract group information from the design column
data_phi['group'] = data_phi['design'].str.extract(r'Group_([0-9]+)_.*')

# View the first few rows to confirm changes
print(data_phi.head())

# Save the modified dataframe to a new CSV file
data_phi.to_csv("modified_phi_ig.csv", index=False)

# Now process the mu_jg data
data = pd.read_csv("final_merged_mu_jg_all_sizes_transposed.csv")

# Change the name of the first column to 'design'
data.columns.values[0] = "design"

# Clean up gene names in column headers
# For gene columns like "A1BG (1)"
new_cols = [col if col == "design" else re.sub(r' \(\d+\)', '', col) for col in data.columns]
data.columns = new_cols

# Extract size information from the design column
data['size'] = data['design'].str.extract(r'.*_size_([0-9]+).*').astype(int)

# Extract group information from the design column
data['group'] = data['design'].str.extract(r'Group_([0-9]+)_.*')

# View the first few rows to confirm changes
print(data.head())

# Save the modified dataframe to a new CSV file
data.to_csv("modified_mu_jg.csv", index=False)