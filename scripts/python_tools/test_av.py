import av
import wave

def extract_audio(video_path, audio_path):
    container = av.open(video_path)
    audio_stream = next(s for s in container.streams if s.type == 'audio')
    
    with wave.open(audio_path, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(16000)
        
        resampler = av.AudioResampler(
            format='s16', 
            layout='mono', 
            rate=16000
        )
        
        for frame in container.decode(audio_stream):
            frame.pts = None
            for resampled_frame in resampler.resample(frame):
                wav_file.writeframes(resampled_frame.planes[0].to_bytes())
                
    print("Success")

extract_audio("frontend/public/BigBuckBunny.mp4", "temp_test_audio.wav")
