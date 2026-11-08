"""STREET WIRETAP — MIDI input dispatch for TOOLBOXX.

Run receive() on the GUI thread, never from the device callback thread.
Per-channel sustain and MIDI panic are handled here before command mapping.
"""

class StreetMidiDispatch:
    def __init__(self, router, automation, command, note_on, note_off, parameter_change=None):
        self.router = router
        self.automation = automation
        self.command = command
        self.note_on = note_on
        self.note_off = note_off
        self.parameter_change = parameter_change or (lambda changes: None)
        self.held = set()
        self.deferred = set()
        self.sustain = set()

    def panic(self, channel=None):
        """Release every voice tracked by this dispatcher (or one channel)."""
        selected = self.held | self.deferred
        if channel is not None:
            selected = {key for key in selected if key[0] == channel}
        for _, note in sorted(selected):
            self.note_off(note)
        self.held.difference_update(selected)
        self.deferred.difference_update(selected)
        if channel is None:
            self.sustain.clear()
        else:
            self.sustain.discard(channel)
        return len(selected)

    def receive(self, device, message, position=0, playing=False):
        kind = getattr(message, 'type', None)
        result = {'commands': [], 'changes': [], 'notes': []}
        if kind not in ('note_on', 'note_off', 'control_change'):
            return result
        channel = getattr(message, 'channel', 0)
        if not isinstance(channel, int) or not 0 <= channel <= 15:
            return result
        if kind == 'control_change':
            cc = getattr(message, 'control', None)
            value = getattr(message, 'value', None)
            if not isinstance(cc, int) or not 0 <= cc <= 127 or not isinstance(value, int) or not 0 <= value <= 127:
                return result
            if cc in (120, 123):
                self.panic(channel)
                result['notes'].append(('panic', channel))
                return result
            if cc == 64:
                if value >= 64:
                    self.sustain.add(channel)
                else:
                    self.sustain.discard(channel)
                    for key in sorted(k for k in self.deferred if k[0] == channel):
                        self.note_off(key[1])
                        self.deferred.discard(key)
                        result['notes'].append(('off', key[1]))
        changes = self.automation.process(device, message, position=position, playing=playing)
        self.parameter_change(changes)
        result['changes'] = changes
        commands = self.router.translate(message)
        for action in commands:
            self.command(action)
        result['commands'] = commands
        if kind in ('note_on', 'note_off'):
            note = getattr(message, 'note', None)
            velocity = getattr(message, 'velocity', 0)
            if not isinstance(note, int) or not 0 <= note <= 127 or not isinstance(velocity, int) or not 0 <= velocity <= 127:
                return result
            # A mapped pad/button must never also play an instrument note.
            if f'note:{channel}:{note}' in self.router.bindings:
                return result
            key = (channel, note)
            if kind == 'note_off' or velocity == 0:
                self.held.discard(key)
                if channel in self.sustain:
                    self.deferred.add(key)
                else:
                    self.deferred.discard(key)
                    self.note_off(note)
                    result['notes'].append(('off', note))
            elif not commands:
                self.deferred.discard(key)
                self.held.add(key)
                self.note_on(note, velocity / 127.0)
                result['notes'].append(('on', note))
        return result
