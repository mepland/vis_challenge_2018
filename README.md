# 2018 Scholars@Duke Visualization Challenge
Matthew Epland  
matthew.epland@duke.edu  

Work for the [2018 Scholars@Duke Visualization Challenge](https://rc.duke.edu/scholars-vis-challenge-2018)  

## Abstract
This submission to the 2018 Scholars@Duke Visualization Challenge explored the nature of interdisciplinary research at Duke through the study of Ph.D. committee membership for the 2013-2017 academic years. By combining the committee membership data with the faculty appointments directory, connections between different academic organizations were found and used to construct an undirected, weighted graph. From this graph communities of closely connected organizations were created via the Louvain method. The majority of communities fell along the typical disciplinary divisions, with a few interesting exceptions in Neurology, and Biology - Evolutionary Anthropology. Additionally, the level of interdisciplinary activity in each organization was measured by comparing the relative weights of their external and self connections, which showed potentially lower levels interdisciplinary activity in the Physics, Psychology and Neuroscience, and Philosophy departments. Lastly, future directions and areas of improvement for the analysis were identified, along with possible solutions.  

## Documentation
Please see the included poster and paper for further details.  
An interactive version of the academic organizations graph for all years may also be viewed online at [http://bl.ocks.org/mepland/raw/598590f30f49b17dc76ea4ed74695252](http://bl.ocks.org/mepland/raw/598590f30f49b17dc76ea4ed74695252)  

## Cloning the Repository
ssh  
```bash
git clone git@github.com:mepland/vis_challenge_2018.git
```

https  
```bash
git clone https://github.com/mepland/vis_challenge_2018.git
```
## Installing Dependencies
It is recommended to work in a `virtualenv` to avoid clashes with other installed software. A useful extension for this purpose is [`virtualenvwrapper`](https://virtualenvwrapper.readthedocs.io/en/latest/). Follow the instructions in the documentation to install and initialize wrapper before continuing.  

```bash
mkvirtualenv newenv
pip install -r requirements.txt
jupyter nbextension enable --py widgetsnbextension
```

### Installing networkx from master
In order to use the new QOL [random\_state](https://github.com/networkx/networkx/blob/a8a51d4763b01c034349fbc752713f47c637a81f/networkx/drawing/layout.py#L294) parameter of `spring_layout` you must install [`networkx`](https://github.com/networkx/networkx) from the master as it is not included in the current version 2.0. The `requirements.txt` file will try to install a known working commit, but you are welcome to install directly from master (see below) or look for a new version 2.x tag.  
```bash
cd /where/you/would/like/to/install/networkx
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

