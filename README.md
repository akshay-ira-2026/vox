# Vox: hands-free voice control that works in a noisy room

Say "open claude", "type ...", "send it", "new chat", "scratch that". No keys, no wake button.
Free, offline, runs on 2 CPU cores with no GPU (Graphics Processing Unit).

Watch: [vox_demo.mp4](vox_demo.mp4): the same noisy-room audio fed to two engines, real keystrokes, real time, no cuts.

## Results: room noise (people talking + vacuum + fan, reverberant room)

| 10 dB SNR (Signal-to-Noise Ratio) | Naive whisper | Vox v8 |
|---|---|---|
| Control commands | 7/10 | 9/10 |
| False actions | 5 | 0 |
| Dictation WER (Word Error Rate) | 0.555 | 0.13 |

| 5 dB SNR | Naive whisper | Vox v8 |
|---|---|---|
| Control commands | 9/10 | 8/10 |
| False actions | 8 | 1 |
| Dictation WER | 0.657 | 0.165 |

With GTCRN (Grouped Temporal Convolutional Recurrent Network) denoising at 10 dB: 9/10, WER 0.11, 0 false actions.

## How it works
1. Silero VAD (Voice Activity Detection) + loudness gate.
2. faster-whisper base.en int8 with word timestamps.
3. Near-speaker filter: words much quieter than the user's own level (TV, people across the room) are dropped.
4. Strict control grammar finds the skeleton (open / send / new chat / scratch) with misheard-word aliases.
5. Dictation between controls is re-decoded on raw audio by NVIDIA Parakeet TDT 0.6B v2 int8 (sherpa-onnx).

Latency: whisper ~570 ms per burst, Parakeet ~360 ms per burst. Parakeet RAM ~966 MB.

## Files
- fuse5.py: the engine entry point (returns actions with event times); strict.py, intent3.py, filt3.py, seg.py, split.py: grammar, filter, segmenter
- mix.py, bench*.py, fair.py, rescore3.py: noisy set builder and scorers
- desk.html, drive.py, rec.sh: mock desktop, xdotool keystroke driver, recording script
