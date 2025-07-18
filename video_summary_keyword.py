# %%
import humming_bird as hb
import contract_engine as ce
import pandas as pd
import os
import time

ce.setup_endor_client(
    model_name=ce.AFM_MODEL_ID_DEFAULT,
    app_id=os.getenv('CUSTOM_ENDOR_APP_ID'),
    app_password=os.getenv('CUSTOM_ENDOR_APP_PASSWORD')
)

def run_keyword_summary():
    df = pd.read_parquet('metadata_speaker.parquet')\
            .sort_values(by='upload_date', ascending=False).reset_index(drop=True)

    df = df[~df.lines.isna()]

    path_ai = 'metadata_ai_keyword_summary.parquet'
    df_ai = None
    if os.path.exists(path_ai):
        df_ai = pd.read_parquet(path_ai)

    model_selected = ce.AFM_MODEL_ID_DEFAULT

    for idx, row in df[:500].iterrows():

        if df_ai is not None and row['video_id'] in set(df_ai.video_id):
            print('skip')
            continue

        document_content = ""
        for line in row['lines']:
            context = f"line {line['line']}, {line['speaker']}: {line['text']}"    
            document_content += context

        document_content.replace("'", "").replace('"', "").replace('{', "").replace('}', "")

        print(idx, len(document_content), row['upload_date'])
        keyword_prompt = hb.KEYWORD_PROMPT_TEMPLATE.substitute(document_content = document_content)
        summary_prompt = hb.SUMMARY_PROMPT_TEMPLATE.substitute(document_content = document_content)

        row_dict = row.to_dict()

        try:
            summary_response = ce.ModelInference.complete(
                prompt=summary_prompt ,
                model_selected=model_selected,
                model_service_choice=ce.MODEL_SERVICE_CHOICE.ENDOR
            )
            print(summary_response)
        except:
            row_dict['summary'] = {'high_level_summary': "Unable to extract summary and keywords"}

        try:
            keyword_response = ce.ModelInference.complete(
                prompt=keyword_prompt ,
                model_selected=model_selected,
                model_service_choice=ce.MODEL_SERVICE_CHOICE.ENDOR
            )
            print(keyword_response)
        except:
            row_dict['keywords'] = []
            
        _keyword_response = ce.model_response_literal_eval(keyword_response)
        _summary_response = ce.model_response_literal_eval(summary_response)
        keyword_dict = dict()
        try:
            for item in _keyword_response:
                keyword_dict[item['line']] = item['keywords']
        except:
            pass
        
        unique_keywords = set()
        for item in row['lines']:
            line = None
            try: line = int(item['line'])
            except: pass

            if line is not None and line in keyword_dict:
                keywords = keyword_dict[line]
                item['keywords'] = keywords
                unique_keywords = unique_keywords.union(set(keywords))
            else:
                item['keywords'] = None
        row_dict['keywords'] = unique_keywords
        if _summary_response is not None:
            row_dict['summary'] = _summary_response
        else:
            row_dict['summary'] = dict(unstructured_summary=summary_response)

        if df_ai is None:
            df_ai = pd.DataFrame([row_dict])
        else:
            df_ai = pd.concat([df_ai, pd.DataFrame([row_dict])])

        df_ai.reset_index(drop=True).to_parquet(path_ai)

while True:
    run_keyword_summary()
    time.sleep(600)


# %%
