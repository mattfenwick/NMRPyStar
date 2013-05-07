'''
Created on May 3, 2013

@author: mattf
'''
import patcher.trial as pt
import patcher.model as pmod


def old():
    q = pt.star_in('../../PeakPick/proj.star')

    old = q.spectra['nhsqc']
    q.spectra['nhsqc'] = pmod.Spectrum(old.axes, dict(filter(lambda (_,pk): 'backbone amide' not in pk.tags, old.peaks.items())))

    pt.xeasy_out(q, {'nhsqc': 'nhsqc.txt'})




import xeasy.parser as xp
import parse.conslist as pc
import parse.position as pp

def load_peaks():
    # load the peak file
    # pull out all the ids
    # write them out, 1 per line, along with the experiment id, maybe tab-separated
    path = 'poopy.xez'
    exp_id = 2
    with open(path, 'r') as infile:
        string = infile.read()
        parsed = xp.xeasy.parse(pc.ConsList.fromIterable(pp.addLineCol(string)), None)
        ids = sorted(parsed.value['result'].peaks.keys())
        for p in ids:
            print p, '\t', exp_id


def load_shifts():
    # load the peaks file
    # pull out all the peaks
    # for each peak
    #   1. write out shift 1  (peak_id, dim, shift)
    #   2. write out shift 2
    path = 'poopy.xez'
    with open(path, 'r') as infile:
        string = infile.read()
        parsed = xp.xeasy.parse(pc.ConsList.fromIterable(pp.addLineCol(string)), None)
        i = 253 # the current next number in the autoincrement sequence
        for (pid, pk) in parsed.value['result'].peaks.iteritems():
            print i, pid, 1, pk.shifts[0]
            i += 1
            print i, pid, 2, pk.shifts[1]
            i += 1
            print i, pid, 3, pk.shifts[2]
            i += 1


def spin_systems():
    hnco, nhsqc = 'hnco.xez', 'nhsqc.xez'
    n_epsilon, h_epsilon = .1, .0125
    count = 0
    ss = {}
    ssid = 10001
    with open(hnco, 'r') as in1:
        with open(nhsqc, 'r') as in2:
            h = xp.xeasy.parse(pc.ConsList.fromIterable(pp.addLineCol(in1.read())), None)
            n = xp.xeasy.parse(pc.ConsList.fromIterable(pp.addLineCol(in2.read())), None)
            for (nid, npk) in n.value['result'].peaks.iteritems():
                ss[ssid] = [nid] 
                for (hid, hpk) in h.value['result'].peaks.iteritems():
                    nn, nh = npk.shifts
                    hh, hn, hc = hpk.shifts
                    if abs(nn - hn) < n_epsilon and abs(nh - hh) < h_epsilon:
                        ss[ssid].append(hid)
                ssid += 1
            ssids = []
            assigns = []
            for (ss_id, pkids) in sorted(ss.items(), key=lambda x: x[0]):
                ssids.append(ss_id)
                for pkid in pkids:
                    assigns.append((ss_id, pkid))
            for s in ssids:
                print s
            for (ss_id_, pkid) in assigns:
                print pkid, ss_id_

spin_systems()