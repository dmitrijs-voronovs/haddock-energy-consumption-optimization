python experiment.py get-data -d exp-local -c GL6_4
python experiment.py get-data -d exp-local -c GL5_4
python experiment.py get-data -d exp-local -c SS2
python experiment.py get-logs -d exp-local
python experiment.py clean -d exp-local
python experiment.py get-info -d exp-local -c GL6_4
python experiment.py get-info -d exp-local -c GL5_4
python experiment.py get-info -d exp-local -c SS2
python experiment.py gen-run-diagrams -d exp-local