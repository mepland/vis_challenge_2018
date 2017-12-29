# 2018 Scholars@Duke Visualization Challenge
Matthew Epland  
matthew.epland@duke.edu  

Work for the [2018 Scholars@Duke Visualization Challenge](https://rc.duke.edu/scholars-vis-challenge-2018)  

## Prerequisites
```bash
pip install pandas
pip install jupyter
pip install matplotlib
pip install networkx==1.11
pip install visJS2jupyter
pip install python-louvain
```

## Running
### 

### Creating edges from original data
```bash
python -u build_edges.py 2>&1 | tee last.log
```

### Creating graph from edges, and manipulating it
```bash
jupyter notebook graph.ipynb
```

