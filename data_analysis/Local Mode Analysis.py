#!/usr/bin/env python
# coding: utf-8

# In[76]:


from pathlib import Path
import pandas as pd
import regex as re
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np


# # Experiment on Local Mode
# 
# ## Independent Variable
# * ```ncores: [4, 8, 16, 32]```
# * ```workload: [daa, dpp]```
# * ```node: [gl6]```
# 
# ## Dependent Variable:
# 
# * ```Energy Consumption (MJ)```
# * ```Execution Time (hours)```
# * ```Memory Utilization - AveRSS (MB)```

# In[77]:


# Functions for parsing the files
def extract_workflow(df):
    # This function gets the entries referring to batches
    # and extracts the corresponding workflow from the job entry
    batches = df[df['JobID'].str.contains('batch', regex=True)]

    for i, row in batches.iterrows():
        jobid = row.JobID.split('.')[0]  # extracts di ID
        # find the job entry in the dataframe including all the entries
        jobrow = df[df['JobID'] == jobid]
        # extract the workflow from job name
        workflow = jobrow['JobName'].item().split('-')[0]

        # substitute JobName with the workflow
        row['JobName'] = workflow
        row['JobID'] = jobid

    return batches.rename(columns={'JobName': 'Workflow'})


def parse(path):
    df = pd.read_csv(path, header=None, delimiter=r"\s+")
    df.columns = list(df.loc[0])  # set headers
    # gets completed entries
    df = df[(df['State'] == 'COMPLETED')]

    return extract_workflow(df)


def read_dataset(files):
    dfs = [parse(f) for f in files]

    return pd.concat(dfs, ignore_index=True)


# In[78]:


# Functions for performing Statistical Tests
import scipy.stats as stats
from scipy.stats import f_oneway
from scipy.stats import shapiro
from statistics import mean

pd.set_option('mode.chained_assignment', None)


def improvement(original_value, new_value):
    improvement_percentage = ((new_value - original_value) / abs(original_value)) * 100
    return improvement_percentage


# Code taken from
# https://stats.stackexchange.com/questions/67926/understanding-the-one-way-anova-effect-size-in-scipy

def effect_size(*args):
    """ Return the eta squared as the effect size for ANOVA"""
    return float(ss_between(*args) / ss_total(*args))


def ss_total(*args):
    vec = concentrate(*args)
    ss_total = sum((vec - np.mean(vec)) ** 2)

    return ss_total


def ss_between(*args):
    # grand mean
    grand_mean = np.mean(concentrate(*args))

    ss_btwn = 0
    for a in args:
        ss_btwn += (len(a) * (np.mean(a) - grand_mean) ** 2)

    return ss_btwn


def ss_within(*args):
    return ss_total(*args) - ss_between(*args)


def concentrate(*args):
    v = list(map(np.asarray, args))
    vec = np.hstack(np.concatenate(v))
    return vec


def normality_check(samples, x_label="", y_label=""):
    # Set Grid for the plots
    fig, axs = plt.subplots(ncols=2, nrows=2, figsize=(20, 10))

    c = 0
    i = 0

    # Normality Check using Shapiro-Wilk
    for x, y in samples.items():
        stat, p = shapiro(y)
        print('NCORES:', x, '\tSTAT:', stat, '\tp-value:', p)

        # Generate a Violin Plot
        ax = sns.violinplot(data=y, ax=axs[i][c])
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.set_xticklabels([x])
        c += 1

        if c > 1:
            i += 1
            c = 0


# In[79]:


# Import Dataset
data_dir = "./exp-local/data/old"


# ## RQ - What is the impact of the ncores parameter on energy consumption and performance?

# In[80]:


files = Path(data_dir).glob('*gl6*.txt')
data = read_dataset(files)


# In[81]:


data.head()


# In[82]:


def convert_to_hours(time_str):
    d = 0

    if '-' in time_str:
        d = time_str.split('-')
        time_str = d[1]
        d = int(d[0])

    h, m, s = list(map(int, time_str.split(':')))
    total_hours = h + m / 60 + s / 3600

    return total_hours + (d * 24)


def remove_unit(string):
    if 'M' in string:
        return string.replace('M', '')
    # elif 'K' in string:
    return string.replace('K', '')


def convert_to_gb(memory_str):
    return float(remove_unit(memory_str)) * (10 ** -6)


def convert_to_mega_joule(energy_str):
    return remove_unit(energy_str)


def get_data(data, workflow="daa", column="Elapsed"):
    output = data[data['Workflow'] == workflow][[column, 'NCPUS']]

    # Clean Data
    if column == "ConsumedEnergy":
        output[column] = output[column].apply(convert_to_mega_joule)
    elif column == "AveRSS":
        output[column] = output[column].apply(convert_to_gb)
    elif column == "Elapsed":
        output[column] = output[column].apply(convert_to_hours)

    # Convert Data
    return output.astype({column: float, "NCPUS": int})


# ### Energy Consumption 

# #### DAA

# In[83]:


daa_energy = get_data(data, workflow='daa', column='ConsumedEnergy')


# In[84]:


# Descriptive Statistics
daa_energy.groupby('NCPUS').agg(['mean', 'std', 'var'])


# In[85]:


# Pearson correlation Between NCORES and Energy Consumption
print(
    "Pearson Correlation:",
    daa_energy['NCPUS'].corr(daa_energy['ConsumedEnergy'])
)


# In[86]:


# Obtaining the samples (daa, 4) (daa, 8) .. (daa, 32)
samples = {
    x: list(daa_energy[daa_energy['NCPUS'] == x]['ConsumedEnergy']) for x in [4, 8, 16, 32]
}


# In[87]:


normality_check(samples, x_label='NCores', y_label='ConsumedEnergy(MJ)')


# In[88]:


# homoscedasticity Levene's Test
statistic, p_value = stats.levene(*list(samples.values()))
print("stat:", statistic, "p_value:", p_value)


# In[89]:


# One-Way Anova Test
f_stat, p_value = f_oneway(*list(samples.values()))
print("f_stat:", statistic, "p_value:", p_value)


# In[90]:


# Effect Size using Eta Squared
effect_size(*list(samples.values()))


# In[91]:


# Average Improvement
average_energy = [mean(x) for x in samples.values()]
improvement(average_energy[0], average_energy[-1])


# #### DPP

# In[92]:


dpp_energy = get_data(data, workflow='dpp', column='ConsumedEnergy')


# In[93]:


# Descriptive Statistics
dpp_energy.groupby('NCPUS').agg(['mean', 'std', 'var'])


# In[94]:


# Pearson correlation Between NCORES and Energy Consumption
print(
    "Pearson Correlation:",
    dpp_energy['NCPUS'].corr(dpp_energy['ConsumedEnergy'])
)


# In[95]:


# Obtaining the samples (daa, 4) (daa, 8) .. (daa, 32)
samples = {
    x: list(dpp_energy[dpp_energy['NCPUS'] == x]['ConsumedEnergy']) for x in [4, 8, 16, 32]
}


# In[96]:


normality_check(samples, x_label='NCores', y_label='ConsumedEnergy(KJ)')


# In[97]:


# homoscedasticity Levene's Test
statistic, p_value = stats.levene(*list(samples.values()))
print("stat:", statistic, "p_value:", p_value)


# In[98]:


# One-Way Anova Test
f_stat, p_value = f_oneway(*list(samples.values()))
print("f_stat:", statistic, "p_value:", p_value)


# In[99]:


# Effect Size using Eta Squared
effect_size(*list(samples.values()))


# In[100]:


# Average Improvement
average_energy = [mean(x) for x in samples.values()]
improvement(average_energy[0], average_energy[-1])


# ### Execution Time

# #### DAA

# In[101]:


daa_time = get_data(data, workflow='daa', column='Elapsed')


# In[102]:


# Descriptive Statistics
daa_time.groupby('NCPUS').agg(['mean', 'std', 'var'])


# In[103]:


# Pearson correlation Between NCORES and Execution Time
print(
    "Pearson Correlation:",
    daa_time['NCPUS'].corr(daa_time['Elapsed'])
)


# In[104]:


# Obtaining the samples (daa, 4) (daa, 8) .. (daa, 32)
samples = {
    x: list(daa_time[daa_time['NCPUS'] == x]['Elapsed']) for x in [4, 8, 16, 32]
}


# In[105]:


normality_check(samples, x_label='NCores', y_label='ElapsedTime(h)')


# In[106]:


# Average Improvement
average_energy = [mean(x) for x in samples.values()]
improvement(average_energy[0], average_energy[-1])


# #### DPP

# In[107]:


dpp_time = get_data(data, workflow='dpp', column='Elapsed')


# In[108]:


# Descriptive Statistics
dpp_time.groupby('NCPUS').agg(['mean', 'std', 'var'])


# In[109]:


# Pearson correlation Between NCORES and Execution Time
print(
    "Pearson Correlation:",
    dpp_time['NCPUS'].corr(dpp_time['Elapsed'])
)


# In[110]:


samples = {
    x: list(dpp_time[dpp_time['NCPUS'] == x]['Elapsed']) for x in [4, 8, 16, 32]
}


# In[111]:


normality_check(samples, x_label='NCores', y_label='ElapsedTime(h)')


# In[112]:


# Average Improvement
average_energy = [mean(x) for x in samples.values()]
improvement(average_energy[0], average_energy[-1])


# ### Memory Usage

# #### DAA

# In[113]:


daa_memory = get_data(data, workflow='daa', column='AveRSS')


# In[114]:


daa_memory.head()


# In[115]:


# Descriptive Statistics
daa_memory.groupby('NCPUS').agg(['mean', 'std', 'var'])


# In[116]:


# Pearson correlation Between NCORES and Memory
print(
    "Pearson Correlation:",
    daa_memory['NCPUS'].corr(daa_memory['AveRSS'])
)


# In[117]:


samples = {
    x: list(daa_memory[daa_memory['NCPUS'] == x]['AveRSS']) for x in [4, 8, 16, 32]
}


# In[118]:


normality_check(samples, x_label='NCores', y_label='AveRSS(Gb)')


# In[119]:


# Average Improvement
average_energy = [mean(x) for x in samples.values()]
improvement(average_energy[0], average_energy[-1])


# #### DPP

# In[120]:


dpp_memory = get_data(data, workflow='dpp', column='AveRSS')


# In[121]:


dpp_memory.groupby('NCPUS').agg(['mean', 'std', 'var'])


# In[122]:


# Pearson correlation Between NCORES and Memory
print(
    "Pearson Correlation:",
    dpp_memory['NCPUS'].corr(dpp_memory['AveRSS'])
)


# In[123]:


samples = {
    x: list(dpp_memory[dpp_memory['NCPUS'] == x]['AveRSS']) for x in [4, 8, 16, 32]
}


# In[124]:


normality_check(samples, x_label='NCores', y_label='AveRSS(Gb)')


# In[125]:


# Average Improvement
average_energy = [mean(x) for x in samples.values()]
improvement(average_energy[0], average_energy[-1])


# In[126]:


data


# ## RQ - What is the impact of the underlying hardware platform on energy consumption and performance?

# In[147]:


## merge into a single descriptive table
daa_e = daa_energy.groupby('NCPUS').agg(['mean', 'std', 'var']).reset_index()
dpp_e = dpp_energy.groupby('NCPUS').agg(['mean', 'std', 'var']).reset_index()
daa_t = daa_time.groupby('NCPUS').agg(['mean', 'std', 'var']).reset_index()
dpp_t = dpp_time.groupby('NCPUS').agg(['mean', 'std', 'var']).reset_index()
daa_m = daa_memory.groupby('NCPUS').agg(['mean', 'std', 'var']).reset_index()
dpp_m = dpp_memory.groupby('NCPUS').agg(['mean', 'std', 'var']).reset_index()

# combine all daa
daa = pd.merge(daa_e, daa_t, on='NCPUS')
daa = pd.merge(daa, daa_m, on='NCPUS')

# combine all dpp
dpp = pd.merge(dpp_e, dpp_t, on='NCPUS')
dpp = pd.merge(dpp, dpp_m, on='NCPUS')

# add explicit columns with workflow - either daa or dpp
daa['workflow'] = 'daa'
dpp['workflow'] = 'dpp'

# combine all
all_data = pd.concat([daa, dpp])

# drop NCPUS == 2
all_data = all_data[all_data['NCPUS'] != 2]

# reset index
all_data.reset_index(drop=True, inplace=True)

# show only 3 digits after the comma
all_data = all_data.round(3)

#  make workflow the first column
cols = all_data.columns.tolist()
cols = cols[-1:] + cols[:-1]
all_data = all_data[cols]

all_data


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




