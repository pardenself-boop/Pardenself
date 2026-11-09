"""Velocity-aware steps and guarded undo for quantized sample-pad takes."""
import math


def step_velocity(value):
    if type(value) is bool:
        return float(value)
    if type(value) not in (int, float) or not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError('Pattern steps must be booleans or velocities between zero and one')
    return float(value)


def pattern_step(beat, clip=None):
    """Nearest sixteenth in the source pattern, including slip/trim phase."""
    source = beat if clip is None else beat - clip['start'] + clip.get('offset', 0.)
    return int(math.floor(source * 4 + .5)) % 16


def performance_beat(playhead, bpm, loop_start, loop_end, loop_enabled, now, tick_beat=None, tick_started=None):
    beat = playhead if tick_started is None else tick_beat + max(0., now-tick_started) * bpm / 60.
    if loop_enabled and loop_end > loop_start and beat >= loop_end:
        beat = loop_start + (beat-loop_start) % (loop_end-loop_start)
    return beat


class PadTakes:
    """One take per record pass; refuse undo if its cells have since changed."""
    def __init__(self):
        self.pending = {}
        self.history = []
        self.future = []

    def record(self, patterns, name, pad, step, velocity):
        velocity = step_velocity(velocity)
        if velocity == 0:
            return
        key = (name, pad, step)
        before = self.pending[key][0] if key in self.pending else patterns[name][pad][step]
        self.pending[key] = (before, velocity)
        patterns[name][pad][step] = velocity

    def finish(self):
        changes = {key: pair for key, pair in self.pending.items() if pair[0] != pair[1]}
        self.pending = {}
        if changes:
            self.history.append(changes)
            self.history = self.history[-32:]
            self.future.clear()

    def _restore(self, patterns, source, destination, before_index, after_index):
        if not source:
            return False
        changes = source[-1]
        for (name, pad, step), pair in changes.items():
            if name not in patterns or patterns[name][pad][step] != pair[before_index]:
                return False
        for (name, pad, step), pair in changes.items():
            patterns[name][pad][step] = pair[after_index]
        destination.append(source.pop())
        return True

    def undo(self, patterns):
        self.finish()
        return self._restore(patterns, self.history, self.future, 1, 0)

    def redo(self, patterns):
        self.finish()
        return self._restore(patterns, self.future, self.history, 0, 1)
