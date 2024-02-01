#!/usr/bin/env python
# coding: utf-8

# In[2]:


import re
import sys
from pathlib import Path

import pandas as pd
from IPython.core.display_functions import display
from matplotlib import pyplot as plt
from matplotlib.image import AxesImage

sys.path.append(str(Path.cwd().parent))
sys.path.append(str(Path.cwd()))
from data_analysis.CLI import ExperimentDir


# In[3]:


exp = ExperimentDir.LOCAL
if len(sys.argv) > 1:
    try:
        exp = ExperimentDir.value_to_enum(sys.argv[1])
    except ValueError as e:
        print(f"Experiment was set to {exp}", e)

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


# In[4]:


data_gathered = df.groupby(['image_name', 'mode', 'workflow', 'ncores']).size().reset_index(name='count')
data_gathered.to_csv('info.csv', index=False)
data_gathered


# In[5]:


data_gathered_by_node = df.groupby(['image_name', 'mode', 'workflow', 'ncores', 'node']).size().reset_index(
    name='count')
data_gathered_by_node.to_csv('info.by_node.csv', index=False)
data_gathered_by_node


# In[6]:


workflow = 'daa'
image_name = 'run_avg_cpu_util_all.png'
df_slice = df[(df.workflow == workflow) & (df.image_name == image_name)]
df_slice


# In[15]:


df_count = df_slice.groupby(['node', 'ncores']).size().reset_index(name='count')
df_max_count_per_ncores = df_count.groupby('ncores')['count'].max().reset_index(name='max_count')
total_count = df_max_count_per_ncores['max_count'].sum()
# df_max
node_order_by_run_count = df_slice.groupby(['node']).size().reset_index(name="count").sort_values(by=['count'],
                                                                                                  ascending=False)
display(df_count, df_max_count_per_ncores,
        node_order_by_run_count.node.values.tolist(),
        total_count)


# In[37]:


from typing import Set

scale = 3

# df = df[(df.workflow == 'daa') & (df.image_name == 'run_avg_cpu_util_all.png')]

# for unique workflogs
for workflow in df.workflow.unique():
    for image_name in df.image_name.unique():
        img_name = f"{workflow}_{image_name}"
        print(f"Generating {img_name}")

        df_slice = df[(df.workflow == workflow) & (df.image_name == image_name)]
        df_count = df_slice.groupby(['node', 'ncores']).size().reset_index(name='count')
        df_max_count_per_ncores = df_count.groupby('ncores')['count'].max().reset_index(name='max_count')

        n_cols = len(df_slice.node.unique())
        n_rows = df_max_count_per_ncores['max_count'].sum()
        fig, ax = plt.subplots(n_rows, n_cols, figsize=(n_cols * 5 * scale, n_rows * 2 * scale))

        node_order_by_run_count = df_slice.groupby(['node']).size().reset_index(name="count").sort_values(
            by=['count']).node.values.tolist()
        plotted = set()
        for col_reverse, node in enumerate(node_order_by_run_count):
            # reverse iteration for correct y_label (ncores) printing
            col = len(node_order_by_run_count) - 1 - col_reverse
            row_offset = 0
            df_slice_node = df_slice[df_slice.node == node]
            for ncore in df_max_count_per_ncores.ncores:
                max_ncore_group_rows = \
                    df_max_count_per_ncores[df_max_count_per_ncores.ncores == ncore].max_count.values[0]
                for ncore_group_row, (_, cfg) in enumerate(df_slice_node[df_slice_node.ncores == ncore].iterrows()):
                    row = row_offset + ncore_group_row
                    plotted.add((row, col))
                    ax[row, col].imshow(plt.imread(cfg.path))
                    ax[row, col].axis('off')


                    def adjust_style(axx):
                        axx.axis('on')
                        axx.set_xticks([])
                        axx.set_yticks([])
                        axx.spines[:].set_visible(False)


                    if col == 0 or not (row, col + 1) in plotted:
                        adjust_style(ax[row, col])
                        ax[row, col].set_ylabel(f"{cfg.ncores} ncores", fontsize=20)
                        ax[row, col].yaxis.set_label_position('right')
                    if col == 0:
                        ax[row, col].yaxis.set_label_position('left')

                    if row == n_rows - 1 or not (row - 1, col) in plotted:
                        adjust_style(ax[row, col])
                        ax[row, col].set_xlabel(f"{node}", fontsize=20)
                        ax[row, col].xaxis.set_label_position('top')
                    if row == n_rows - 1:
                        ax[row, col].xaxis.set_label_position('bottom')

                    # add horizontal line delimited for ncores
                    if ncore_group_row == 0 and row != 0:
                        ax[row, col].spines['top'].set_visible(True)

                row_offset += max_ncore_group_rows

        for i in range(n_cols):
            for j in range(n_rows):
                if not (j, i) in plotted:
                    ax[j, i].axis('off')
                    ax[j, i].set_xticks([])
                    ax[j, i].set_yticks([])

        plt.tight_layout()
        fig.suptitle(f"{workflow}_{image_name.replace('.png', '')}", fontsize=30, y=1.01)

        plt.savefig(img_name)
        # plt.show()



# In[ ]:




