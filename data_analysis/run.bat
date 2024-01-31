python experiment.py get-data -d exp-local -c GL6_5
python experiment.py get-data -d exp-local -c GL5_5
python experiment.py get-data -d exp-local -c SS2_2
python experiment.py get-logs -d exp-local
python experiment.py clean -d exp-local
python experiment.py get-info -d exp-local -c GL6_5
python experiment.py get-info -d exp-local -c GL5_5
python experiment.py get-info -d exp-local -c SS2_2
python experiment.py gen-diagrams
python experiment.py gen-run-diagrams -d exp-local
