# %%

import pandas as pd

df = pd.read_parquet('metadata_speaker.parquet')
df = df[~df['lines'].isna()]
df
# %%
df.to_parquet('metadata_speaker.parquet')


# %%
df = pd.read_parquet('metadata.parquet')
# %%
df
# %%
