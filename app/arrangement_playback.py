"""Pure arrangement-to-pad event scheduler; positions are quarter-note beats.

A clip references a pattern id. Source offset is in beats, so trim/split/slip
preserve the musical phase. Pattern loops every 4 beats (16 sixteenth steps).
"""
import math
from pad_patterns import step_velocity

STEPS_PER_BEAT = 4
PATTERN_BEATS = 4

def velocity_hits_at(clips, patterns, beat, step_beats=0.25, excluded_steps=()):
    """Return pad/velocity pairs, keeping the strongest simultaneous clip hit.

    The caller advances at sixteenth-note boundaries. This function does not
    trigger a clip that starts halfway through a scheduler step.
    """
    result = {}
    for clip in clips:
        if clip.get('kind', 'pattern') != 'pattern':
            continue
        start = float(clip['start'])
        end = start + float(clip['length'])
        if not (start <= beat < end):
            continue
        source_beat = beat - start + float(clip.get('offset', 0))
        position = source_beat * STEPS_PER_BEAT
        if abs(position - round(position)) > 1e-6:
            continue
        step = int(round(position)) % (PATTERN_BEATS * STEPS_PER_BEAT)
        name = str(clip.get('pattern_id', 'main'))
        pattern = patterns.get(name)
        if not pattern:
            continue
        for pad, row in enumerate(pattern[:32]):
            if (name,pad,step) in excluded_steps:
                continue
            if step < len(row):
                velocity = step_velocity(row[step])
                if velocity:
                    result[pad] = max(result.get(pad, 0.), velocity)
    return sorted(result.items())


def hits_at(clips, patterns, beat, step_beats=0.25):
    """Compatibility interface for callers that only need pad indexes."""
    return [pad for pad, velocity in velocity_hits_at(clips, patterns, beat, step_beats)]


def advance(beat, loop_start, loop_end, loop_enabled=True, quantum=0.25):
    next_beat = beat + quantum
    if loop_enabled and loop_end > loop_start and next_beat >= loop_end:
        next_beat = loop_start + ((next_beat - loop_start) % (loop_end - loop_start))
    return next_beat
