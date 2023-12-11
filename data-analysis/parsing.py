#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import regex as re


# In[2]:


data1 = pd.read_fwf('local-exp-gl2-data.txt', skiprows=[1])
data2 = pd.read_fwf('local-exp-gl6-data.txt', skiprows=[1])
data = pd.concat([data1, data2])
data


# In[3]:


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


data = data[data.State == 'COMPLETED']
data.JobName = data.JobName.replace('batch', method='ffill')
data = data.dropna(subset=['ConsumedEnergy'])
data = data.drop('Unnamed: 3', axis=1)
data = data[~data.JobName.str.contains("nc2")].reset_index(drop=True)
data[['Workflow', 'mode', 'ncores', 'node', 'trial']] = data.JobName.str.extract(
    r'(\w+)-(\w+)-nc(\d+)_(gl\d+)-(\d+).cfg')
data.ncores = data.ncores.astype(int)
data.trial = data.trial.astype(int)

for column in ['ConsumedEnergy', 'AveRSS', 'AveDiskRead', 'AveDiskWrite', 'AveVMSize']:
    data[column] = data[column].apply(convert_to_numeric)
    data[f"{column}K"] = data[column] / 1000
    data[f"{column}M"] = data[column] / 1000000

data['ElapsedSeconds'] = data.Elapsed.apply(convert_elapsed_time)
data['ElapsedMinutes'] = data.ElapsedSeconds / 60
data['ElapsedHours'] = data.ElapsedMinutes / 60

data = data.sort_values(by=['ncores', 'Workflow'])
data


# In[4]:


# All collected data
data.groupby(['Workflow', 'mode', 'ncores', 'node']).size().reset_index(name='count').sort_values(
    by=['Workflow', "node", "ncores"]).to_csv('local_exp_overview.csv', index=False, header=True)


# In[5]:


mask = (data.groupby(['Workflow', 'mode', 'ncores', 'node']).size()).reset_index(name='count')
mask['count_threshold'] = mask['count'] > 1
mask = mask[mask.count_threshold]
mask


# In[6]:


mask.drop(['count', 'count_threshold'], axis=1, inplace=True)
data = data.merge(mask, on=['Workflow', 'mode', 'ncores', 'node'], how='inner')
data


# In[7]:


import matplotlib.pyplot as plt


# In[8]:


# draw one plot containing multiple boxplots with data distribution curve for each (workflow,ncores,node) agains EnergyConsumption
fig, ax = plt.subplots(figsize=(15, 10))
data.boxplot(column='ElapsedSeconds', by=['Workflow', 'ncores', 'node'], ax=ax)
plt.show()
# save
fig.savefig('boxplot.png')


# In[9]:


# draw two plots based on workflow containing multiple boxplots with data distribution curve for each (ncores,node) agains ConsumedEnergy, then 2 plots agains AveRSS, AveDiskRead, AveDiskWrite, AveVMSize. Add titles to plots with workflow name. Make sure that it is one big plot that contains all the subplots.
fig, ax = plt.subplots(nrows=2, ncols=6, figsize=(40, 10))
for j, workflow in enumerate(data.Workflow.unique()):
    for i, column in enumerate(
            ['ElapsedHours', 'ConsumedEnergyK', 'AveRSSM', 'AveDiskReadM', 'AveDiskWriteM', 'AveVMSizeM']):
        data[data.Workflow == workflow].boxplot(column=column, by=['ncores', 'node'], ax=ax[j, i])
        ax[j, i].set_title(f"{workflow}-{column}")
        # next to every boxplot box show data distribution

fig.savefig('boxplot-overview-by-workflows.png')


# In[47]:


fig, ax = plt.subplots(nrows=2, ncols=3, figsize=(40, 20))
for i, column in enumerate(
        ['ElapsedHours', 'ConsumedEnergyK', 'AveRSSM', 'AveDiskReadM', 'AveDiskWriteM', 'AveVMSizeM']):
    data.boxplot(column=column, by=['Workflow', 'ncores', 'node'], ax=ax[i // 3, i % 3])
    ax[i // 3, i % 3].set_title(column)

fig.savefig('boxplot-overview.png')


# In[ ]:




