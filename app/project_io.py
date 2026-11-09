"""Project persistence with relative media references and staged session loading."""
import copy
import json
import math
import os
from pathlib import Path
import tempfile
from pad_patterns import step_velocity, PadTakes

FORMAT = 'toolboxx.project.v3'


def _relative(path, folder):
    path = Path(path).expanduser().resolve()
    try:
        return os.path.relpath(path, folder)
    except ValueError:  # Windows media can live on another drive.
        return str(path)


def _resolve(path, folder):
    if not isinstance(path, str) or not path.strip():
        raise ValueError('Invalid audio source path')
    return str((folder / Path(path).expanduser()).resolve())


def _number(value, label, minimum=0, positive=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f'Invalid {label}')
    if value < minimum or (positive and value == minimum):
        raise ValueError(f'Invalid {label}')
    return value


def snapshot(app, destination):
    folder = Path(destination).expanduser().resolve().parent
    arranger = copy.deepcopy(app.arr.serialize())
    for clip in arranger['clips']:
        if clip.get('kind') == 'audio':
            clip['path'] = _relative(clip['path'], folder)
    paths = list(app.engine.sample_paths)
    for index, sample in enumerate(app.engine.samples):
        if sample is not None and not paths[index]:
            raise ValueError(f'Pad {index + 1} has no source path; reload its WAV before saving')
    return {
        'format': FORMAT, 'version': '3.0', 'bpm': app.bpm,
        'arranger': arranger, 'pattern': copy.deepcopy(app.pattern),
        'patterns': copy.deepcopy(app.patterns), 'mapping': dict(app.mapping),
        'sample_paths': [_relative(p, folder) if p else None for p in paths],
        'labb_samples': [{'labb': i, 'path': _relative(slot[3], folder),
                          'root_note': slot[2]} for i, slot in app.labbs.crate.slots.items()],
        'suites': app.suites.serialize(), 'labbs': app.labbs.serialize(),
        'note_lane': app.notes.serialize(),
        'mix_rack': json.loads(app.engine.mix_rack.to_json()),
        'controller': app.hardware_midi.serialize() if hasattr(app, 'hardware_midi') else None,
    }


def save_project(app, destination):
    target = Path(destination).expanduser().resolve()
    payload = json.dumps(snapshot(app, target), indent=2, allow_nan=False)
    # Replace only a fully written file. Failures leave the old project intact.
    temp = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=target.parent,
                                         prefix=target.name + '.', suffix='.tmp', delete=False) as stream:
            temp = Path(stream.name)
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        temp.replace(target)
    finally:
        if temp is not None and temp.exists():
            temp.unlink()
    return target


def stage_project(source):
    """Read/validate/load all media without touching the active app or device."""
    from toolboxx import Engine
    from arranger_core import Arranger
    from note_lane import NoteLane
    from suite_registry import SuiteRouter
    from studio_midi_adapter import MidiControlRouter

    source = Path(source).expanduser().resolve()
    def reject_constant(value):
        raise ValueError(f'Non-finite JSON value: {value}')
    data = json.loads(source.read_text(encoding='utf-8'), parse_constant=reject_constant)
    if not isinstance(data, dict):
        raise ValueError('Project must be a JSON object')
    if data.get('format') not in (None, 'toolboxx.project.v2', FORMAT):
        raise ValueError('Unsupported project format')
    bpm = _number(data.get('bpm'), 'tempo', positive=True)
    patterns = data.get('patterns')
    if patterns is None:
        patterns = {'main': data.get('pattern')}
    if not isinstance(patterns, dict) or not patterns:
        raise ValueError('Project must contain pad patterns')
    for name, pattern in patterns.items():
        if not isinstance(pattern, list) or len(pattern) != 32:
            raise ValueError(f'Pattern {name} must have 32 pads')
        for row in pattern:
            if not isinstance(row, list) or len(row) != 16:
                raise ValueError(f'Pattern {name} must contain 16 steps per pad')
            for value in row:step_velocity(value)
    fallback = data.get('pattern', next(iter(patterns.values())))
    pattern = patterns.get('main', fallback)
    if pattern not in patterns.values():
        raise ValueError('Active pattern is not part of the project')
    mapping = data.get('mapping', {})
    if not isinstance(mapping, dict) or any(not isinstance(v, str) for v in mapping.values()):
        raise ValueError('Invalid MIDI mapping')
    arr_data = data.get('arranger', {'clips': data.get('clips', [])})
    if not isinstance(arr_data, dict) or not isinstance(arr_data.get('clips', []), list):
        raise ValueError('Invalid arrangement')
    for clip in arr_data.get('clips', []):
        if not isinstance(clip, dict):
            raise ValueError('Invalid clip')
        _number(clip.get('start'), 'clip start')
        _number(clip.get('length'), 'clip length', positive=True)
        track = _number(clip.get('track'), 'clip track')
        if not isinstance(track, int):
            raise ValueError('Clip track must be an integer')
        _number(clip.get('offset', 0), 'clip offset')
        if clip.get('kind') == 'audio':
            clip['path'] = _resolve(clip.get('path'), source.parent)
    arr = Arranger()
    arr.deserialize(arr_data)
    _number(arr.loop_start, 'loop start')
    _number(arr.loop_end, 'loop end', positive=True)
    _number(arr.snap, 'snap')
    notes = NoteLane()
    notes.deserialize(data.get('note_lane', {}))
    _number(notes.quantize, 'note quantize')
    for values in notes.patterns.values():
        for note in values:
            _number(note.beat, 'note beat')
            _number(note.duration, 'note duration', positive=True)
            if not isinstance(note.pitch, int) or not 0 <= note.pitch <= 127:
                raise ValueError('Invalid note pitch')
            if not 0 <= _number(note.velocity, 'note velocity') <= 1:
                raise ValueError('Invalid note velocity')
    suites = SuiteRouter()
    suites.deserialize(data.get('suites', {}))
    controller = None
    if data.get('controller') is not None:
        controller = MidiControlRouter()
        controller.deserialize(data['controller'])
    engine = Engine()
    from mix_rack import MixRack
    engine.mix_rack=MixRack.from_json(json.dumps(data.get('mix_rack',[]),allow_nan=False))
    engine.labbs.deserialize(data.get('labbs', {}))
    paths = data.get('sample_paths', [None] * 32)
    if not isinstance(paths, list) or len(paths) != 32:
        raise ValueError('Project must have exactly 32 sample paths')
    for index, path in enumerate(paths):
        if path is not None:
            try:
                engine.load(index, _resolve(path, source.parent))
            except Exception as exc:
                raise ValueError(f'Pad {index + 1} audio could not load: {path}: {exc}') from exc
    for slot in data.get('labb_samples', []):
        engine.labbs.crate.load(slot['labb'], _resolve(slot['path'], source.parent), slot['root_note'])
    for clip in arr.clips:
        if clip.get('kind') == 'audio':
            try:
                engine.regions.preload(clip['path'])
            except Exception as exc:
                raise ValueError(f'Audio region could not load: {clip["path"]}: {exc}') from exc
    return dict(bpm=bpm, arr=arr, notes=notes, suites=suites, engine=engine,
                patterns=patterns, pattern=pattern, mapping=mapping, controller=controller,
                legacy_media='sample_paths' not in data)


def load_project(app, source):
    staged = stage_project(source)
    # GUI calls this on its main thread. Staging failures leave playback untouched.
    if hasattr(app, 'street_dispatch'):
        app.street_dispatch.panic()
    if hasattr(app, '_drain_midi'):
        app._drain_midi(2048)
    app.hardware_learn = None
    app.learn = None
    app.playing = False
    app.recording = False
    if app.tick_id:
        app.root.after_cancel(app.tick_id)
        app.tick_id = None
    with app.engine.lock:
        app.engine.voices = []
        app.engine.samples = staged['engine'].samples
        app.engine.sample_paths = staged['engine'].sample_paths
        app.engine.regions = staged['engine'].regions
        app.engine.mix_rack=staged['engine'].mix_rack
        app.mix_rack=app.engine.mix_rack
        app.engine.labbs = staged['engine'].labbs
        app.labbs = app.engine.labbs
        app.arr = staged['arr']
        from arranger_ranges import RangeEditor
        app.range_editor = RangeEditor(app.arr)
        app.clips = app.arr.clips
        app.notes = staged['notes']
        app.suites = staged['suites']
        app.bpm = staged['bpm']
        app.patterns = staged['patterns']
        app.pattern = staged['pattern']
        app.pad_takes = PadTakes()
        app._tick_started = None
        app._pad_skip_once = {}
        app.mapping = staged['mapping']
        if staged['controller'] is not None:
            if hasattr(app, 'hardware_midi'):
                app.hardware_midi.deserialize(staged['controller'].serialize())
            else:
                app.hardware_midi = staged['controller']
        app.selected_clip = 0
        app.playhead = 0
        app.step = 0
    if hasattr(app, 'cookup_window'):
        app.cookup_window.macro = app.labbs.orbs
    return staged['legacy_media']
