#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
1. musicXML to midi by music21
2. key detection (Major)
3. negative harmony midi
'''
import music21, shutil, os, time, pretty_midi, datetime

def main():

    file= 'jinglebell_test.musicxml'

    ### 1. musicXML to midi (require: music21, shutil)
    midifile = musicXML_to_midi(file)

    ### 2. key detection
    original_key = detect_midi_key(midifile)

    ### 3. (Task1) Negative harmony
    cmaj_transpose_map = {'C': 0, 'CS': -1, 'D': -2, 'DS': -3, 'E': -4, 'F': -5, 'FS': -6, 'G': -7, 'GS': -8, 'A': -9, 'AS': -10, 'B': -11,}
    midi_data = pretty_midi.PrettyMIDI(midifile)
    original_bpm = int(round(midi_data.get_tempo_changes()[1][0]))
    new_midi_data = pretty_midi.PrettyMIDI(initial_tempo=original_bpm)
    for instrument in midi_data.instruments:
        nh_track = pretty_midi.Instrument(program=0, name='{0} negative harmony track'.format(instrument.name))

        original_pitchSeries = [note.pitch for note in instrument.notes]
        cmaj_pitchSereis = [p + cmaj_transpose_map[original_key] for p in original_pitchSeries]
        nh_pitchSeries = transfer_to_negative_harmony(cmaj_pitchSereis)
        transpose_to_original_key_pitchSeries = [p - cmaj_transpose_map[original_key] for p in nh_pitchSeries]
        
        # 音域
        if sum(transpose_to_original_key_pitchSeries) / len(transpose_to_original_key_pitchSeries) - sum(original_pitchSeries)/len(original_pitchSeries) > 7:
            transpose_to_original_key_pitchSeries = [x + 12 for x in transpose_to_original_key_pitchSeries]

        i = 0
        for note in instrument.notes:
            newnote = pretty_midi.Note(start=note.start, end=note.end, pitch=transpose_to_original_key_pitchSeries[i], velocity=note.velocity)
            nh_track.notes.append(newnote)
            i += 1
        new_midi_data.instruments.append(nh_track)
    nhmidifile = '{0}_negative_harmony.mid'.format(midifile.replace('.mid', ''))
    new_midi_data.write(nhmidifile)
    print('negative harmony midi generated:', nhmidifile)


def detect_midi_key(midifile):
    keymap = {
        'C':  [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1],
        'CS': [1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0],
        'D':  [0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1],
        'DS': [1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0],
        'E':  [0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1],
        'F':  [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0],
        'FS': [0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1],
        'G':  [1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1],
        'GS': [1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0],
        'A':  [0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1],
        'AS': [1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0],
        'B':  [0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1],
        # 'Am':  [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1],
        # 'ASm': [1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0],
        # 'Bm':  [0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1],
        # 'Cm': [1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0],
        # 'CSm':  [0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1],
        # 'Dm':  [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0],
        # 'DSm': [0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1],
        # 'Em':  [1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1],
        # 'Fm': [1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0],
        # 'FSm':  [0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1],
        # 'Gm': [1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0],
        # 'GSm':  [0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1],
    }
    midi_data = pretty_midi.PrettyMIDI(midifile)
    total_velocity = sum(sum(midi_data.get_chroma()))
    chroma_vector = [sum(semitone) / total_velocity for semitone in midi_data.get_chroma()]
    temp = {k: sum([chroma_vector[i]*v[i] for i in range(12)]) for k, v in keymap.items()}
    key = sorted(temp.items(), key=lambda x: x[1], reverse=True)[0][0]
    return key

def transfer_to_negative_harmony(cmaj_pitchSereis):
    #first_note_map = {0: 7, 1: 6, 2: 5, 3: 4, 4: 3, 5: 2, 6: 1, 7: 0, 8:-1, 9: -2, 10: -3, 11: -4}
    newpitchSeris = [cmaj_pitchSereis[0] + 2 * (3 - cmaj_pitchSereis[0] % 12) + 1]
    cur_note = newpitchSeris[0]
    for i in range(1, len(cmaj_pitchSereis)):
        newpitchSeris.append(cur_note - (cmaj_pitchSereis[i]-cmaj_pitchSereis[i-1]))
        cur_note = newpitchSeris[-1]

    return newpitchSeris

def musicXML_to_midi(file):

    music21temp = '/var/folders/4m/2kjny40n1rgd6fvcfv9syxg80000gn/T/music21/'
    mytemp = ''
    c = music21.converter.parse(file)
    c.show('midi')
    midifile = [x for x in os.listdir(music21temp) if '.mid' in x][0]
    time.sleep(0.5)
    transfered_midifile = file.replace('.musicxml', '').replace('.mxml', '') + datetime.datetime.now().strftime("%y%m%d%H%M%S%f") + '.mid'
    shutil.copy(os.path.join(music21temp, midifile), transfered_midifile)
    os.popen('rm {0}*'.format(music21temp))
    return transfered_midifile


if __name__ == "__main__":

    main()