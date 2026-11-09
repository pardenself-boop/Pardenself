"""Thread-safe bridge from MIDI callback threads to the Tk main thread.

The MIDI callback must never call Tk or mutate the synth. `submit` copies the
small MIDI event into a bounded queue. `drain` runs on the GUI thread.
"""
from collections import deque
from dataclasses import dataclass
from threading import Lock


@dataclass(frozen=True)
class MidiPacket:
    """A callback snapshot tagged with the connection that produced it."""
    generation: int
    message: object


@dataclass(frozen=True)
class MidiEvent:
    device: str
    type: str
    channel: int = 0
    note: int = 0
    velocity: int = 0
    control: int = 0
    value: int = 0


class StreetMidiQueue:
    def __init__(self, dispatch, capacity=4096):
        if capacity < 2:
            raise ValueError('capacity must be >= 2')
        self.dispatch = dispatch
        self.capacity = capacity
        self._queue = deque()
        self._lock = Lock()
        self.dropped = 0
        self.overflow_panics = 0
        self._panic_pending = False

    def submit(self, device, message):
        kind = getattr(message, 'type', None)
        if kind not in ('note_on', 'note_off', 'control_change'):
            return False
        event = MidiEvent(str(device), kind,
                          getattr(message, 'channel', 0),
                          getattr(message, 'note', 0),
                          getattr(message, 'velocity', 0),
                          getattr(message, 'control', 0),
                          getattr(message, 'value', 0))
        with self._lock:
            if len(self._queue) >= self.capacity:
                # Dropped note-offs could leave voices hanging. A queued panic
                # guarantees that every active voice is released on next drain.
                self._panic_pending = True
                self._queue.clear()
                self.dropped += 1
                self.overflow_panics += 1
            self._queue.append(event)
        return True

    def drain(self, max_events=256, position=0, playing=False):
        """Call only on the DAW UI thread, e.g. via root.after(10, poll)."""
        if max_events < 1:
            raise ValueError('max_events must be positive')
        with self._lock:
            panic = self._panic_pending
            self._panic_pending = False
            events = [self._queue.popleft() for _ in range(min(max_events, len(self._queue)))]
        if panic:
            self.dispatch.panic()
        return [self.dispatch.receive(event.device, event, position, playing)
                for event in events]

    def pending(self):
        with self._lock:
            return len(self._queue)
