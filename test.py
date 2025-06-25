# %%

import pandas as pd

df = pd.read_parquet('downloads/metadata_speaker.parquet')
# %%

df.iloc[0].lines
# %%
