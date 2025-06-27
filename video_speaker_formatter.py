# %%
import humming_bird as hb
import torch
import pandas as pd
import os
import time
import gc
torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True
def load_speaker_formatter():
    gc.collect()
    torch.cuda.empty_cache()

    if torch.cuda.is_available():
        device = "cuda"
        compute_type = "float16" if torch.cuda.get_device_capability()[0] >= 7 else "float32"
    else:
        device = "cpu"
        compute_type = "int8"

    HF_TOKEN = None
    with open('hf_token.txt') as f:
        HF_TOKEN = f.read()

    sf = hb.SpeakerFormatter(HF_TOKEN, device, compute_type)
    return sf



incr = 0
while True:

    df = pd.read_parquet('metadata.parquet')\
        .sort_values(by='upload_date', ascending=False)\
        .reset_index(drop=True)

    df_spk = None
    path_spk = 'metadata_speaker.parquet'
    if os.path.exists(path_spk):
        df_spk = pd.read_parquet(path_spk)
        df_spk = df_spk[~df_spk['lines'].isna()]

    sf = load_speaker_formatter()

    for idx, row in df.iterrows():
        if incr % 10 == 0 and incr != 0:
            del sf
            sf = load_speaker_formatter()

        print('>>>>>>>>>>>>>>>', idx, row['upload_date'])
        if df_spk is not None and row['video_id'] in set(df_spk.video_id):
            print('skip')
            continue

        incr += 1

        row_dict = row.to_dict()
        audio_path = row['audio_path']
        print(audio_path)

        try:
            lines = sf.get_audio_speaker_lines(audio_path=audio_path )
            print(lines)
            row_dict['lines'] = lines
        except:
            print('error')
            row_dict['lines'] = None

        if df_spk is None:
            df_spk = pd.DataFrame([row_dict])
        else:
            df_spk = pd.concat([df_spk, pd.DataFrame([row_dict])])
        df_spk.reset_index(drop=True).to_parquet(path_spk)

    print('Finished loop!')

# %%