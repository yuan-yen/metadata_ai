import os
from pydub import AudioSegment

def merge_consecutive_speaker_segments(segments):
    if not segments:
        return []

    for seg in segments:
        if 'speaker' not in seg:
            seg['speaker'] = 'Unidentified SPEAKER'

    merged = []
    current = segments[0].copy()

    for seg in segments[1:]:
        if seg['speaker'] == current['speaker']:
            # Merge text and update end time
            current['text'] += ' ' + seg['text']
            current['end'] = seg['end']
        else:
            # Push current to merged and reset current
            merged.append(current)
            current = seg.copy()

    # Append the last segment
    merged.append(current)
    return merged


def segment_audio(input, output, segments):
    # 建立輸出資料夾（包括 nested folders）
    os.makedirs(output, exist_ok=True)

    # 載入音訊檔
    audio = AudioSegment.from_file(input)

    filepath_list = []
    for idx, seg in enumerate(segments):
        start_ms = int(seg['start'] * 1000)  # pydub 使用毫秒
        end_ms = int(seg['end'] * 1000)
        segment_audio = audio[start_ms:end_ms]

        # 組成輸出檔案名稱
        filename = f"{idx+1:04d}_start={seg['start']:.2f}_end={seg['end']:.2f}_{seg['speaker']}.wav"
        filepath = os.path.join(output, filename)

        # 匯出音訊切片為 .wav 格式
        segment_audio.export(filepath, format="wav")
        print(f"Saved: {filepath}")
        seg['filepath'] = filepath

    return segments