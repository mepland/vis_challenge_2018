# 2018 Scholars@Duke Visualization Challenge
Matthew Epland  
matthew.epland@duke.edu  

Work for the [2018 Scholars@Duke Visualization Challenge](https://rc.duke.edu/scholars-vis-challenge-2018)  

## Brief Abstract
This submission to the 2018 Scholars@Duke Visualization Challenge explored the nature of interdisciplinary research at Duke through the study of Ph.D. committee membership for the 2013-2017 academic years. By combining the committee membership data with the faculty appointments directory, connections between different academic organizations were found and used to construct an undirected, weighted graph. From this graph communities of closely connected organizations were created via the Louvain method. The majority of communities fell along the typical disciplinary divisions, with a few interesting exceptions in Neurology, and Biology - Evolutionary Anthropology. Additionally, the level of interdisciplinary activity in each organization was measured by comparing the relative weights of their external and self connections, which showed potentially lower levels interdisciplinary activity in the Physics, Psychology and Neuroscience, and Philosophy departments. Lastly, future directions and areas of improvement for the analysis were identified, along with possible solutions.  

## Documentation
Please see the included poster and paper for further details.  
An interactive version of the academic organizations graph for all years may also be viewed online at [http://bl.ocks.org/mepland/raw/598590f30f49b17dc76ea4ed74695252](http://bl.ocks.org/mepland/raw/598590f30f49b17dc76ea4ed74695252)  

## Installing Dependencies
```bash
pip install pandas
pip install matplotlib
pip install jupyter
jupyter nbextension enable --py widgetsnbextension
networkx
pip install visJS2jupyter
pip install python-louvain
```

### Installing networkx from master
In order to use the new [random\_state](https://github.com/networkx/networkx/blob/a8a51d4763b01c034349fbc752713f47c637a81f/networkx/drawing/layout.py#L294) parameter of `spring_layout` you must install [`networkx`](https://github.com/networkx/networkx) from the master as it is included in version 2.0. Do this before installing visJS2jupyter and python-louvain.  
```bash
cd /where/you/would/like/to/install
git clone git@github.com:networkx/networkx.git
cd networkx
pip install -e .
```

## Running
### 

### Creating graph edges from the original xlsx data
```bash
cd edges
python -u build_edges.py 2>&1 | tee last.log
```

### Creating the actual graph from edges, and manipulating it / producing plots
```bash
cd graph
jupyter notebook graph.ipynb
```

