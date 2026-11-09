"""Original short synthesized monitor clicks; no samples or device dependency."""
import math


class Metronome:
    def __init__(self):
        self.voices = []

    def trigger(self, accent=False):
        self.voices.append([0, bool(accent)])
        self.voices = self.voices[-4:]

    def clear(self):
        self.voices.clear()

    def render(self, frames, sample_rate):
        output = [0.] * frames
        length = max(1, round(sample_rate * .035))
        active = []
        for age, accent in self.voices:
            frequency, gain = (1600., .65) if accent else (1100., .45)
            count = min(frames, max(0, length-age))
            for index in range(count):
                at = age + index
                envelope = math.sin(math.pi * at / length) * math.exp(-6 * at / length)
                output[index] += math.sin(2 * math.pi * frequency * at / sample_rate) * envelope * gain
            age += frames
            if age < length:
                active.append([age, accent])
        self.voices = active
        return output
