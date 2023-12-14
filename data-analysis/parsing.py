#!/usr/bin/env python
# coding: utf-8

# In[160]:


import pandas as pd
import regex as re
from IPython.core.display_functions import display


# In[161]:


data1 = pd.read_fwf('local-exp-gl2-data.txt', skiprows=[1], index_col=None)
data2 = pd.read_fwf('local-exp-gl6-data.txt', skiprows=[1], index_col=None)
data3 = pd.read_fwf('local-exp-gl5-data.txt', skiprows=[1], index_col=None)
data4 = pd.read_fwf('local-exp-gl2_2-data.txt', skiprows=[1], index_col=None)
data = pd.concat([data1, data2, data3, data4], axis=0, ignore_index=True)
data


# In[162]:


def convert_to_numeric(value):
    match = re.match(r'^([\d.]+)([KkMm])$', value)
    if match:
        numeric_part = float(match.group(1))
        multiplier = match.group(2).upper()

        if multiplier == 'K':
            return numeric_part * 1000
        elif multiplier == 'M':
            return numeric_part * 1000000

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


# In[163]:


def filter_out_completed_jobs(dat):
    dat = dat[dat.State == 'COMPLETED']
    dat.JobName = dat.JobName.replace('batch', method='ffill')
    return dat.dropna(subset=['ConsumedEnergy'])


def extract_params_from_local_file_name(dat):
    dat[['Workflow', 'mode', 'ncores', 'node', 'trial']] = dat.JobName.str.extract(
        r'(\w+)-(\w+)-nc(\d+)_(gl\d+)-(\d+).cfg')
    dat.ncores = dat.ncores.astype(int)
    dat.trial = dat.trial.astype(int)
    return dat


def append_job_data_columns(dat):
    for column in ['ConsumedEnergy', 'AveRSS', 'AveDiskRead', 'AveDiskWrite', 'AveVMSize']:
        dat[column] = dat[column].apply(convert_to_numeric)
        dat[f"{column}K"] = dat[column] / 1000
        dat[f"{column}M"] = dat[column] / 1_000_000
        dat[f"{column}G"] = dat[column] / 1_000_000_000
    dat['ElapsedSeconds'] = dat.Elapsed.apply(convert_elapsed_time)
    dat['ElapsedMinutes'] = dat.ElapsedSeconds / 60
    dat['ElapsedHours'] = dat.ElapsedMinutes / 60
    return dat


# In[164]:


data = data.loc[:, ~data.columns.str.contains('Unnamed')]

data_completed = filter_out_completed_jobs(data)
data_completed = data_completed[~data_completed.JobName.str.contains("nc2")].reset_index(drop=True)

data_pending = data[data.State == "PENDING"]
data_pending = data_pending[~data_pending.JobName.str.contains("nc2")].reset_index(drop=True)

data = pd.concat([data_completed, data_pending], axis=0, ignore_index=True)
data = data[~data.JobName.str.contains("nc2")].reset_index(drop=True)

# data = data[~data.JobName.str.contains("nc2")].reset_index(drop=True)
data = extract_params_from_local_file_name(data)
data_completed = extract_params_from_local_file_name(data_completed)
data_pending = extract_params_from_local_file_name(data_pending)

data_completed = append_job_data_columns(data_completed)
data_completed = data_completed.sort_values(by=['ncores', 'Workflow'])

display(data_completed, data_pending, data)


# In[165]:


jobs_to_eliminate = data[data.ncores == 2]
" ".join(map(str, list(jobs_to_eliminate.JobID.to_list())))


# In[166]:


gl2_trials = data[data.node == "gl2"].sort_values(
    by=['Workflow', "node", "ncores", "trial"]).groupby(['Workflow', 'mode', 'ncores', 'node']).agg(
    # trials_count=('trial', 'count'),
    # trials_list=('trial', lambda x: x.tolist()),
    # trials_left=('trial', lambda x: list(set(range(1, 11)) - set(x.tolist()))),
    trials_left_count=('trial', lambda x: 10 - len(x.tolist())),
).reset_index()
gl2_trials


# In[167]:


gl2_trials_left = data_completed[data_completed.node == "gl2"].sort_values(
    by=['Workflow', "node", "ncores", "trial"]).groupby(['Workflow', 'mode', 'ncores', 'node']).agg(
    # trials_count=('trial', 'count'),
    # trials_list=('trial', lambda x: x.tolist()),
    # trials_left=('trial', lambda x: list(set(range(1, 11)) - set(x.tolist()))),
    trials_left_count=('trial', lambda x: 10 - len(x.tolist())),
).reset_index()
gl2_trials_left.to_csv('gl2_trials_left.csv', index=False, header=True)
gl2_trials_left


# In[168]:


gl6_trials_left = data_completed[data_completed.node == "gl6"].sort_values(
    by=['Workflow', "node", "ncores", "trial"]).groupby(['Workflow', 'mode', 'ncores', 'node']).agg(
    # trials_count=('trial', 'count'),
    # trials_list=('trial', lambda x: x.tolist()),
    # trials_left=('trial', lambda x: list(set(range(1, 11)) - set(x.tolist()))),
    trials_left_count=('trial', lambda x: 10 - len(x.tolist())),
).reset_index()
gl6_trials_left.to_csv('gl6_trials_left.csv', index=False, header=True)
gl6_trials_left


# In[169]:


# All collected data
collected_data = data_completed.groupby(['Workflow', 'mode', 'ncores', 'node']).size().reset_index(
    name='count').sort_values(
    by=['Workflow', "node", "ncores"])
collected_data.to_csv('local_exp_overview.csv', index=False, header=True)
collected_data


# In[170]:


data_completed['n_trials_completed'] = data_completed.sort_values(
    by=['Workflow', "node", "ncores"]).groupby(['Workflow', 'mode', 'ncores', 'node']).Workflow.transform('count')
data_completed['n_trials_threshold'] = data_completed['n_trials_completed'] >= 2
data_completed


# In[171]:


import matplotlib.pyplot as plt


# In[172]:


data_for_analysis = data_completed[data_completed.n_trials_threshold].reset_index(drop=True)


# In[173]:


# draw one plot containing multiple boxplots with data distribution curve for each (workflow,ncores,node) agains EnergyConsumption
fig, ax = plt.subplots(figsize=(15, 10))
data_for_analysis.boxplot(column='ElapsedSeconds', by=['Workflow', 'ncores', 'node'], ax=ax)
ax.set_xticklabels(ax.get_xticklabels(), rotation=-60)
# save
fig.savefig('boxplot.png')


# In[174]:


# draw two plots based on workflow containing multiple boxplots with data_for_analysis distribution curve for each (ncores,node) agains ConsumedEnergy, then 2 plots agains AveRSS, AveDiskRead, AveDiskWrite, AveVMSize. Add titles to plots with workflow name. Make sure that it is one big plot that contains all the subplots.
fig, ax = plt.subplots(nrows=2, ncols=6, figsize=(26, 10))
for j, workflow in enumerate(data_for_analysis.Workflow.unique()):
    for i, column in enumerate(
            ['ElapsedHours', 'ConsumedEnergyK', 'AveRSSM', 'AveDiskReadM', 'AveDiskWriteM', 'AveVMSizeM']):
        data_for_analysis[data_for_analysis.Workflow == workflow].boxplot(column=column, by=['ncores', 'node'],
                                                                          ax=ax[j, i])
        ax[j, i].set_title(f"{workflow}-{column}")
        ax[j, i].set_xticklabels(ax[j, i].get_xticklabels(), rotation=-60)
        # next to every boxplot box show data_for_analysis distribution

fig.subplots_adjust(hspace=0.5, wspace=0.25)

fig.savefig('boxplot-overview-by-workflows.png')


# In[175]:


fig, ax = plt.subplots(nrows=2, ncols=3, figsize=(26, 10))
for i, column in enumerate(
        ['ElapsedHours', 'ConsumedEnergyK', 'AveRSSM', 'AveDiskReadM', 'AveDiskWriteM', 'AveVMSizeM']):
    data_for_analysis.boxplot(column=column, by=['Workflow', 'ncores', 'node'], ax=ax[i // 3, i % 3])
    ax[i // 3, i % 3].set_title(column)
    ax[i // 3, i % 3].set_xticklabels(ax[i // 3, i % 3].get_xticklabels(), rotation=-60)

fig.subplots_adjust(hspace=0.6)

fig.savefig('boxplot-overview.png')


# In[ ]:




