#!/usr/bin/env python3

import os, sys
from glob import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.rcParams["font.size"]=14
import matplotlib.dates as mdates
import bsod_get_fieldbook
import namelist
fpath = namelist.fbook_sonde
qc_data_dir = namelist.qc_data_dir
fbook = bsod_get_fieldbook.get_fieldbook(fpath)
xctd_out_dir = namelist.output_dir

### parameter for sonde

# available variables
#'TimeUTC', 'DCnt', 'RE', 'FCnt', 'rcvFREQ', 'WM', 'WD', 'WS', 'Height',
#'Xdistanc', 'Ydistanc', 'HDP', 'PDP', 'GeodetLat', 'GeodetLon', 'V',
#'FE', 'FRT', 'FTI', 'FVH', 'FVL', 'FSP1', 'FSP2', 'FSP3', 'FSP4', 'N',
#'Prs', 'Tmp', 'Hum'
# and available calculated variables
# 'Pot': potential temperature

var_sonde = 'Tmp'

# top height of figure
top = 10000


### parameter for xctd

# available variables
#'depth', 'Temp', 'Conductivity', 'Salinity', 'Sound Velocity',
#       'Density'

var_xctd = 'Temp'

# bottom depth of figure
bottom = 1000.0  # m

# cut data to remove noise, must be integer
cut_top = 2  # m
cut_bottom = 50  # m
#################

# range of times
times = pd.date_range("2024-06-18 00", "2024-06-18 23", freq="h")

######################### no need to edit below 
# range of atmosphere height level
z_atm = np.arange(0,top,5)
# range of ocean depth level
z_ocean = np.arange(0.0,bottom,1.0)
#################

fdir = f'fig/time_seq_atm_ocean'
os.makedirs(fdir,exist_ok=True)
fig_path = f'{fdir}/{var_sonde}_{var_xctd}.png'


def calc_pot(t,p):
    k = 2/7
    return t * ((1000/p) ** k)

def check_time(launch_time,xctd=False):

    if not xctd:
        launch_time_pd = pd.to_datetime(launch_time) + pd.Timedelta(minutes=30)
    else:
        launch_time_pd = launch_time# + pd.Timedelta(minutes=30)
    nearest_00_time = launch_time_pd.round("h")
    for i,t in enumerate(times):
        if t == nearest_00_time:
            return i
    return 99999

def main_atm():

    csvs = glob(f'{qc_data_dir}/*csv')

    N = len(times)
    x = np.arange(N)
    ar = np.full((len(z_atm),N),np.nan)

    print("St. name\tJST time\tsonde No.")
    for j in range(len(fbook)):
        st_name = fbook["st_name"].iloc[j]
        launch_time = fbook["JSTtime"].iloc[j]
        sonde_no = fbook["sonde_no"].iloc[j]
        print(f"{st_name}\t{launch_time}\t{sonde_no}")

        qcdata_fpath = f"{qc_data_dir}/{st_name}.csv"
        df = pd.read_csv(qcdata_fpath, index_col=0)

        idx_t = check_time(launch_time)
        if idx_t == 99999:
            continue

        P = df['Prs'].values
        Z = df['Height'].values

        if var_sonde == "Pot":
            A = df['Tmp'].values + 273.15
            A = calc_pot(A,P)
        else:
            A = df[var_sonde].values

        Z_min = np.nanmin(Z)
        Z_max = np.nanmax(Z)
        for i,_z in enumerate(z_atm):
            idx_z = (np.abs(Z - _z)).argmin()
            if np.abs(Z[idx_z]-_z) < 5:
                ar[i,idx_t] = A[idx_z]

    # unwanted columns
    #ar[:,5] = np.nan
    #ar[:,8] = np.nan

    return ar

def main_xctd():

    csvs = glob(f'{xctd_out_dir}/*csv')

    N = len(times)
    x = np.arange(N)
    ar = np.full((len(z_ocean),N),np.nan)

    for j,file_name in enumerate(csvs):
        print("read ",file_name)

        df = pd.read_csv(file_name, index_col=0)

        base_name = os.path.basename(file_name)
        _time = base_name.split("_")[1]
        y = _time[0:4]
        m = _time[4:6]
        d = _time[6:8]
        h = _time[8:10]
        s = _time[10:12]
        launch_time = pd.to_datetime(f"{y}-{m}-{d} {h}:{s}:00")

        idx_t = check_time(launch_time,xctd=True)
        if idx_t == 99999:
            continue

        Z = df['depth'].values[cut_top:-cut_bottom]

        A = df[var_xctd].values[cut_top:-cut_bottom]

        #idx_z = [True if _z in Z else False for _z in z]
        Z_min = np.nanmin(Z)
        Z_max = np.nanmax(Z)
        #print(P_max,P_min)
        idx_0 = 0
        idx_1 = len(z_ocean)
        inner = False
        for i,_z in enumerate(z_ocean):
            if _z == Z_min:
                idx_0 = i
            if _z == Z_max:
                inner = True
                idx_1 = i + 1
                break

        if not inner:
            A = A[:idx_1-idx_0]

        ar[idx_0:idx_1,idx_t] = A

    # unwanted columns
    #ar[:,5] = np.nan
    #ar[:,8] = np.nan

    return ar

def draw_time_seq(ar_atm,ar_ocean):

    fig, axes = plt.subplots(2, 1, sharex=True)

    shade=axes[0].pcolormesh(times,z_atm,ar_atm)
    plt.colorbar(shade)

    axes[0].set_ylim([0.0,top])

    axes[0].xaxis.set_major_formatter(mdates.DateFormatter("%d-%H"))
    plt.xticks(rotation=45)

    axes[0].set_title(f"Sonde:{var_sonde} XCTD:{var_xctd}")

    shade=axes[1].pcolormesh(times,z_ocean,ar_ocean)
    plt.colorbar(shade)

    axes[1].set_ylim([bottom,0.0])

    ticks = axes[0].get_yticks()
    axes[0].set_yticks([tick for tick in ticks if tick != 0])
    ticks = axes[1].get_yticks()
    axes[1].set_yticks([tick for tick in ticks if tick != 0])

    plt.tight_layout()
    plt.subplots_adjust(hspace=0.05)
    plt.savefig(fig_path, dpi=512)

ar_air=main_atm()
ar_ocean=main_xctd()
draw_time_seq(ar_air,ar_ocean)
