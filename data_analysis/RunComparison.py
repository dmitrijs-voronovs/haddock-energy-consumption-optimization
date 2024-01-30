#!/usr/bin/env python
# coding: utf-8

# In[140]:


import re
from pathlib import Path

import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.image import AxesImage

from data_analysis.CLI import ExperimentDir


# In[84]:


exp = ExperimentDir.LOCAL
exp_dir = Path(ExperimentDir.host_dir(exp)) / 'runs'
pngs = list(exp_dir.glob('run.*.parsed/*png'))

generic_config_regex = r".+?\.(.+?)-(.+?)(?:-(.+?))_(.+?)-(\d+)\.cfg.+"
local_config_regex = r".+?\.(.+?)-(.+?)-nc(\d+)_(.+?)-(\d+)\.cfg.+"
extract_params_from_config = lambda cfg: re.match(local_config_regex,
                                                  cfg).groups()
extract_cfg_name = lambda cfg: re.match(r"^.+?\.(.+?)\..+$", cfg).group(1)

configs = []
for png in pngs:
    workflow, mode, ncores, node, trial = extract_params_from_config(png.parent.name)
    configs.append({
        'cfg_name': extract_cfg_name(png.parent.name),
        'path': png,
        'workflow': workflow,
        "mode": mode,
        'ncores': int(ncores),
        'node': node,
        'trial': int(trial),
        'image_name': png.name,
    })

df = pd.DataFrame(configs, columns=['cfg_name', 'path', 'workflow', 'mode', 'ncores', 'node', 'trial', 'image_name'])
df


# In[96]:


data_gathered = df.groupby(['image_name', 'mode', 'workflow', 'ncores']).size().reset_index(name='count')
data_gathered.to_csv('gathered_data_stat.csv', index=False)
data_gathered


# In[97]:


data_gathered_by_node = df.groupby(['image_name', 'mode', 'workflow', 'ncores', 'node']).size().reset_index(
    name='count')
data_gathered_by_node.to_csv('gathered_data_by_node_stat.csv', index=False)
data_gathered_by_node


# In[118]:


workflow = 'daa'
image_name = 'run_avg_cpu_util_all.png'
df_slice = df[(df.workflow == workflow) & (df.image_name == image_name)]
df_slice


# In[119]:


df_grouped = df_slice.groupby(['node', 'ncores']).size().reset_index(name='count')
df_max = df_grouped.groupby('ncores')['count'].max().reset_index(name='max_count')
total_count = df_max['max_count'].sum()
# df_max
display(df_grouped, df_max, total_count)


# In[167]:


scale = 3

# for unique workflogs
for workflow in df.workflow.unique():
    for image_name in df.image_name.unique():
        df_slice = df[(df.workflow == workflow) & (df.image_name == image_name)]
        df_grouped = df_slice.groupby(['node', 'ncores']).size().reset_index(name='count')
        df_max = df_grouped.groupby('ncores')['count'].max().reset_index(name='max_count')
        x_len = len(df_slice.node.unique())
        y_len = df_max['max_count'].sum()
        fig, ax = plt.subplots(y_len, x_len, figsize=(x_len * 5 * scale, y_len * 2 * scale))
        for (n, node) in enumerate(df_slice.node.unique()):
            y_offset = 0
            df_slice_node = df_slice[df_slice.node == node]
            for ncore in df_max.ncores:
                max_for_ncores = df_max[df_max.ncores == ncore].max_count.values[0]
                for ncc, (_, cfg) in enumerate(df_slice_node[df_slice_node.ncores == ncore].iterrows()):
                    nc = y_offset + ncc
                    ax[nc, n].imshow(plt.imread(cfg.path))
                    ax[nc, n].axis('off')


                    def adjust_style(axx):
                        axx.axis('on')
                        axx.set_xticks([])
                        axx.set_yticks([])
                        axx.spines[:].set_visible(False)


                    if n == 0 or n == x_len - 1:
                        adjust_style(ax[nc, n])
                        ax[nc, n].set_ylabel(f"{cfg.ncores} ncores", fontsize=20)
                    if n == x_len - 1:
                        ax[nc, n].yaxis.set_label_position('right')

                    if nc == 0 or nc == y_len - 1:
                        adjust_style(ax[nc, n])
                        ax[nc, n].set_xlabel(f"{node}", fontsize=20)
                    if nc == 0:
                        ax[nc, n].xaxis.set_label_position('top')

                    if ncc == 0 and nc != 0:
                        ax[nc, n].spines['top'].set_visible(True)

                y_offset += max_for_ncores

        for i in range(x_len):
            for j in range(y_len):
                children = ax[j, i].get_children()
                if not any(isinstance(child, AxesImage) for child in children):
                    ax[j, i].axis('off')
                    ax[j, i].set_xticks([])
                    ax[j, i].set_yticks([])

        plt.tight_layout()
        plt.savefig(f"{workflow}_{image_name}")
        plt.show()



# In[ ]:




