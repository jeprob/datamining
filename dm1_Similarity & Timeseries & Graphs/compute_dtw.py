"""
Homework  : Similarity measures on sets
Course    : Data Mining (636-0018-00L)
Student: Jennifer Probst (16-703-423)

Compute all pairwise DTW and Euclidean distances of time-series within
and between groups.
"""
# Author: Xiao He <xiao.he@bsse.ethz.ch>
# Author: Bastian Rieck <bastian.rieck@bsse.ethz.ch>

import os
import sys
import argparse
import numpy as np
import math


def manhattan_distance(x, y):
    
    return np.sum(np.abs(x-y))


def constrained_dtw(x, y, w):
    """
    x,y two time series
    w user defined hyperparameter
    """
    n=len(x)
    m=len(y)
    distmat = np.full((n+1,m+1), math.inf)
    distmat[0,0] = 0
    for i in range(1,n+1):
        for j in range(1, m+1):
            #constrained
            if np.abs(i-j)>w:
                continue
            #dynamic time warping step
            distmat[i,j] = manhattan_distance(x[i-1],y[j-1]) + min(distmat[i,j-1], distmat[i-1,j], distmat[i-1,j-1])
            
    return distmat[n,m]

v1 = np.array([2,2])
v2 = np.array([2,2,2])
constrained_dtw(v1,v2, 10)

#%%

if __name__ == '__main__':

    # Set up the parsing of command-line arguments
    parser = argparse.ArgumentParser(
        description="Compute distance functions on time-series"
    )
    parser.add_argument(
        "--datadir",
        required=True,
        help="Path to input directory containing file EGC200_TRAIN.txt"
    )
    parser.add_argument(
        "--outdir",
        required=True,
        help="Path to directory where timeseries_output.txt will be created"
    )

    args = parser.parse_args()

    # Set the paths
    data_dir = args.datadir
    out_dir = args.outdir

    os.makedirs(args.outdir, exist_ok=True)

    # Read the file
    data = np.loadtxt("{}/{}".format(args.datadir, 'ECG200_TRAIN.txt'),
                      delimiter=',')

    # Create the output file
    try:
        file_name = "{}/timeseries_output.txt".format(args.outdir)
        f_out = open(file_name, 'w')
    except IOError:
        print("Output file {} cannot be created".format(file_name))
        sys.exit(1)

    cdict = {}
    cdict['abnormal'] = -1
    cdict['normal'] = 1
    lst_group = ['abnormal', 'normal']
    w_vals = [0, 10, 25, float('inf')]

    # Write header for output file
    f_out.write('{}\t{}\t{}\n'.format(
        'Pair of classes',
        'Manhattan',
        '\t'.join(['DTW, w = {}'.format(w) for w in w_vals])))

    # Iterate through all combinations of pairs
    for idx_g1 in range(len(lst_group)):
        for idx_g2 in range(idx_g1, len(lst_group)):
            # Get the group data
            group1 = data[data[:, 0] == cdict[lst_group[idx_g1]]]
            group2 = data[data[:, 0] == cdict[lst_group[idx_g2]]]

            # Get average similarity
            count = 0
            vec_sim = np.zeros(1 + len(w_vals), dtype=float)
            for x in group1[:, 1:]:
                for y in group2[:, 1:]:
                    # Skip redundant calculations
                    if idx_g1 == idx_g2 and (x == y).all():
                        continue
                    
                    vec_sim[0] += manhattan_distance(x, y)

                    # Compute DTW distance for all values of hyperparameter w
                    for i, w in enumerate(w_vals):
                        vec_sim[i + 1] += constrained_dtw(x, y, w)

                    count += 1
            vec_sim /= count

            # Transform the vector of distances to a string
            str_sim = '\t'.join('{0:.2f}'.format(x) for x in vec_sim)

            # Save the output
            f_out.write(
                '{}:{}\t{}\n'.format(
                    lst_group[idx_g1], lst_group[idx_g2], str_sim)
            )
    f_out.close()