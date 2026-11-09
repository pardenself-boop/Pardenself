"""Bounded MIDI activity observed on the GUI thread, without consuming messages."""
from collections import deque
import time


class MidiActivity:
    def __init__(self, limit=64):
        self.entries = deque(maxlen=limit)
        self.count = 0
        self.last_received = None

    def record(self, message):
        kind = getattr(message, 'type', '')
        if kind not in ('note_on', 'note_off', 'control_change'):
            return False
        channel = getattr(message, 'channel', None)
        number = getattr(message, 'control' if kind == 'control_change' else 'note', None)
        value = getattr(message, 'value' if kind == 'control_change' else 'velocity', None)
        if type(channel) is not int or not 0 <= channel <= 15:
            return False
        if any(type(v) is not int or not 0 <= v <= 127 for v in (number, value)):
            return False
        self.count += 1
        self.last_received = time.monotonic()
        text = f'CH {channel+1:02}  ' + (f'CC {number:03}  VALUE {value:03}' if kind == 'control_change' else f'{kind.upper():8}  NOTE {number:03}  VEL {value:03}')
        self.entries.append(text)
        return True
