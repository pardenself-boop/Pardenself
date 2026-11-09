"""STREET WIRETAP — MIDI input dispatch for TOOLBOXX.

Run receive() on the GUI thread, never from the device callback thread.
Per-channel sustain and MIDI panic are handled here before command mapping.
"""

class StreetMidiDispatch:
    def __init__(self, router, automation, command, note_on, note_off, parameter_change=None, pad_command=None, channel_aware=False):
        self.router = router
        self.automation = automation
        self.command = command
        self.note_on = note_on
        self.note_off = note_off
        self.parameter_change = parameter_change or (lambda changes: None)
        self.pad_command = pad_command
        self.channel_aware = channel_aware
        self.held = set()
        self.deferred = set()
        self.sustain = set()

    def release_note(self, channel, note):
        if self.channel_aware:
            self.note_off(note, channel)
        else:
            self.note_off(note)

    def play_note(self, channel, note, velocity):
        if self.channel_aware:
            self.note_on(note, velocity, channel)
        else:
            self.note_on(note, velocity)

    def panic(self, channel=None):
        """Release every voice tracked by this dispatcher (or one channel)."""
        selected = self.held | self.deferred
        if channel is not None:
            selected = {key for key in selected if key[0] == channel}
        for selected_channel, note in sorted(selected):
            self.release_note(selected_channel, note)
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
        if type(channel) is not int or not 0 <= channel <= 15:
            return result
        if kind in ('note_on', 'note_off'):
            note = getattr(message, 'note', None)
            velocity = getattr(message, 'velocity', 0)
            if type(note) is not int or not 0 <= note <= 127 or type(velocity) is not int or not 0 <= velocity <= 127:
                return result
        if kind == 'control_change':
            cc = getattr(message, 'control', None)
            value = getattr(message, 'value', None)
            if type(cc) is not int or not 0 <= cc <= 127 or type(value) is not int or not 0 <= value <= 127:
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
                        self.release_note(key[0], key[1])
                        self.deferred.discard(key)
                        result['notes'].append(('off', key[1]))
        changes = self.automation.process(device, message, position=position, playing=playing)
        self.parameter_change(changes)
        result['changes'] = changes
        commands = self.router.translate(message)
        for action in commands:
            if self.pad_command is not None and kind=='note_on' and velocity>0 and action.startswith(('PAD ', 'BANK PAD ')):
                self.pad_command(action,velocity/127.)
            else:
                self.command(action)
        result['commands'] = commands
        if kind in ('note_on', 'note_off'):
            note = getattr(message, 'note', None)
            velocity = getattr(message, 'velocity', 0)
            if not isinstance(note, int) or not 0 <= note <= 127 or not isinstance(velocity, int) or not 0 <= velocity <= 127:
                return result
            # A mapped pad/button must never also play an instrument note.
            if f'note:{channel}:{note}' in self.router.bindings:
                key=(channel,note)
                if (kind=='note_off' or velocity==0) and key in self.held | self.deferred:
                    self.held.discard(key);self.deferred.discard(key)
                    self.release_note(channel,note)
                return result
            key = (channel, note)
            if kind == 'note_off' or velocity == 0:
                self.held.discard(key)
                if channel in self.sustain:
                    self.deferred.add(key)
                else:
                    self.deferred.discard(key)
                    self.release_note(channel, note)
                    result['notes'].append(('off', note))
            elif not commands:
                self.deferred.discard(key)
                self.held.add(key)
                self.play_note(channel, note, velocity / 127.0)
                result['notes'].append(('on', note))
        return result
