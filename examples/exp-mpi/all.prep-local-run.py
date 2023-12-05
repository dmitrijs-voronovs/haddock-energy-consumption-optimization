# configs = [
#               Config(workflow, ncores, node, trial)
#               for workflow in ["dpp", "daa"]
#               for node in get_list_intersection(["gl2", "gl6"], nodes)
#               for ncores in [2, 4, 8]
#               for trial in range(1, 11)
#           ] + [
#               Config(workflow, ncores, node, trial)
#               for workflow in ["dpp", "daa"]
#               for ncores in [16, 32]
#               for node in get_list_intersection(["gl6"], nodes)
#               for trial in range(1, 11)
#           ]