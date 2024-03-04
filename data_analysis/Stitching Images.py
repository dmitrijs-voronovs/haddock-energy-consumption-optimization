#!/usr/bin/env python
# coding: utf-8

# In[6]:


from PIL import Image
from enum import Enum
from pathlib import Path

run_dir = Path("../examples/exp-local/runs")


class Img(Enum):
    run_avg_cpu_freq = "run_avg_cpu_freq.png"
    run_avg_cpu_util_all = "run_avg_cpu_util_all.png"
    run_avg_cpu_util_every = "run_avg_cpu_util_every.png"
    run_avg_mem_util = "run_avg_mem_util.png"
    run_avg_normalized = "run_avg_normalized.png"


class Mode(Enum):
    LOCAL = "local"
    HPC = "hpc"
    MPI = "mpi"


class Workflow(Enum):
    DAA = "daa"
    DPP = "dpp"


class Node(Enum):
    gl2 = "gl2"
    gl4 = "gl4"
    gl5 = "gl5"
    gl6 = "gl6"


def get_image_path(workflow: 'Workflow', ncores: int, node: 'Node', trial: int, image: 'Img'):
    return run_dir / f"run.{workflow.value}-{Mode.LOCAL.value}-nc{ncores}_{node.value}-{trial}.cfg.parsed" / image.value


def glue_images_horizontally(images, output_path):
    images = [Image.open(x) for x in images]
    widths, heights = zip(*(i.size for i in images))

    total_width = sum(widths)
    max_height = max(heights)

    new_im = Image.new('RGB', (total_width, max_height))

    x_offset = 0
    for im in images:
        new_im.paste(im, (x_offset, 0))
        x_offset += im.size[0]

    new_im.save(output_path)


def glue_images_vertically(images, output_path):
    images = [Image.open(x) for x in images]
    widths, heights = zip(*(i.size for i in images))

    total_height = sum(heights)
    max_width = max(widths)

    new_im = Image.new('RGB', (max_width, total_height))

    y_offset = 0
    for im in images:
        new_im.paste(im, (0, y_offset))
        y_offset += im.size[1]

    new_im.save(output_path)


# In[16]:


output_dir = Path("./run_analysis/")
glue_images_vertically([get_image_path(Workflow.DAA, 4, Node.gl5, 31, Img.run_avg_cpu_util_all),
                        get_image_path(Workflow.DAA, 8, Node.gl5, 31, Img.run_avg_cpu_util_all),
                        get_image_path(Workflow.DAA, 16, Node.gl5, 41, Img.run_avg_cpu_util_all),
                        get_image_path(Workflow.DAA, 32, Node.gl5, 41, Img.run_avg_cpu_util_all)],
                       output_dir / "daa-cpu_util_all-ncores-cmp.png")

glue_images_vertically([get_image_path(Workflow.DAA, 4, Node.gl5, 31, Img.run_avg_mem_util),
                        get_image_path(Workflow.DAA, 8, Node.gl5, 31, Img.run_avg_mem_util),
                        get_image_path(Workflow.DAA, 16, Node.gl5, 41, Img.run_avg_mem_util),
                        get_image_path(Workflow.DAA, 32, Node.gl5, 41, Img.run_avg_mem_util)],
                       output_dir / "daa-mem_util-ncores-cmp.png")

glue_images_vertically([get_image_path(Workflow.DPP, 4, Node.gl5, 33, Img.run_avg_cpu_util_all),
                        get_image_path(Workflow.DPP, 8, Node.gl5, 33, Img.run_avg_cpu_util_all),
                        get_image_path(Workflow.DPP, 16, Node.gl5, 33, Img.run_avg_cpu_util_all),
                        get_image_path(Workflow.DPP, 32, Node.gl5, 33, Img.run_avg_cpu_util_all)],
                       output_dir / "dpp-cpu_util_all-ncores-cmp.png")

glue_images_vertically([get_image_path(Workflow.DPP, 4, Node.gl5, 33, Img.run_avg_mem_util),
                        get_image_path(Workflow.DPP, 8, Node.gl5, 33, Img.run_avg_mem_util),
                        get_image_path(Workflow.DPP, 16, Node.gl5, 33, Img.run_avg_mem_util),
                        get_image_path(Workflow.DPP, 32, Node.gl5, 33, Img.run_avg_mem_util)],
                       output_dir / "dpp-mem_util-ncores-cmp.png")

glue_images_vertically([get_image_path(Workflow.DAA, 8, Node.gl5, 31, Img.run_avg_cpu_freq),
                        get_image_path(Workflow.DAA, 8, Node.gl5, 31, Img.run_avg_cpu_util_all),
                        get_image_path(Workflow.DAA, 8, Node.gl5, 31, Img.run_avg_mem_util)],
                       output_dir / "daa-8nc-metrics-cmp.png")

glue_images_vertically([get_image_path(Workflow.DPP, 16, Node.gl5, 33, Img.run_avg_cpu_util_all),
                        get_image_path(Workflow.DPP, 16, Node.gl5, 33, Img.run_avg_cpu_util_every)],
                       output_dir / "dpp-16nc-cpu_util-every-all-cmp.png")

glue_images_vertically([get_image_path(Workflow.DAA, 32, Node.gl5, 42, Img.run_avg_cpu_util_all),
                        get_image_path(Workflow.DPP, 32, Node.gl5, 35, Img.run_avg_cpu_util_all)],
                       output_dir / "32nc-workflow-cmp.png")

glue_images_vertically([get_image_path(Workflow.DPP, 4, Node.gl5, 32, Img.run_avg_cpu_util_every),
                        get_image_path(Workflow.DPP, 8, Node.gl5, 31, Img.run_avg_cpu_util_every),
                        get_image_path(Workflow.DPP, 16, Node.gl5, 31, Img.run_avg_cpu_util_every),
                        get_image_path(Workflow.DPP, 32, Node.gl5, 31, Img.run_avg_cpu_util_every)],
                       output_dir / "dpp-cpu_util_every-ncores-cmp.png")

# In[ ]:
