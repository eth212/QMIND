import pandas as pd
import numpy as np
import time
from collections import Counter

data = pd.read_excel("../tractor_data.xlsx")

# Count the number of nulls in the engine col:
engine_col = data["Engine"]
engine_np = np.array(engine_col.tolist())
engine_counts = Counter(engine_np)
engine_counts_sorted = engine_counts.most_common()
print(engine_counts_sorted)
print("We have 34061 unfilled columns originally")
# Get unique engine types in engine col:
engine_unique = np.array(list(engine_counts.keys()))
print(len(engine_unique))

notes_col = data["mNotes"]

engine_col_null = notes_col.isnull()
engine_col_new = np.zeros((10000,1))

t = time.time()
for i in range(0,10000):
    if(notes_col[i] == " "):
        engine_col_new[i] = False
    elif(engine_col_null[i] == True):
        engine_col_new[i] = False
    else:
        engine_col_new[i] = any(engine in notes_col[i] for engine in engine_unique)
elapsed = time.time() - t
elapsed
elapsed*10.5

sum(engine_col_new)
elapsed*10.5*6/3600
