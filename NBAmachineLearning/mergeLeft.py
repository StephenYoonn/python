import pandas as pd
import os

def mergeOnPlayerNames():
    #merging file1 +file2 to new filename, enter with one space between
    info = input("Enter data: (file1, file2, new filename) ").split(" ")
    
    if len(info) < 3:
        print("Please provide the correct input: file1, file2, and new filename")
        return
    
    #base directory for input files
    base_dir = '../data/raw/csv/'
    
    file1_path = os.path.join(base_dir, info[0])
    file2_path = os.path.join(base_dir, info[1])
    
    #load the input files into DataFrames
    df1 = pd.read_csv(file1_path)
    #df2 = pd.read_csv(file2_path)
    df2 = pd.read_csv(file2_path,usecols=range(29))

    #df1 = df1.drop(df1.columns[0])

   # df1['Player'] = df1['Player'].astype(str)
   # df2['Player'] = df2['Player'].astype(str)
   # print(df1['Player'].head())
   # print(df2['Player'].head())
    
    #columns that are present in both df1,df2 except for the 'Player' column
    common_columns = [col for col in df1.columns if col in df2.columns and col != 'Player']
    
    #drop the common columns from the df2 to avoid duplication
    df2 = df2.drop(columns=common_columns)
    
    #left join on the 'Player' column to keep only rows where the Player exists in df1
    df_final = pd.merge(df1, df2, on='Player', how='left')
    
    output_file_path =  os.path.join(base_dir, info[2])
    df_final.to_csv(output_file_path, index=False)
    
    print(f"Merged DataFrame saved to {output_file_path}")

if __name__ == "__main__":
    mergeOnPlayerNames()
