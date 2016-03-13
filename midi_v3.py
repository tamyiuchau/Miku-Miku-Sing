import itertools
from bisect import bisect_left
import csv
import math
import mido
from time import sleep,time
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import butter, lfilter
import scipy.signal
mido.set_backend('mido.backends.rtmidi')
a="""C0	16.35	2109.89
 C#0/Db0 	17.32	1991.47
D0	18.35	1879.69
 D#0/Eb0 	19.45	1774.20
E0	20.60	1674.62
F0	21.83	1580.63
 F#0/Gb0 	23.12	1491.91
G0	24.50	1408.18
 G#0/Ab0 	25.96	1329.14
A0	27.50	1254.55
 A#0/Bb0 	29.14	1184.13
B0	30.87	1117.67
C1	32.70	1054.94
 C#1/Db1 	34.65	995.73
D1	36.71	939.85
 D#1/Eb1 	38.89	887.10
E1	41.20	837.31
F1	43.65	790.31
 F#1/Gb1 	46.25	745.96
G1	49.00	704.09
 G#1/Ab1 	51.91	664.57
A1	55.00	627.27
 A#1/Bb1 	58.27	592.07
B1	61.74	558.84
C2	65.41	527.47
 C#2/Db2 	69.30	497.87
D2	73.42	469.92
 D#2/Eb2 	77.78	443.55
E2	82.41	418.65
F2	87.31	395.16
 F#2/Gb2 	92.50	372.98
G2	98.00	352.04
 G#2/Ab2 	103.83	332.29
A2	110.00	313.64
 A#2/Bb2 	116.54	296.03
B2	123.47	279.42
C3	130.81	263.74
 C#3/Db3 	138.59	248.93
D3	146.83	234.96
 D#3/Eb3 	155.56	221.77
E3	164.81	209.33
F3	174.61	197.58
 F#3/Gb3 	185.00	186.49
G3	196.00	176.02
 G#3/Ab3 	207.65	166.14
A3	220.00	156.82
 A#3/Bb3 	233.08	148.02
B3	246.94	139.71
C4	261.63	131.87
 C#4/Db4 	277.18	124.47
D4	293.66	117.48
 D#4/Eb4 	311.13	110.89
E4	329.63	104.66
F4	349.23	98.79
 F#4/Gb4 	369.99	93.24
G4	392.00	88.01
 G#4/Ab4 	415.30	83.07
A4	440.00	78.41
 A#4/Bb4 	466.16	74.01
B4	493.88	69.85
C5	523.25	65.93
 C#5/Db5 	554.37	62.23
D5	587.33	58.74
 D#5/Eb5 	622.25	55.44
E5	659.25	52.33
F5	698.46	49.39
 F#5/Gb5 	739.99	46.62
G5	783.99	44.01
 G#5/Ab5 	830.61	41.54
A5	880.00	39.20
 A#5/Bb5 	932.33	37.00
B5	987.77	34.93
C6	1046.50	32.97
 C#6/Db6 	1108.73	31.12
D6	1174.66	29.37
 D#6/Eb6 	1244.51	27.72
E6	1318.51	26.17
F6	1396.91	24.70
 F#6/Gb6 	1479.98	23.31
G6	1567.98	22.00
 G#6/Ab6 	1661.22	20.77
A6	1760.00	19.60
 A#6/Bb6 	1864.66	18.50
B6	1975.53	17.46
C7	2093.00	16.48
 C#7/Db7 	2217.46	15.56
D7	2349.32	14.69
 D#7/Eb7 	2489.02	13.86
E7	2637.02	13.08
F7	2793.83	12.35
 F#7/Gb7 	2959.96	11.66
G7	3135.96	11.00
 G#7/Ab7 	3322.44	10.38
A7	3520.00	9.80
 A#7/Bb7 	3729.31	9.25
B7	3951.07	8.73
C8	4186.01	8.24
 C#8/Db8 	4434.92	7.78
D8	4698.63	7.34
 D#8/Eb8 	4978.03	6.93
E8	5274.04	6.54
F8	5587.65	6.17
 F#8/Gb8 	5919.91	5.83
G8	6271.93	5.50
 G#8/Ab8 	6644.88	5.19
A8	7040.00	4.90
 A#8/Bb8 	7458.62	4.63
B8	7902.13	4.37
""".split()
ref_hz=[float(i) for i in a[1::3]]
ref=a[0::3]
def pitch(hz):
    a= math.log(hz/440,2)*12+69
    if (a>0): return a
    else: return 0
def periods(t, y, threshold):
    """
    Given the input signal `y` with samples at times `t`,
    find the time periods between the times at which the
    signal `y` increases through the value `threshold`.

    `t` and `y` must be 1-D numpy arrays.
    """
    transition_times = find_transition_times(t, y, threshold)
    deltas = np.diff(transition_times)
    return deltas
def find_transition_times(t, y, threshold):
    """
    Given the input signal `y` with samples at times `t`,
    find the times where `y` increases through the value `threshold`.

    `t` and `y` must be 1-D numpy arrays.

    Linear interpolation is used to estimate the time `t` between
    samples at which the transitions occur.
    """
    # Find where y crosses the threshold (increasing).
    lower = y < threshold
    higher = y >= threshold
    transition_indices = np.where(lower[:-1] & higher[1:])[0]

    # Linearly interpolate the time values where the transition occurs.
    t0 = t[transition_indices]
    t1 = t[transition_indices + 1]
    y0 = y[transition_indices]
    y1 = y[transition_indices + 1]
    slope = (y1 - y0) / (t1 - t0)
    transition_times = t0 + (threshold - y0) / slope

    return transition_times

    
def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a
def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y
def pitch2hz(pitch):
    return 2**((round(pitch,0)-69)/12)*440
def sticky(b,fq,a,w):
    hi=pitch2hz(a)+(pitch2hz(a+1)-pitch2hz(a))*w
    low=pitch2hz(a)-(pitch2hz(a)-pitch2hz(a-1))*w
    #print(b,a,pitch2hz(a-1),hi,fq,low)
    if fq>low and fq<hi:return True
    else: return False
    
def main():
    with open('a.csv','r') as csvfile:
        reader=csv.reader(csvfile)
        flag=0
        c=0.0
        t0=0
        next(reader)
        next(reader)
        tmp=[(float(x),float(y)) for x,y,z1,z2,z3 in reader]
        timelist,pitchlist=zip(*tmp)
        a=69
        with mido.open_output('LoopBe Internal MIDI') as mid:
            #track=mido.midifiles.MidiTrack()
            #mid.tracks.append(track)
            mid.send(mido.Message('program_change',program=53,time=0.0))
            #pitchlist=butter_lowpass_filter(pitchlist,5,50,5)
            #filtered = scipy.signal.medfilt
            #pitchlist=butter_lowpass_filter(pitchlist,5,100,1)
            #pitchlist=butter_lowpass_filter(pitchlist,5,100,3)
            #if 0:
            for row in list(zip(timelist,pitchlist))[3:-15]:
                row=list(row)
                #print(row)
                b=pitch(float(row[1]))
                if b>100: continue
                if not sticky(b,float(row[1]),a,0.8):
                    if flag:
                        sleep((float(row[0])-t0)/10)
                        mid.send(mido.Message('note_off',note=round(a,0),
                                               time=float(row[0])-t0))
                    else:
                        t0=float(row[0])
                        flag=1
                    t0=float(row[0])                                 
                    #last_state=(2**((round(b,0)-69)/120)*440)
                    print(row[0],int(round(a,0)),int(round(b,0)))
                    a=round(b,0)
                    mid.send(mido.Message('note_on',note=round(b),
                                           time=float(row[0])-t0))
                    
                #timelist.append(float(row[0])-t0)
                #pitchlist.append(float(row[1]))
            #plt.plot(timelist,pitchlist)
            threshold = 0.5
            timelist=np.asarray(timelist[30:])
            pitchlist=np.asarray(pitchlist[30:])
            #deltas = periods(timelist, pitchlist, threshold)
            #print(timelist,pitchlist,deltas)
            plt.plot(timelist,pitchlist)
            #trans_times = butter_lowpass_filter(pitchlist,5,100,3)
            #print(trans_times)
            #plt.plot(timelist,trans_times,'r')
            #plt.plot(trans_times, threshold * np.ones_like(trans_times))
            plt.show()

            #mid.save('song.midi')
                      
main()

