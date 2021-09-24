import soundfile as sf
import numpy as np

threshold_amp = 0.05
min_silence_duration = 0.1
margin_duration = 0.05

for voice in range(100):
    wave, sr = sf.read(f'VOICEACTRESS100_{voice + 1:03d}.wav')
    silence = wave < threshold_amp

    left = np.arange(len(silence))
    left[silence] = 0
    np.maximum.accumulate(left, out=left)

    right = np.arange(len(silence))
    right[silence[::-1]] = 0
    np.maximum.accumulate(right, out=right)
    right = len(silence) - right[::-1] - 1

    silence_continuous = right - left + 1
    silence_continuous[np.logical_not(silence)] = 0

    silence = silence_continuous >= min_silence_duration * sr

    last_idx = 0
    while True:
        try:
            start_idx = last_idx + silence[last_idx:].tolist().index(True)
        except ValueError:
            break

        try:
            end_idx = start_idx + silence[start_idx:].tolist().index(False)
        except ValueError:
            end_idx = None
            
        if start_idx + int(margin_duration * sr) >= len(silence): start_idx = len(silence) - int(margin_duration * sr) - 1
        silence[start_idx:start_idx + int(margin_duration * sr)] = False

        if end_idx is None: break

        if end_idx - int(margin_duration * sr) < 0: end_idx = int(margin_duration * sr)
        silence[end_idx - int(margin_duration * sr): end_idx] = False

        last_idx = end_idx

    cropped_wave = wave[np.logical_not(silence)]
    sf.write(f'VOICEACTRESS100_{voice + 1:03d}.wav', cropped_wave, sr)
