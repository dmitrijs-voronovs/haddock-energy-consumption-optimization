#!/usr/bin/env python
# coding: utf-8

# In[77]:


import re
from pathlib import Path

import pandas as pd
from matplotlib import pyplot as plt

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


# In[98]:


workflow = 'dpp'
image_name = 'run_avg_mem_util.png'
df_slice = df[(df.workflow == workflow) & (df.image_name == image_name)]
df_slice


# In[112]:


df_grouped = df_slice.groupby(['node', 'ncores']).size().reset_index(name='count')
df_max = df_grouped.groupby('ncores')['count'].max().reset_index(name='max_count')
# total_count = df_max['max_count'].sum()
# df_max
display(df_grouped, df_max)


# In[66]:


# for unique workflogs
# for workflow in df.workflow.unique():
for workflow in ['dpp']:
    # for image_name in df.image_name.unique():
    for image_name in ['run_avg_mem_util.png']:
        print(f"{workflow=} {image_name=}")
        #                 x axis - nodes
        #                y axis - nc_param
        df_slice = df[(df.workflow == workflow) & (df.image_name == image_name)]
        x_len = len(df_slice.node.unique())
        y_len = df_slice.groupby(['node']).count().ncores.max()
        # y_len = len(df_slice.ncores.unique())
        print(f"{x_len=} {y_len=}")
        fig, ax = plt.subplots(y_len, x_len, figsize=(x_len * 10, y_len * 4))
        display(df_slice)
        for (n, node) in enumerate(df_slice.node.unique()):
            # for (p, ncores) in enumerate(df_slice.ncores.unique()):
            for (nc, ncores) in enumerate(df_slice[df_slice.node == node].ncores):
                print(f"{n=} {nc=}")
                cfg = df_slice[(df_slice.node == node)].iloc[nc]
                ax[nc, n].imshow(plt.imread(cfg.path))
                ax[nc, n].set_title(f"Trial: {cfg.trial}, {node=}, {ncores=}", fontsize=10, pad=2)
                # ax[p, n].axis('off')
                ax[nc, n].set_xticks([])
                ax[nc, n].set_yticks([])
                ax[nc, n].xaxis.set_label_position('top')
                ax[nc, n].set_xlabel(node)
                ax[nc, n].set_ylabel(ncores)

                # for axx, ncores in zip(ax[0], unique_ncores):
                #     axx.set_xlabel(ncores, fontsize=12, labelpad=10)
                # for axx, node in zip(ax[:, 0], unique_nodes):
                #     axx.set_ylabel(node, fontsize=12, labelpad=10)

        # add labels to the plot
        # plt.xlabel('node')
        # plt.ylabel('ncores')
        # plt.xticks(range(x_len), x_ticks)
        # plt.yticks(range(y_len), y_ticks)
        # Add labels and ticks to the plot

        plt.tight_layout()
        plt.savefig(f"{workflow}_{image_name}")
        plt.show()


