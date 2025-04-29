import pandas as pd
import sys

def test_aco2():
    print("=== Running ACO2 Gene Test ===")
    
    # Step 1: Check if ACO2 exists in mu_data columns
    print("\nStep 1: Checking mu_data for ACO2")
    try:
        mu_cols = pd.read_csv("modified_mu_jg.csv", nrows=1).columns.tolist()
        print(f"Total columns in mu_data: {len(mu_cols)}")
        print(f"First few columns: {mu_cols[:5]}")
        print(f"Last few columns: {mu_cols[-5:]}")
        
        # Check for exact match of ACO2
        has_aco2 = "ACO2" in mu_cols
        print(f"Has exact match for 'ACO2': {has_aco2}")
        
        # Check for case-insensitive match
        aco2_variants = [col for col in mu_cols if col.upper() == "ACO2"]
        if aco2_variants:
            print(f"Found case variants: {aco2_variants}")
        
        # If not found, show similar columns
        if not has_aco2 and not aco2_variants:
            similar_cols = [col for col in mu_cols if "ACO" in col]
            print(f"Similar columns containing 'ACO': {similar_cols}")
    except Exception as e:
        print(f"Error reading mu_data: {str(e)}")
    
    # Step 2: Try to load ACO2 data
    print("\nStep 2: Trying to load ACO2 data")
    try:
        # Try with exact case match first
        if "ACO2" in mu_cols:
            aco2_data = pd.read_csv("modified_mu_jg.csv", usecols=["design", "ACO2", "size", "group"])
            print("Successfully loaded ACO2 data with exact match")
            print(f"Sample data:\n{aco2_data.head()}")
        elif aco2_variants:
            # If we found a case variant, use that
            variant = aco2_variants[0]
            aco2_data = pd.read_csv("modified_mu_jg.csv", usecols=["design", variant, "size", "group"])
            print(f"Successfully loaded ACO2 data using variant '{variant}'")
            print(f"Sample data:\n{aco2_data.head()}")
        else:
            print("Could not find ACO2 in any form in the data")
    except Exception as e:
        print(f"Error loading ACO2 data: {str(e)}")
    
    # Step 3: Check sgRNA mapping for ACO2
    print("\nStep 3: Checking sgRNA mapping for ACO2")
    try:
        phi_cols = pd.read_csv("modified_phi_ig.csv", nrows=1).columns.tolist()
        print(f"Total columns in phi_data: {len(phi_cols)}")
        
        # Extract sgRNA columns
        sgrna_cols = phi_cols[1:-2]
        
        # Extract gene names from sgRNA columns (everything before the underscore)
        sgrna_genes = [col.split('_')[0] if '_' in col else col for col in sgrna_cols]
        
        # Check for ACO2
        aco2_sgrnas = [col for i, col in enumerate(sgrna_cols) 
                       if sgrna_genes[i] == "ACO2" or sgrna_genes[i].upper() == "ACO2"]
        
        print(f"Found {len(aco2_sgrnas)} sgRNAs for ACO2")
        if aco2_sgrnas:
            print(f"First few sgRNAs: {aco2_sgrnas[:3]}")
        else:
            # Check for similar gene names
            similar_genes = set([g for g in sgrna_genes if "ACO" in g])
            if similar_genes:
                print(f"Found similar genes in sgRNAs: {similar_genes}")
    except Exception as e:
        print(f"Error checking sgRNA mapping: {str(e)}")
        
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_aco2()
    
    # Try to provide a fix recommendation
    print("\n=== Recommendations ===")
    print("1. If ACO2 exists with a different case (e.g., 'Aco2'), update your app to use case-insensitive matching")
    print("2. If ACO2 exists but with a different name format, check the exact format in your data and use it")
    print("3. If ACO2 exists in mu_data but not in sgRNA mapping, the phi data visualization might be empty")