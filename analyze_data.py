import pandas as pd

# Load dataset
df = pd.read_csv("ICRISAT-District Level Data.csv")

# Check available states and districts
print("Available States:")
print(df['State Name'].unique())
print(f"\nTotal states: {df['State Name'].nunique()}")

# Check sample districts
print("\nSample districts:")
print(df[['State Name', 'Dist Name']].drop_duplicates().head(20))

# Check yield columns
yield_columns = [col for col in df.columns if 'YIELD' in col]
print(f"\nYield columns: {yield_columns}")

# Check average yields by crop
print("\nAverage yields by crop (Kg per ha):")
for col in yield_columns:
    avg_yield = df[col].mean()
    print(f"{col}: {avg_yield:.2f}")

# Check if there's data for specific state/district combinations
print("\nChecking data for Maharashtra:")
mh_data = df[df['State Name'] == 'Maharashtra']
print(f"Maharashtra data points: {len(mh_data)}")
print(f"Maharashtra districts: {mh_data['Dist Name'].nunique()}")

# Check yields for Maharashtra
print("\nMaharashtra average yields:")
for col in yield_columns:
    if col in mh_data.columns:
        avg_yield = mh_data[col].mean()
        if not pd.isna(avg_yield) and avg_yield > 0:
            print(f"{col}: {avg_yield:.2f}")
