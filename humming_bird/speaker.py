import whisperx
from whisperx.diarize import DiarizationPipeline
from pyannote.audio import Pipeline
import datetime
from .utils import merge_consecutive_speaker_segments

class SpeakerFormatter:
    def __init__(self, HF_TOKEN, device, compute_type):
        
        self.device = device
        self.model = whisperx.load_model("large-v2", device=device, compute_type=compute_type)
        self.diarize_model = DiarizationPipeline(use_auth_token=HF_TOKEN, device=device)
        self.diarize_model.pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token=HF_TOKEN)

    def get_audio_speaker_lines(self, audio_path: str, min_speakers=1, max_speakers=5):
        time_begin = datetime.datetime.now()
        audio = whisperx.load_audio(audio_path)
        
        ## Step 1: Transcribe
        asr_result = self.model.transcribe(audio)
                
        ## Step 2: Align for word-level timestamps
        align_model, metadata = whisperx.load_align_model(language_code=asr_result["language"], device=self.device)
        asr_result = whisperx.align(asr_result["segments"], align_model, metadata, audio, device=self.device)
        
        # Step 3: Diarization
        diarized_segments = self.diarize_model(audio, min_speakers=min_speakers, max_speakers=max_speakers)
        asr_result = whisperx.assign_word_speakers(diarized_segments, asr_result)
        time_end = datetime.datetime.now()
                
        print('Processing Time took: ', time_end - time_begin)
        
        segments = merge_consecutive_speaker_segments(asr_result['segments'])
             
        lines = []
        for idx, seg in enumerate(segments):
            line = dict(line=idx, speaker=seg['speaker'], start=seg['start'], text=seg['text'])
            lines.append(line)
        return lines