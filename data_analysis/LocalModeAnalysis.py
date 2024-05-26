#!/usr/bin/env python
# coding: utf-8

# In[1]:


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

# In[2]:


# Functions for parsing the files
def extract_workflow(df):
    # This function gets the entries referring to batches
    # and extracts the corresponding workflow from the job entry
    batches = df[df['JobID'].str.contains('batch', regex=True)]

    for i, row in batches.iterrows():
        jobid = row.JobID.split('.')[0] # extracts di ID
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
    df.columns =  list(df.loc[0]) # set headers
    # gets completed entries
    df = df[(df['State'] == 'COMPLETED')]
    
    return extract_workflow(df)

def read_dataset(files):
    dfs = [parse(f) for f in files]
    
    return pd.concat(dfs, ignore_index=True)


# In[3]:


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
    ss_total = sum((vec - np.mean(vec))**2)

    return ss_total

def ss_between( *args):
    # grand mean
    grand_mean = np.mean(concentrate(*args))

    ss_btwn = 0
    for a in args:
        ss_btwn += (len(a) * (np.mean( a) - grand_mean) **2)

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


# In[4]:


# Import Dataset
data_dir = "./exp-local"


# ## RQ - What is the impact of the ncores parameter on energy consumption and performance?

# In[5]:


files = Path(data_dir).glob('*gl6*.txt')
data = read_dataset(files)


# In[6]:


data.head()


# In[7]:


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
    return float(remove_unit(memory_str)) * (10**-6)

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

# In[8]:


daa_energy = get_data(data, workflow='daa', column='ConsumedEnergy')


# In[9]:


# Descriptive Statistics
daa_energy.groupby('NCPUS').agg(['mean', 'std', 'var'])


# In[10]:


# Pearson correlation Between NCORES and Energy Consumption
print(
    "Pearson Correlation:", 
    daa_energy['NCPUS'].corr(daa_energy['ConsumedEnergy'])
)


# In[11]:


# Obtaining the samples (daa, 4) (daa, 8) .. (daa, 32)
samples = {
    x : list(daa_energy[daa_energy['NCPUS'] == x]['ConsumedEnergy']) for x in [4, 8, 16, 32]
}


# In[12]:


normality_check(samples, x_label='NCores', y_label='ConsumedEnergy(MJ)')


# In[13]:


# homoscedasticity Levene's Test
statistic, p_value = stats.levene(*list(samples.values()))
print("stat:", statistic, "p_value:", p_value)


# In[14]:


# One-Way Anova Test
f_stat, p_value = f_oneway(*list(samples.values()))
print("f_stat:", statistic, "p_value:", p_value)


# In[15]:


# Effect Size using Eta Squared
effect_size(*list(samples.values()))


# In[16]:


# Average Improvement
average_energy = [mean(x) for x in samples.values()]
improvement(average_energy[0], average_energy[-1])


# #### DPP

# In[17]:


dpp_energy = get_data(data, workflow='dpp', column='ConsumedEnergy')


# In[18]:


# Descriptive Statistics
dpp_energy.groupby('NCPUS').agg(['mean', 'std', 'var'])


# In[19]:


# Pearson correlation Between NCORES and Energy Consumption
print(
    "Pearson Correlation:", 
    dpp_energy['NCPUS'].corr(dpp_energy['ConsumedEnergy'])
)


# In[20]:


# Obtaining the samples (daa, 4) (daa, 8) .. (daa, 32)
samples = {
    x : list(dpp_energy[dpp_energy['NCPUS'] == x]['ConsumedEnergy']) for x in [4, 8, 16, 32]
}


# In[21]:


normality_check(samples, x_label='NCores', y_label='ConsumedEnergy(KJ)')


# In[22]:


# homoscedasticity Levene's Test
statistic, p_value = stats.levene(*list(samples.values()))
print("stat:", statistic, "p_value:", p_value)


# In[23]:


# One-Way Anova Test
f_stat, p_value = f_oneway(*list(samples.values()))
print("f_stat:", statistic, "p_value:", p_value)


# In[24]:


# Effect Size using Eta Squared
effect_size(*list(samples.values()))


# In[25]:


# Average Improvement
average_energy = [mean(x) for x in samples.values()]
improvement(average_energy[0], average_energy[-1])


# ### Execution Time

# #### DAA

# In[26]:


daa_time = get_data(data, workflow='daa', column='Elapsed')


# In[27]:


# Descriptive Statistics
daa_time.groupby('NCPUS').agg(['mean', 'std', 'var'])


# In[28]:


# Pearson correlation Between NCORES and Execution Time
print(
    "Pearson Correlation:", 
    daa_time['NCPUS'].corr(daa_time['Elapsed'])
)


# In[29]:


# Obtaining the samples (daa, 4) (daa, 8) .. (daa, 32)
samples = {
    x : list(daa_time[daa_time['NCPUS'] == x]['Elapsed']) for x in [4, 8, 16, 32]
}


# In[30]:


normality_check(samples, x_label='NCores', y_label='ElapsedTime(h)')


# In[31]:


# Average Improvement
average_energy = [mean(x) for x in samples.values()]
improvement(average_energy[0], average_energy[-1])


# #### DPP

# In[32]:


dpp_time = get_data(data, workflow='dpp', column='Elapsed')


# In[33]:


# Descriptive Statistics
dpp_time.groupby('NCPUS').agg(['mean', 'std', 'var'])


# In[34]:


# Pearson correlation Between NCORES and Execution Time
print(
    "Pearson Correlation:", 
    dpp_time['NCPUS'].corr(dpp_time['Elapsed'])
)


# In[35]:


samples = {
    x : list(dpp_time[dpp_time['NCPUS'] == x]['Elapsed']) for x in [4, 8, 16, 32]
}


# In[36]:


normality_check(samples, x_label='NCores', y_label='ElapsedTime(h)')


# In[37]:


# Average Improvement
average_energy = [mean(x) for x in samples.values()]
improvement(average_energy[0], average_energy[-1])


# ### Memory Usage

# #### DAA

# In[38]:


daa_memory = get_data(data, workflow='daa', column='AveRSS')


# In[39]:


daa_memory.head()


# In[40]:


# Descriptive Statistics
daa_memory.groupby('NCPUS').agg(['mean', 'std', 'var'])


# In[41]:


# Pearson correlation Between NCORES and Memory
print(
    "Pearson Correlation:", 
    daa_memory['NCPUS'].corr(daa_memory['AveRSS'])
)


# In[42]:


samples = {
    x : list(daa_memory[daa_memory['NCPUS'] == x]['AveRSS']) for x in [4, 8, 16, 32]
}


# In[43]:


normality_check(samples, x_label='NCores', y_label='AveRSS(Gb)')


# In[44]:


# Average Improvement
average_energy = [mean(x) for x in samples.values()]
improvement(average_energy[0], average_energy[-1])


# #### DPP

# In[45]:


dpp_memory = get_data(data, workflow='dpp', column='AveRSS')


# In[46]:


dpp_memory.groupby('NCPUS').agg(['mean', 'std', 'var'])


# In[47]:


# Pearson correlation Between NCORES and Memory
print(
    "Pearson Correlation:", 
    dpp_memory['NCPUS'].corr(dpp_memory['AveRSS'])
)


# In[48]:


samples = {
    x : list(dpp_memory[dpp_memory['NCPUS'] == x]['AveRSS']) for x in [4, 8, 16, 32]
}


# In[49]:


normality_check(samples, x_label='NCores', y_label='AveRSS(Gb)')


# In[50]:


# Average Improvement
average_energy = [mean(x) for x in samples.values()]
improvement(average_energy[0], average_energy[-1])


# In[51]:


data


# ## RQ - What is the impact of the underlying hardware platform on energy consumption and performance?

# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




