"""Pure arrangement-to-pad event scheduler; positions are quarter-note beats.

A clip references a pattern id. Source offset is in beats, so trim/split/slip
preserve the musical phase. Pattern loops every 4 beats (16 sixteenth steps).
"""
import math

STEPS_PER_BEAT = 4
PATTERN_BEATS = 4

def hits_at(clips, patterns, beat, step_beats=0.25):
    """Return pad indexes triggered at beat, deduplicated per simultaneous clip.

    The caller advances at sixteenth-note boundaries. This function does not
    trigger a clip that starts halfway through a scheduler step.
    """
    result = set()
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
        pattern = patterns.get(str(clip.get('pattern_id', 'main')))
        if not pattern:
            continue
        for pad, row in enumerate(pattern[:32]):
            if step < len(row) and row[step]:
                result.add(pad)
    return sorted(result)


def advance(beat, loop_start, loop_end, loop_enabled=True, quantum=0.25):
    next_beat = beat + quantum
    if loop_enabled and loop_end > loop_start and next_beat >= loop_end:
        next_beat = loop_start + ((next_beat - loop_start) % (loop_end - loop_start))
    return next_beat
