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

# import os
# import tempfile
# import subprocess
# import whisper
# from concurrent.futures import ThreadPoolExecutor, as_completed


# def ffmpeg_chunk_audio(path, chunk_duration=30):
#     tmp = tempfile.mkdtemp()
#     pattern = os.path.join(tmp, "chunk_%03d.wav")

#     cmd = [
#         "ffmpeg", "-y",
#         "-i", path,
#         "-f", "segment",
#         "-segment_time", str(chunk_duration),
#         "-c:a", "pcm_s16le",
#         "-ac", "1",
#         "-ar", "16000",
#         pattern
#     ]

#     result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#     if result.returncode != 0:
#         raise RuntimeError("FFmpeg chunking failed:\n" + result.stderr.decode())

#     chunks = sorted([
#         os.path.join(tmp, x) for x in os.listdir(tmp) if x.endswith(".wav")
#     ])

#     if not chunks:
#         raise RuntimeError("No chunks created.")

#     return chunks


# def process_chunk(model, chunk_path, speed=1.35):
#     """Speed up audio + resample + transcribe silently."""
#     tmp = tempfile.mkdtemp()
#     processed = os.path.join(tmp, "processed.wav")

#     cmd = [
#         "ffmpeg", "-y",
#         "-i", chunk_path,
#         "-ac", "1",
#         "-ar", "16000",
#         "-filter:a", f"atempo={speed}",
#         processed
#     ]

#     subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

#     return model.transcribe(processed, fp16=False, verbose=False)


# def transcribe_parallel(path, workers=6, speed=1.35):
#     print("🔪 Chunking audio...")

#     chunks = ffmpeg_chunk_audio(path)
#     total = len(chunks)

#     print(f"⚡ Running {workers} workers...")

#     model = whisper.load_model("turbo")
#     results = [None] * total

#     with ThreadPoolExecutor(max_workers=workers) as ex:
#         futures = {
#             ex.submit(process_chunk, model, chunks[i], speed): i
#             for i in range(total)
#         }

#         completed = 0
#         for fut in as_completed(futures):
#             idx = futures[fut]
#             completed += 1

#             print(f"📝 Transcribing chunk {completed}/{total}...")

#             results[idx] = fut.result()

#     print("\n🎤 Final merged transcription:\n")

#     full_text = ""

#     # Whisper-style segment printing
#     for r in results:
#         for seg in r["segments"]:
#             print(f"[{seg['start']:.2f} --> {seg['end']:.2f}]  {seg['text']}")
#             full_text += seg["text"] + " "

#     return full_text.strip()


# # RUN
# output = transcribe_parallel(
#     r"C:\Users\nilax\Desktop\test\4.1 The Great Brain at the Academy.mp3",
#     workers=6,
#     speed=1.35
# )

# print("\n\n===== FINAL TEXT =====\n")
# print(output)
