#!/usr/bin/env python

import os
import numpy as np
import pandas as pd
from colorama import init, Fore

import trajectory_utils
import associate_timestamps as associ

init(autoreset=True)


def load_estimate_and_associate(fn_gt, 
                                fn_es, fn_matches, data_gt=None,
                                max_diff=0.02,
                                start_t_sec=-float('inf'),
                                end_t_sec=float('inf')):
    matches = np.array([])
    if os.path.exists(fn_matches):
        matches = np.loadtxt(fn_matches, dtype=int)
    if matches.size > 0:
        print(Fore.YELLOW +
              "Loaded exsiting matching results {0}.".format(fn_matches))
    else:

        # matches = associ.read_files_and_associate(fn_es, fn_gt,  -10.48*10e9, 2*10e9)
        matches = associ.read_files_and_associate(fn_es, fn_gt, 0.0, max_diff)
        np.savetxt(fn_matches, np.array(matches, dtype=int), fmt='%d')
        print(Fore.YELLOW +
              "Saved matching results to {0}.".format(fn_matches))

    dict_matches = dict(matches)

    data_es = np.loadtxt(fn_es, delimiter=",", dtype=float, usecols=range(8))

    if data_gt is None:
        data_gt = np.loadtxt(fn_gt)

    p_es_all = []
    p_es = []
    p_gt = []
    q_es = []
    q_gt = []
    t_gt = []
    for es_id, es in enumerate(data_es):
        p_es_all.append(es[1:4])
        if es_id in dict_matches:
            gt = data_gt[dict_matches[es_id]]
            if gt[0] < start_t_sec or gt[0] > end_t_sec:
                continue
            t_gt.append(gt[0])    
            p_es.append(es[1:4])
            p_gt.append(gt[1:4])
            q_es.append(es[4:8])
            q_gt.append(gt[4:8])
    p_es = np.array(p_es)
    p_gt = np.array(p_gt)
    q_es = np.array(q_es)
    q_gt = np.array(q_gt)
    t_gt = np.array(t_gt)

    p_es_all = np.array(p_es_all)

    return t_gt, p_es, q_es, t_gt, p_gt, q_gt, p_es_all


def load_stamped_dataset(results_dir,
                         gt_dir,
                         nm_gt='stamped_groundtruth.txt',
                         nm_est='stamped_traj_estimate.txt',
                         nm_matches='stamped_est_gt_matches.txt',
                         max_diff=0.02,
                         start_t_sec=-float('inf'),
                         end_t_sec=float('inf')):
    '''
    read synchronized estimation and groundtruth and associate the timestamps
    '''
    fn_gt = os.path.join(gt_dir, nm_gt)

    data_gt = np.loadtxt(fn_gt, delimiter=",", dtype=float)

    fn_es = os.path.join(results_dir, nm_est)
    fn_matches = os.path.join(results_dir, nm_matches)

    return load_estimate_and_associate(
        fn_gt, fn_es, fn_matches, data_gt, max_diff, start_t_sec, end_t_sec)


def load_raw_groundtruth(results_dir, nm_gt ='stamped_groundtruth.txt',
                         start_t_sec=-float('inf'), end_t_sec=float('inf')):
    fn_gt = os.path.join(results_dir, nm_gt)

    data_gt = np.loadtxt(fn_gt, delimiter=",", dtype=float)

    t_gt = []
    p_gt = []
    q_gt = []
    for d in data_gt:
        if d[0] < start_t_sec or d[0] > end_t_sec:
            continue
        t_gt.append(d[0])    
        p_gt.append(d[1:4])
        q_gt.append(d[4:8])
    t_gt = np.array(t_gt)
    p_gt = np.array(p_gt)
    q_gt = np.array(q_gt)

    return t_gt, p_gt, q_gt

def load_system_logs(results_dir,
                    nm_file_cpu='log_cpu.csv',
                    nm_file_mem='log_mem.csv'):

    fn_cpu = os.path.join(results_dir, nm_file_cpu)
    data_cpu = pd.read_csv(fn_cpu, delimiter=",", dtype=float, usecols=[1,2,3])

    fn_mem = os.path.join(results_dir, nm_file_mem)
    data_mem = np.loadtxt(fn_mem, delimiter=",", dtype=float, skiprows=1)

    proc_names = np.loadtxt(fn_mem, delimiter=",", dtype=str, max_rows=1)

    return data_cpu, data_mem, proc_names

def load_freq(results_dir, nm_timestamps):
    fn_es = os.path.join(results_dir, nm_timestamps)
    # extract timestamps from file 
    time_es = np.loadtxt(fn_es, delimiter=",", dtype=float, usecols=range(1))
    # calc freq based on timestamps
    freq_es = []
    for es_id, time in enumerate(time_es):
        # skip first data because we need the time difference 
        if (es_id == 0):
            continue
        freq_es.append(10e8*(1/(time_es[es_id] - time_es[es_id-1])))

    return freq_es, time_es

