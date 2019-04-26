
class GrooveBuilder():
    def __init__(self, data):
        self._get_time_intervals(data)
        self._label_time_intervals()
        self._get_segments(data)

        self.groove = self.build_groove()

    def _get_time_intervals(self, data):
        self.bars = pd.DataFrame(data['bars'])
        self.beats = pd.DataFrame(data['beats'])
        self.tatums = pd.DataFrame(data['tatums'])
        self.sections = pd.DataFrame(data['sections'])

    def _label_time_intervals(self):
        beats_per_bar = int(round(self.bars.duration.mean() / self.beats.duration.mean()))
        tatums_per_beat = int(round(self.beats.duration.mean() / self.tatums.duration.mean()))

        self.sections['section'] = pd.Series(self.sections.index.values) + 1

        self.bars['bar'] = pd.Series(self.bars.index.values) + 1
        self.beats['beat'] = (pd.Series(self.beats.index.values)
                                .apply(lambda x: x % beats_per_bar) + 1)
        self.tatums['tatum'] = (pd.Series(self.tatums.index.values)
                                .apply(lambda x: x % tatums_per_beat) + 1)

    def _get_segments(self, data):
        segments = pd.DataFrame(data['segments'])
        ps_and_ts = []
        pitch_names = ['pitch_' + str(i).zfill(2) for i in range(12)]
        timbre_names = ['timbre_' + str(i).zfill(2) for i in range(12)]
        for index, row in segments.iterrows():
            p_dict = dict(zip(pitch_names, row.pitches))
            t_dict = dict(zip(timbre_names, row.timbre))
            ps_and_ts.append({**p_dict, **t_dict})        # {**dict1, **dict2} merges two dicts
        ps_and_ts = pd.DataFrame(ps_and_ts)
        ps_and_ts['start'] = segments.start
        self.segments = (segments.drop(['pitches', 'timbre'], axis=1).merge(ps_and_ts, on='start'))

    def build_groove(self):
        beats_per_bar = int(round(self.bars.duration.mean() / self.beats.duration.mean()))

        # Starting with tatums, add the count of each beat ...
        transients = pd.merge_asof(self.tatums[['start', 'tatum']], 
                                    self.beats[['start', 'beat']], 
                                    on='start')

        # ... and bar ...
        # (fillna(0) because there may be beats before first bar)
        transients = pd.merge_asof(transients, 
                                    self.bars[['start', 'bar']], 
                                    on='start').fillna(0)
        transients.bar = transients.bar.astype(int)

        # ... and section.
        transients = pd.merge_asof(transients, 
                                    self.sections[['start', 'section']], 
                                    on='start')

        # Fix beat numbering in case of anacrusis (1 or more beats before first complete bar)
        first_bar = transients[transients['bar']==1].index[0]
        beat_offset = transients.beat[first_bar]
        transients.beat = (transients.beat - beat_offset) % beats_per_bar + 1

        # Finally, annotate all of our segments (sound) features with the
        # timing counts from our sections, bars, beats, and tatums.
        transients = pd.merge_asof(transients, 
                                    self.segments, 
                                    on='start')

        # housekeeping
        transients = transients[transients.duration.diff() != 0] # remove duplicates
        transients = transients[transients.loudness_max > -40]

        # formatting
        transients.rename(columns={'start':'time', 'loudness_max_time':'attack'}, inplace=True)
        cols = ['section', 'bar', 'beat', 'tatum', 
                'time', 'duration',
                'loudness_start', 'loudness_max', 'attack', 
                'pitch_00', 'pitch_01', 'pitch_02', 'pitch_03', 'pitch_04', 'pitch_05',
                'pitch_06', 'pitch_07', 'pitch_08', 'pitch_09', 'pitch_10', 'pitch_11',
                'timbre_00', 'timbre_01', 'timbre_02', 'timbre_03', 'timbre_04', 'timbre_05', 
                'timbre_06', 'timbre_07', 'timbre_08', 'timbre_09', 'timbre_10', 'timbre_11']
        transients = transients[cols]

        return transients

