#!/usr/bin/env python
# coding: utf-8

# In[2]:


from pathlib import Path

import pandas as pd


# In[4]:


def import_perf_data(dir):
    all_files = Path(dir).glob('perf.*.csv')
    all_data = [pd.read_csv(path, index_col=None) for path in all_files]
    return pd.concat(all_data, axis=0, ignore_index=True)


data_dir = "./exp-local/data/info"
data = import_perf_data(data_dir)


def extract_params_from_local_file_name(dat):
    dat[['Workflow', 'mode', 'ncores', 'node', 'trial']] = dat.JobName.str.extract(
        r'(\w+)-(\w+)-nc(\d+)_(\w+?\d+)-(\d+).cfg')
    dat.ncores = dat.ncores.astype(int)
    dat.trial = dat.trial.astype(int)
    return dat


data = extract_params_from_local_file_name(data)
data


# In[33]:


# create 3 separate plots each having JobName and another column

import matplotlib.pyplot as plt

fig, axs = plt.subplots(3, 1, figsize=(10, 20))
# increase vertical space
fig.subplots_adjust(hspace=.7)

data.sort_values(by=['power_energy_pkg'], inplace=True)

# plot 1
axs[0].bar(data['JobName'], data.power_energy_pkg)
axs[0].set_title('power_energy_pkg')
axs[0].set_xticklabels(axs[0].get_xticklabels(), rotation=-75)

# plot 2
axs[1].bar(data['JobName'], data.power_energy_ram)
axs[1].set_title('power_energy_ram')
axs[1].set_xticklabels(axs[1].get_xticklabels(), rotation=-75)

# plot 3
axs[2].bar(data['JobName'], data.perf_elapsed)
axs[2].set_title('perf_elapsed')
axs[2].set_xticklabels(axs[2].get_xticklabels(), rotation=-75)


# In[41]:


# create similar 3 plots buy boxplots, make sure to group them by workflow, mode, ncores, node

fig, axs = plt.subplots(3, 1, figsize=(10, 20))
# increase vertical space
fig.subplots_adjust(hspace=.7)

# plot 1
data.boxplot(column=['power_energy_pkg'], by=['Workflow', 'mode', 'ncores', 'node'], ax=axs[0])
axs[0].set_title('power_energy_pkg')
axs[0].set_xticklabels(axs[0].get_xticklabels(), rotation=-75)

# plot 2
data.boxplot(column=['power_energy_ram'], by=['Workflow', 'mode', 'ncores', 'node'], ax=axs[1])
axs[1].set_title('power_energy_ram')
axs[1].set_xticklabels(axs[1].get_xticklabels(), rotation=-75)

# plot 3
data.boxplot(column=['perf_elapsed'], by=['Workflow', 'mode', 'ncores', 'node'], ax=axs[2])
axs[2].set_title('perf_elapsed')
axs[2].set_xticklabels(axs[2].get_xticklabels(), rotation=-75)

# save it to file
plt.savefig('energy.boxplots.png')


# In[ ]:




