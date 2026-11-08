"""Beat-range editing shared by mouse, controller commands and software displays."""
import copy
import math


class RangeEditor:
    def __init__(self, arranger):
        self.arr = arranger
        self.track_range = (arranger.focus_track, arranger.focus_track)
        self.clipboard = None

    def scope_tracks(self):
        if self.arr.mode == 'ARR':
            return None
        if self.arr.mode == 'TRK':
            return {self.arr.focus_track}
        lo, hi = sorted(self.track_range)
        return set(range(lo, hi + 1))

    def set_range(self, start, end, track0=None, track1=None):
        if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in (start, end)):
            raise ValueError('Range endpoints must be finite beats')
        start, end = sorted((max(0., self.arr.quant(start)), max(0., self.arr.quant(end))))
        if end <= start:
            end = start + (self.arr.snap or .25)
        self.arr.loop_start, self.arr.loop_end = start, end
        if track0 is not None:
            a, b = int(track0), int(track0 if track1 is None else track1)
            self.track_range = (max(0, min(a, b)), max(0, max(a, b)))
            self.arr.focus_track = max(0, a)
        self.select()

    def select(self):
        tracks = self.scope_tracks()
        start, end = self.arr.loop_start, self.arr.loop_end
        ids = [c['id'] for c in self.arr.clips if (tracks is None or c['track'] in tracks)
               and c['start'] < end and c['start'] + c['length'] > start]
        # Selection must not change the focused track or MRQ scope.
        self.arr.selected = set(ids)
        return ids

    @staticmethod
    def _piece(clip,left,right):
        part=copy.deepcopy(clip)
        part.update(start=left,length=right-left,offset=clip.get('offset',0.)+left-clip['start'])
        if clip.get('kind')=='audio':
            part['envelope_offset']=clip.get('envelope_offset',0.)+left-clip['start']
            part['envelope_length']=clip.get('envelope_length',clip['length'])
        return part

    def _segments(self):
        tracks = self.scope_tracks()
        start, end = self.arr.loop_start, self.arr.loop_end
        segments = []
        for clip in self.arr.clips:
            if tracks is not None and clip['track'] not in tracks:
                continue
            left, right = max(start, clip['start']), min(end, clip['start'] + clip['length'])
            if right <= left:
                continue
            part = self._piece(clip,left,right)
            part['start']=left-start
            segments.append(part)
        return segments

    def copy(self):
        self.clipboard = {'length': self.arr.loop_end-self.arr.loop_start,
                          'clips': self._segments(), 'tracks': self.scope_tracks()}
        return len(self.clipboard['clips'])

    def _remove(self):
        tracks = self.scope_tracks()
        start, end = self.arr.loop_start, self.arr.loop_end
        kept = []
        for clip in self.arr.clips:
            left, right = clip['start'], clip['start']+clip['length']
            if (tracks is not None and clip['track'] not in tracks) or right <= start or left >= end:
                kept.append(clip)
                continue
            if left < start:
                part = self._piece(clip,left,start); kept.append(part)
            if right > end:
                part = self._piece(clip,end,right)
                if left < start:
                    part['id'] = self.arr._id()
                part.update(start=end, length=right-end, offset=clip.get('offset', 0.)+end-left)
                kept.append(part)
        self.arr.clips = kept
        self.arr.selected.clear()

    def delete(self, cut=False):
        count = len(self._segments())
        if cut:
            self.copy()
        if not count:
            return 0
        self.arr.checkpoint()
        self._remove()
        return count

    def _paste(self, at):
        ids = []
        for clip in self.clipboard['clips']:
            part = copy.deepcopy(clip)
            part.update(id=self.arr._id(), start=at+clip['start'])
            self.arr.clips.append(part); ids.append(part['id'])
        self.arr.selected = set(ids)
        return ids

    def paste(self, at):
        if not self.clipboard or not self.clipboard['clips']:
            return []
        if not isinstance(at, (int, float)) or not math.isfinite(at):
            raise ValueError('Paste position must be finite')
        at = max(0., self.arr.quant(at))
        self.arr.checkpoint()
        return self._paste(at)

    def duplicate(self, insert=False):
        self.copy()
        if not self.clipboard['clips']:
            return []
        self.arr.checkpoint()
        at = self.arr.loop_end
        length = self.clipboard['length']
        tracks = self.scope_tracks()
        if insert:
            shifted = []
            for clip in self.arr.clips:
                if tracks is not None and clip['track'] not in tracks:
                    shifted.append(clip); continue
                left, right = clip['start'], clip['start']+clip['length']
                if left >= at:
                    part=copy.deepcopy(clip);part['start']+=length;shifted.append(part)
                elif right > at:
                    before=self._piece(clip,left,at);shifted.append(before)
                    after=self._piece(clip,at,right);after.update(id=self.arr._id(),start=at+length);shifted.append(after)
                else:
                    shifted.append(clip)
            self.arr.clips=shifted
        ids=self._paste(at)
        self.arr.loop_start=at;self.arr.loop_end=at+length
        return ids
