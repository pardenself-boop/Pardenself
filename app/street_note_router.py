"""Pure MIDI note lifecycle for the STREET SOUND CHECK hardware test."""
class StreetNoteRouter:
    def __init__(self, on, off, panic):
        self.on, self.off, self.panic = on, off, panic
        self.held = {}  # (channel, pitch) -> instrument
        self.deferred = set()
        self.sustain = set()
    def message(self, msg, instrument=3, channel_filter=None):
        typ = getattr(msg, 'type', '')
        ch = getattr(msg, 'channel', 0)
        if channel_filter is not None and ch != channel_filter:
            return False
        key = (ch, getattr(msg, 'note', -1))
        if typ == 'control_change':
            control = getattr(msg, 'control', -1)
            if control in (120, 123):
                self.clear(); return True
            if control == 64:
                if getattr(msg, 'value', 0) >= 64:
                    self.sustain.add(ch)
                else:
                    self.sustain.discard(ch)
                    for k in list(self.deferred):
                        if k[0] == ch:
                            self._release(k)
                return True
        if typ == 'note_on' and getattr(msg, 'velocity', 0) > 0:
            pitch = key[1]
            if not 0 <= pitch <= 127: return False
            if key in self.held: self._release(key)
            self.on(pitch, min(127, max(0, msg.velocity))/127.0, instrument)
            self.held[key] = instrument
            self.deferred.discard(key)
            return True
        if typ == 'note_off' or (typ == 'note_on' and getattr(msg, 'velocity', 0) == 0):
            if key not in self.held: return False
            if ch in self.sustain:
                self.deferred.add(key)
            else:
                self._release(key)
            return True
        return False
    def _release(self, key):
        inst = self.held.pop(key, None)
        self.deferred.discard(key)
        if inst is not None: self.off(key[1], inst)
    def clear(self):
        self.held.clear(); self.deferred.clear(); self.sustain.clear()
        self.panic()
