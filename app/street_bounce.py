"""Offline 16-bit stereo WAV bounce of TOOLBOXX's real Engine mix."""
import argparse
import math
import struct
import wave
from pathlib import Path


def bounce(engine, destination, seconds=4.0, blocksize=512):
    """Render current engine state without a sound card; prevent invalid output."""
    if not math.isfinite(seconds) or not (0 < seconds <= 600):
        raise ValueError('Bounce duration must be between 0 and 600 seconds')
    if blocksize < 1 or blocksize > 65536:
        raise ValueError('Invalid render block size')
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    total = round(seconds * engine.sr)
    peak = 0.0
    clipped = 0
    with wave.open(str(path), 'wb') as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(engine.sr)
        remaining = total
        while remaining:
            count = min(blocksize, remaining)
            samples = engine.render(count)
            if len(samples) != count:
                raise RuntimeError('Audio engine returned wrong frame count')
            pcm = bytearray()
            for sample in samples:
                if not math.isfinite(sample):
                    raise RuntimeError('Audio engine produced non-finite sample')
                peak = max(peak, abs(sample))
                if abs(sample) > 1.0:
                    clipped += 1
                sample = max(-1.0, min(1.0, sample))
                value = max(-32768, min(32767, round(sample * 32767)))
                pcm.extend(struct.pack('<hh', value, value))
            wav.writeframesraw(pcm)
            remaining -= count
    return {'file': str(path), 'frames': total, 'sample_rate': engine.sr,
            'peak': peak, 'clipped_frames': clipped}


def main():
    parser = argparse.ArgumentParser(description='BOOM BAP TOOLBOXX offline WAV bounce')
    parser.add_argument('--output', default='TOOLBOXX_BOUNCE.wav')
    parser.add_argument('--seconds', type=float, default=4.0)
    parser.add_argument('--sample', help='Optional mono/stereo 16-bit WAV to trigger on pad 1')
    args = parser.parse_args()
    from toolboxx import Engine
    engine = Engine()
    if args.sample:
        engine.load(0, args.sample)
        engine.trigger(0)
    else:
        engine.labbs.note_on(note=48, velocity=.85, labb=3, duration=.6)
    print(bounce(engine, args.output, args.seconds))


if __name__ == '__main__':
    main()
