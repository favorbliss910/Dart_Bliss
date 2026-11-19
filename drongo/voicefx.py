"""Match the reference narrator's delivery: +2 semitones, bright close-mic EQ, compression."""
import numpy as np, soundfile as sf, librosa
from scipy.signal import butter, sosfilt
y, sr = sf.read('voice.wav', dtype='float32')
y = librosa.effects.pitch_shift(y, sr=sr, n_steps=2.0)
y = sosfilt(butter(2, 90, 'hp', fs=sr, output='sos'), y)
# presence (~3 kHz) and air shelf
pres = sosfilt(butter(2, [2200, 4500], 'bp', fs=sr, output='sos'), y)
air = sosfilt(butter(2, 7000, 'hp', fs=sr, output='sos'), y)
y = y + 0.45 * pres + 0.25 * air
# simple RMS compressor (4:1 above -20 dBFS), then soft saturation
env = np.sqrt(np.convolve(y ** 2, np.ones(240) / 240, 'same')) + 1e-6
db = 20 * np.log10(env)
gain_db = np.where(db > -20, (-20 - db) * (1 - 1 / 4), 0)
y = y * 10 ** (gain_db / 20)
y = y / np.abs(y).max() * 0.92
sf.write('voice.wav', y.astype(np.float32), sr)
print('fx ok')
