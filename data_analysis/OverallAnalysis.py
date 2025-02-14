#!/usr/bin/env python
# coding: utf-8

# In[1]:


from pathlib import Path

import pandas as pd
import regex as re
from IPython.core.display_functions import display
from matplotlib.text import Text


# In[2]:


data_dir = "./exp-local/data"
info_data_dir = "./exp-local/data/info"


def import_info_data(dir, pattern):
    all_files = Path(dir).glob(pattern)
    all_data = [pd.read_csv(path, index_col=None) for path in all_files]
    return pd.concat(all_data, axis=0, ignore_index=True)


def import_data(dir):
    all_files = Path(dir).glob('data*.txt')
    all_data = [pd.read_fwf(path, skiprows=[1], index_col=None) for path in all_files]
    return pd.concat(all_data, axis=0, ignore_index=True)


data = import_data(data_dir)
energy = import_info_data(info_data_dir, 'perf.*.csv')
frequency = import_info_data(info_data_dir, 'cpu_freq_avg.*.csv')

data.JobName = data.JobName.replace('batch', method='ffill')
data = pd.merge(data, energy, on='JobName', how='left')
data = pd.merge(data, frequency, on='JobName', how='left')

data


# In[3]:


def convert_to_numeric(value):
    try:
        match = re.match(r'^([\d.]+)([KkMm])$', value)
        if match:
            numeric_part = float(match.group(1))
            multiplier = match.group(2).upper()

            if multiplier == 'K':
                return numeric_part * 1000
            elif multiplier == 'M':
                return numeric_part * 1000000

        return value
    except:
        return value


def convert_elapsed_time(elapsed_time):
    parts = elapsed_time.split('-') if '-' in elapsed_time else [0, elapsed_time]
    days = int(parts[0])
    time_parts = parts[1].split(':')
    hours = int(time_parts[0])
    minutes = int(time_parts[1])
    seconds = int(time_parts[2])
    total_seconds = days * 24 * 3600 + hours * 3600 + minutes * 60 + seconds
    return total_seconds


# In[4]:


def filter_out_completed_jobs(dat):
    dat = dat[dat.State == 'COMPLETED']
    return dat.dropna(subset=['ConsumedEnergy'])


def extract_params_from_local_file_name(dat):
    dat[['Workflow', 'mode', 'ncores', 'node', 'trial']] = dat.JobName.str.extract(
        r'(\w+)-(\w+)-nc(\d+)_(\w+?\d+)-(\d+).cfg')
    dat.ncores = dat.ncores.astype(int)
    dat.trial = dat.trial.astype(int)
    return dat


def append_job_data_columns(dat):
    for column in ['ConsumedEnergy', 'AveRSS', 'AveDiskRead', 'AveDiskWrite', 'AveVMSize', 'power_energy_pkg',
                   'power_energy_ram', 'AVG_CPU_freq_MHz']:
        dat[column] = dat[column].apply(convert_to_numeric)
        # ROUND IT TO 2 DECIMALS AFTER COMMA
        dat[f"{column}_K"] = round(dat[column] / 1000, 2)
        dat[f"{column}_M"] = round(dat[column] / 1_000_000, 2)
        dat[f"{column}_G"] = round(dat[column] / 1_000_000_000, 2)
    dat['ElapsedSeconds'] = dat.Elapsed.apply(convert_elapsed_time)
    dat['ElapsedMinutes'] = dat.ElapsedSeconds / 60
    dat['ElapsedHours'] = dat.ElapsedMinutes / 60
    return dat


# In[5]:


data = data.loc[:, ~data.columns.str.contains('Unnamed')]

data_completed = filter_out_completed_jobs(data)
data_completed = data_completed[~data_completed.JobName.str.contains("nc2")].reset_index(drop=True)

data_pending = data[data.State == "PENDING"]
data_pending = data_pending[~data_pending.JobName.str.contains("nc2")].reset_index(drop=True)

data = pd.concat([data_completed, data_pending], axis=0, ignore_index=True)
# data = data[~data.JobName.str.contains("nc2")].reset_index(drop=True)

data = extract_params_from_local_file_name(data)
data_completed = extract_params_from_local_file_name(data_completed)
data_pending = extract_params_from_local_file_name(data_pending)

data_completed = append_job_data_columns(data_completed)
data_completed = data_completed.sort_values(by=['ncores', 'Workflow'])

display(data_completed, data_pending, data)


# In[6]:


data = data.dropna(subset=['AveCPU'])

data['n_ave_cpu'] = data['AveCPU'].apply(convert_elapsed_time)
data['n_elapsed'] = data['Elapsed'].apply(convert_elapsed_time)
data['cpu_utilization'] = data['n_ave_cpu'] / data['n_elapsed']

data_completed = data_completed.dropna(subset=['AveCPU'])
data_completed['n_ave_cpu'] = data_completed['AveCPU'].apply(convert_elapsed_time)
data_completed['n_elapsed'] = data_completed['Elapsed'].apply(convert_elapsed_time)
data_completed['cpu_utilization'] = data_completed['n_ave_cpu'] / data_completed['n_elapsed']

display(data, data_completed)


# In[7]:


collected_data_stats = data_completed.groupby(['Workflow', 'mode', 'ncores', 'node']).describe().reset_index()
collected_data_stats.to_csv(
    'local_exp_overview_stats.csv', header=True)
collected_data_stats


# In[8]:


# All collected data
collected_data = data_completed.sort_values(
    by=['Workflow', "node", "ncores"]).groupby(['Workflow', 'mode', 'ncores', 'node']).agg(
    n_trials=('trial', 'count'), trials_list=('trial', lambda x: sorted(x.tolist()))).reset_index()
collected_data.to_csv('local_exp_overview.csv', index=False, header=True)
collected_data


# In[9]:


# All collected data
collected_data = data_completed.sort_values(
    by=['Workflow', "node", "ncores"]).groupby(['Workflow', 'mode', 'ncores']).agg(
    n_trials=('trial', 'count')).reset_index()
collected_data.to_csv('total_local_exp_overview.csv', index=False, header=True)
collected_data


# In[10]:


def to_local_config_class(workflow, node, trial, ncores, warmup=False):
    warmup_arg = ", True" if warmup else ""
    return f'LocalConfig("{workflow}", "{node}", {trial}, {ncores}{warmup_arg})'


def to_configs_array(x, start_idx, node):
    return f'[{to_local_config_class(x.Workflow, node if node else x.node, "trial", x.ncores)} for trial in range({start_idx}, {start_idx} + {x.trials_left_count})]'


def max_ncores(node):
    if node == 'gl2':
        return 8
    return 32


def get_configs_code_for_new_experiment(node, data_of_node, target_total_n, start_idx):
    exp_data = collected_data[(collected_data.node == data_of_node) & (
            collected_data.n_trials < target_total_n)]
    exp_data['trials_left_count'] = target_total_n - exp_data.n_trials
    exp_data['code'] = exp_data.apply(to_configs_array, axis=1, start_idx=start_idx, node=node)
    return " + ".join(exp_data.code.to_list()), to_local_config_class('dpp', node, start_idx,
                                                                      max_ncores(node), warmup=True)


# In[11]:


TOTAL_EXPERIMENTS_PER_EPOCH = 10


def get_class_name(node, epoch):
    return f"{node.upper()}_{epoch}"


def generate_class(node, epoch, target_total_n, data_of_node):
    configs, warmup_config = get_configs_code_for_new_experiment(node, data_of_node, target_total_n,
                                                                 (epoch - 1) * TOTAL_EXPERIMENTS_PER_EPOCH + 1)
    class_definition = \
        f"""
from typing import List

from examples.domain import LocalExperiment
from examples.domain.config.Config import Config
from examples.domain.config.LocalConfig import LocalConfig

class {get_class_name(node, epoch)}(LocalExperiment):
    def create_configs(self) -> List[Config]:
        return {configs}

    def create_warmup_config(self) -> Config:
        return {warmup_config}
"""
    return class_definition if configs else None


# In[12]:


# new experiment epochs
def generate_experiment_classes(exp_epochs, data_of_node: str):
    for node, epoch in exp_epochs.items():
        class_code = generate_class(node, epoch, TOTAL_EXPERIMENTS_PER_EPOCH, data_of_node)
        if class_code is None:
            continue

        file_path = f"../examples/domain/experiment/local/{get_class_name(node, epoch)}.py"
        with open(file_path, 'w') as file:
            file.write(class_code)

# generate_experiment_classes({
#     # "gl2": 3,
#     # "gl6": 3,
#     "gl5": 3
# }, data_of_node="gl6")


# In[13]:


data_completed['n_trials_completed'] = data_completed.sort_values(
    by=['Workflow', "node", "ncores"]).groupby(['Workflow', 'mode', 'ncores', 'node']).Workflow.transform('count')
data_completed['n_trials_threshold'] = data_completed['n_trials_completed'] >= 2
data_completed


# In[14]:


import matplotlib.pyplot as plt


# In[15]:


data_for_analysis = data_completed[data_completed.n_trials_threshold].reset_index(drop=True)


# In[16]:


# draw one plot containing multiple boxplots with data distribution curve for each (workflow,ncores,node) agains EnergyConsumption
fig, ax = plt.subplots(figsize=(7, 4))
data_for_analysis.boxplot(column='ElapsedSeconds', by=['Workflow', 'ncores', 'node'], ax=ax)
ax.set_xticklabels(ax.get_xticklabels(), rotation=-60, ha="left")
# save
# fig.savefig('boxplot.png')


# In[17]:


# draw two plots based on workflow containing multiple boxplots with data_for_analysis distribution curve for each (ncores,node) agains ConsumedEnergy, then 2 plots agains AveRSS, AveDiskRead, AveDiskWrite, AveVMSize. Add titles to plots with workflow name. Make sure that it is one big plot that contains all the subplots.
columns_to_plot = ['ElapsedHours', 'ConsumedEnergy_M', 'AveRSS_G', 'AveDiskRead_G', 'AveDiskWrite_G', 'AveVMSize_G',
                   'cpu_utilization', 'power_energy_pkg_M', 'power_energy_ram_K', 'AVG_CPU_freq_MHz_K']
nrows = 2
ncols = len(columns_to_plot)
fig, ax = plt.subplots(nrows=nrows, ncols=ncols, figsize=(ncols * 4, nrows * 5))
for j, workflow in enumerate(data_for_analysis.Workflow.unique()):
    for i, column in enumerate(columns_to_plot):
        data_for_analysis[data_for_analysis.Workflow == workflow].dropna(subset=column).boxplot(column=column,
                                                                                                by=['ncores', 'node'],
                                                                                                ax=ax[j, i])
        ax[j, i].set_title(f"{workflow}-{column}")
        ax[j, i].set_xticklabels(ax[j, i].get_xticklabels(), rotation=-60, ha="left")
        # next to every boxplot box show data_for_analysis distribution

fig.subplots_adjust(hspace=0.5, wspace=0.25)

fig.savefig('boxplot-overview-by-workflows.png')


# In[18]:


# draw two plots based on workflow containing multiple boxplots with data_for_analysis distribution curve for each (ncores,node) agains ConsumedEnergy, then 2 plots agains AveRSS, AveDiskRead, AveDiskWrite, AveVMSize. Add titles to plots with workflow name. Make sure that it is one big plot that contains all the subplots.
columns_to_plot = ['ElapsedHours', 'ConsumedEnergy_M', 'AveRSS_G', 'AveDiskRead_G', 'AveDiskWrite_G', 'AveVMSize_G',
                   'cpu_utilization', 'power_energy_pkg_M', 'power_energy_ram_K', 'AVG_CPU_freq_MHz_K']

title_map = {
    'ElapsedHours': 'Execution Time (h)',
    'ConsumedEnergy_M': 'Consumed Energy (MJ)',
    'AveRSS_G': 'Average Memory Utilization (GB)',
    'AveDiskRead_G': 'Average Disk Read (GB)',
    'AveDiskWrite_G': 'Average Disk Write (GB)',
    'AveVMSize_G': 'Average VM Size (GB)',
    'cpu_utilization': 'CPU Utilization (%)',
    'power_energy_pkg_M': 'Power Energy Package (MW)',
    'power_energy_ram_K': 'Power Energy RAM (KW)',
    'AVG_CPU_freq_MHz_K': 'Average vCPU Frequency (GHz)',

}

from matplotlib.text import Text

nrows = 2
ncols = len(columns_to_plot)
fig, ax = plt.subplots(nrows=nrows, ncols=ncols, figsize=(ncols * 4, nrows * 5))
for j, workflow in enumerate(data_for_analysis.Workflow.unique()):
    for i, column in enumerate(columns_to_plot):
        data_for_analysis[data_for_analysis.Workflow == workflow].dropna(subset=column).boxplot(column=column,
                                                                                                by=['ncores'],
                                                                                                ax=ax[j, i])
        ax[j, i].set_title(f"{workflow}: {title_map[column]}")
        ax[j, i].set_xlabel("Number of vCPUs")
        ax[j, i].set_ylabel(title_map[column])
        x_ticklabels = []
        for xlab in ax[j, i].get_xticklabels():
            text = (re.search(r"\((\d+).+", xlab.get_text()).group(1))
            x, y = xlab.get_position()
            x_ticklabels.append(Text(x, y, text=text))
        ax[j, i].set_xticklabels(x_ticklabels, rotation=-60, ha="left")
        # ax[j, i].set_xticklabels(ax[j, i].get_xticklabels(), rotation=-60, ha="left")

        # next to every boxplot box show data_for_analysis distribution

fig.subplots_adjust(hspace=0.5, wspace=0.25)

fig.savefig('boxplot-overview-by-workflows.no-nodes.png')


# In[19]:


# draw two plots based on workflow containing multiple boxplots with data_for_analysis distribution curve for each (ncores,node) agains ConsumedEnergy, then 2 plots agains AveRSS, AveDiskRead, AveDiskWrite, AveVMSize. Add titles to plots with workflow name. Make sure that it is one big plot that contains all the subplots.
columns_to_plot = ['ElapsedHours', 'ConsumedEnergy_M', 'AveRSS_G', 'AveDiskRead_G', 'AveDiskWrite_G', 'AveVMSize_G',
                   'cpu_utilization', 'power_energy_pkg_M', 'power_energy_ram_K', 'AVG_CPU_freq_MHz_K']
nrows = 2
ncols = len(columns_to_plot)
nrows, ncols = ncols, nrows
fig, ax = plt.subplots(nrows=nrows, ncols=ncols, figsize=(ncols * 4, nrows * 5))
for jj, workflow in enumerate(data_for_analysis.Workflow.unique()):
    for ii, column in enumerate(columns_to_plot):
        j, i = ii, jj
        data_for_analysis[data_for_analysis.Workflow == workflow].dropna(subset=column).boxplot(column=column,
                                                                                                by=['ncores'],
                                                                                                ax=ax[j, i])
        ax[j, i].set_xlabel("Number of vCPUs")
        ax[j, i].set_ylabel(title_map[column])
        ax[j, i].set_title(f"{workflow}: {title_map[column]}")
        # ax[j, i].set_xticklabels(ax[j, i].get_xticklabels(), rotation=-60, ha="left")
        x_ticklabels = []
        for xlab in ax[j, i].get_xticklabels():
            text = (re.search(r"\((\d+).+", xlab.get_text()).group(1))
            x, y = xlab.get_position()
            x_ticklabels.append(Text(x, y, text=text))
        ax[j, i].set_xticklabels(x_ticklabels, rotation=-60, ha="center")
        # next to every boxplot box show data_for_analysis distribution

fig.subplots_adjust(hspace=0.5, wspace=0.25)

fig.savefig('boxplot-overview-by-workflows.no-nodes.vert.png')


# In[20]:


import math

ncols = 3
nrows = math.ceil(len(columns_to_plot) / ncols)
fig, ax = plt.subplots(nrows=nrows, ncols=ncols, figsize=(ncols * 8, nrows * 5))
for i, column in enumerate(
        columns_to_plot):
    data_for_analysis.dropna(subset=column).boxplot(column=column, by=['Workflow', 'ncores', 'node'],
                                                    ax=ax[i // 3, i % 3])
    ax[i // 3, i % 3].set_title(column)
    ax[i // 3, i % 3].set_xticklabels(ax[i // 3, i % 3].get_xticklabels(), rotation=-60, ha="left")

if len(columns_to_plot) < ncols * nrows:
    for i in range(len(columns_to_plot), ncols * nrows):
        ax[i // 3, i % 3].axis('off')

fig.subplots_adjust(hspace=0.6)

fig.savefig('boxplot-overview.png')


# In[22]:


import math

ncols = 3
nrows = math.ceil(len(columns_to_plot) / ncols)
fig, ax = plt.subplots(nrows=nrows, ncols=ncols, figsize=(ncols * 8, nrows * 5))
for i, column in enumerate(
        columns_to_plot):
    data_for_analysis.dropna(subset=column).boxplot(column=column, by=['Workflow', 'ncores'],
                                                    ax=ax[i // 3, i % 3])
    ax[i // 3, i % 3].set_xlabel("Workflow, Number of vCPUs")
    ax[i // 3, i % 3].set_ylabel(title_map[column])
    ax[i // 3, i % 3].set_title(f"{title_map[column]}")
    x_ticklabels = []
    for xlab in ax[i // 3, i % 3].get_xticklabels():
        text = (re.search(r"\((\w+, \d+).+", xlab.get_text()).group(1))
        x, y = xlab.get_position()
        x_ticklabels.append(Text(x, y, text=text))
    ax[i // 3, i % 3].set_xticklabels(x_ticklabels, rotation=-60, ha="left")

if len(columns_to_plot) < ncols * nrows:
    for i in range(len(columns_to_plot), ncols * nrows):
        ax[i // 3, i % 3].axis('off')

fig.subplots_adjust(hspace=0.6)

fig.savefig('boxplot-overview.no-nodes.png')


# In[ ]:




