import whisper
import subprocess
import tempfile
import os
import time

def transcribe_fast(audio_path, speed=1.35):
    print("start")
    start_transcribe = time.time()

    # Step 1: Prep temp location
    tmp = tempfile.mkdtemp()
    processed = os.path.join(tmp, "processed.wav")

    # FIX: Use a safe FFmpeg command (no quotes inside quotes)
    cmd = [
        "ffmpeg",
        "-y",
        "-i", audio_path,
        "-ac", "1",
        "-ar", "16000",
        "-filter:a", f"atempo={speed}",
        processed
    ]

    # Run FFmpeg and print errors if any
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if result.returncode != 0:
        print("\n❌ FFmpeg Error:")
        print(result.stderr.decode())
        raise RuntimeError("FFmpeg failed while preprocessing.")

    # Ensure file exists
    if not os.path.exists(processed):
        raise FileNotFoundError(f"Processed file not created: {processed}")

    # Step 2: Load Whisper turbo
    model = whisper.load_model("turbo")


    # Step 3: Transcribe
    print("time to transcribe:")
    start_time = time.time()
    result = model.transcribe(processed, fp16=False, verbose=True)
    end_time = time.time()
    print(f"Transcription took {end_time - start_time:.2f} seconds")

    end_transcribe = time.time()
    print(f"total time took {end_transcribe - start_transcribe:.2f} seconds")

    # returns the full result dict
    return result["text"]