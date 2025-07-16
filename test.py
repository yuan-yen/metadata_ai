# %%

import pandas as pd

df = pd.read_parquet('metadata_speaker.parquet')
df = df[~df['lines'].isna()]
df
# %%
df
# %%

df = pd.read_parquet('metadata_speaker.parquet')
df
# %%
