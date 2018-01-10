# 2018 Scholars@Duke Visualization Challenge
Matthew Epland  
matthew.epland@duke.edu  

Work for the [2018 Scholars@Duke Visualization Challenge](https://rc.duke.edu/scholars-vis-challenge-2018)  

## Prerequisites
```bash
pip install pandas
pip install matplotlib
pip install jupyter
jupyter nbextension enable --py widgetsnbextension
networkx
pip install visJS2jupyter
pip install python-louvain
```

### networkx 2.x from master
In order to use the new [random\_state](https://github.com/networkx/networkx/blob/a8a51d4763b01c034349fbc752713f47c637a81f/networkx/drawing/layout.py#L294) parameter of `spring\_layout` you must install `networkx` from the master. Do this before installing visJS2jupyter and python-louvain.
```bash
cd /where/you/would/like/to/install
git clone git@github.com:networkx/networkx.git
cd networkx
pip install -e .
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

