def getCreateCommand(workflow, ncores, nodes, node, trial, is_warmup=False):
    return f"sh create-mpi-job.sh {workflow} {ncores} {nodes} {ncores // nodes} {node} {trial}{' warmup' if is_warmup else ''}"


commands = [
    getCreateCommand(workflow, ncores, nodes, node, trial)
    for workflow in ["dpp", "daa"]
    for node in ["gl2", "gl6"]
    for (ncores, nodes) in [(2, 2), (4, 4), (8, 8)]
    for trial in range(1, 11)
] + [
    getCreateCommand(workflow, ncores, nodes, node, trial)
    for workflow in ["dpp", "daa"]
    for node in ["gl6"]
    for (ncores, nodes) in [(16, 16), (32, 32)]
    for trial in range(1, 11)
] + [getCreateCommand("dpp", 8, 8, "gl2", 1, True), getCreateCommand("dpp", 8, 8, "gl6", 1, True)]


for command in commands:
    print(command)

with open("all.create-mpi-job.sh", "w") as file:
    file.writelines("#!/bin/bash/ \n")
    file.writelines("\n".join(commands))
