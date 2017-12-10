# ![Logo](https://cecs.anu.edu.au/sites/default/files/styles/anu_doublenarrow_440_scale/public/images/rogas-web.jpg?itok=JfEfhc1_)
Rogas(https://github.com/CornucopiaRG/Rogas) is a project for Network Analytics


## Introduction
Rogas not only can provides a high-level declarative query language to 
formulate analysis queries, but also can unify different graph algorithms 
within the relational environment for query processing.
<br>
<br>
The Rogas has three main components: (1) a hybrid data model, which 
integrates graphs with relations so that we have these two types of data 
structures respectively for network analysis and relational analysis; 
(2) a SQL-like query language, which extends standard SQL with 
graph constructing, ranking, clustering, and path finding operations; 
(3) a query engine, which is built upon PostgreSQL and can efficiently process 
network analysis queries using various graph systems and 
their supporting algorithms.
<br>
<br>

## Main Features
- Database info panel can show the schema information of relations and graphs in the database
- Query input panel can be extended to a larger space for complicated queries
- Show queries and their results as browser-tab style
- Asynchronous execution with loading animation
- Support regular relational queries and graph queries with graph operations (RANK, CLUSTER and PATH) 
- Show the result of a large table in pages 
- Support visualisation for graph queries with graph operations (RANK, CLUSTER and PATH) 
- Support interactive operations on graphs (drag, double click, zoom in/out) 
- Support relation - graph data mapping

## Work Screenshots
- Relational result for a query with the RANK operation
![rank_relation](https://scontent-lga3-1.xx.fbcdn.net/v/t31.0-8/21083342_919659161515806_4718643341927717323_o.jpg?oh=81f5de1ed9d8624c9e0632ed9d2a26dc&oe=5AD548D5)

- Graphical result for a query with the RANK operation
![rank_graph](https://scontent-lga3-1.xx.fbcdn.net/v/t31.0-8/21125702_919659144849141_8898442456570080374_o.jpg?oh=cfeb03e9819b3c09cf96d3b4cc383979&oe=5AC5F8E2)

- Relational result for a query with the CLUSTER operation
![cluster_relation](https://scontent-lga3-1.xx.fbcdn.net/v/t31.0-8/21125686_919659118182477_4669227882070502344_o.jpg?oh=e3abca76c59d4c49e809a4823460fc56&oe=5A8CFF4B)

- Graphical result for a query with the CLUSTER operation
![cluster_graph](https://scontent-lga3-1.xx.fbcdn.net/v/t31.0-8/21167343_919659121515810_4963809998576747306_o.jpg?oh=adb7b9153453c8447f0e20b9ce4a380b&oe=5ACDCA02)

- Relational result for a query with the PATH operation
![path_relation](https://scontent-lga3-1.xx.fbcdn.net/v/t31.0-8/21246579_919659138182475_5021826132940902360_o.jpg?oh=d07fe479ee5f36a5a044e638879af7dc&oe=5ABDDF08)

- Graphical result for a query with the PATH operation & Relation-Graph Mapping
![path_graph](https://scontent-lga3-1.xx.fbcdn.net/v/t31.0-8/21167515_919659134849142_7137453644422028625_o.jpg?oh=bbc0d66113c09715ffffd143fd2e2ffb&oe=5AD7D4DE)

- Database Info
![dbinfo](https://scontent-lga3-1.xx.fbcdn.net/v/t31.0-8/21246405_919659114849144_3518535802659986691_o.jpg?oh=12bc611ea150963c52825d14abf27586&oe=5AC35480)

## Process of Graph Visualization
### Graph Rank Operation 
- 1) Get targeted nodes based on the RANK result
- 2) Find nodes on the shortest path among the selected nodes
- 3) Find nodes around the selected nodes

### Graph Cluster Operation 
- 1) Rescale the size of each cluster according to the proportion
- 2) Score each node according to the inner-cluster edges, cluster-cluster edges and target node's degree
- 3) Find the max connected component in each cluster
- 4) Get certain amount (be specified in setting) of nodes in the max connected component from high score to low score
- 5) Find neighbor nodes around the selected nodes

### Graph Path Operation 
- 1) Get targeted nodes based on the PATH result
- 2) Find nodes around the selected nodes

## Dependencies 
* Python 2.7
* Tornado: http://www.tornadoweb.org/en/stable/
* Postgresql: https://www.postgresql.org/ 
* Psycopg: http://initd.org/psycopg/
* Graph-tool: http://graph-tool.skewed.de/
* SNAP: http://snap.stanford.edu/snappy/index.html
* NetworkX: http://networkx.github.io/  

Note: If you use Mac OS, the Graph-tool installed doesn't support OpenMP by default, you can change the  IS\_GRAPH\_TOOL\_OPENMP = False in rogas/config.py.
<br>
<br>
We also make use of Bootstrap(http://getbootstrap.com/), D3.js(https://d3js.org) and ExpandingTextareas(https://github.com/bgrins/ExpandingTextareas), which are integrated into the system so  you don't need install them by yourself.

## How to Run
- Set up your database information in rogas.config.py to connect to Postgresql
- Python run.py
- Open the browser by entering http://localhost:12345/

## Future Work
- 1) find a more informative naming strategy for different query tabs
- 2) improve the graph visualisation for large graphs (million or billion nodes), including implementing good layouts and improving the efficiency 
- 3) make the visualisation for PATH operations more informative, in particular of dealing with multiple paths
- 4) add more functions about user interaction, such as the content of graphs can correspondingly change when doing zoom-in/out
- 5) build an algorithm store that includes different types of algorithms for network analysis 

## More Information
More details about the Rogas, please refer to 
the thesis "Towards a Unified Framework for Network Analytics" collected in 
Australian National University (http://users.cecs.anu.edu.au/~u5170295/publications/thesis-minjian.pdf). You can also 
contact *minjian.liu@anu.edu.au* or *qing.wang@anu.edu.au* for more information.

## Instructor
Qing Wang (*qing.wang@anu.edu.au*)

## Contributors
- Minjian Liu (*minjian.liu@anu.edu.au*): design the system framework, the query language and the Rogas logo; construct the relation-graph hybrid data model; implement the query processing; implement the prototype GUI (the GUI shown in the VLDB2016 demo paper -- Rogas: A Declarative Framework for Network Analytics ), supervise the work of GSoC2016-ShallYan.
- Yan Xiao (*xiaoyanict@foxmail.com*): design and implement the Web GUI (the work of GSoC2016-ShallYan), design and implement the visualisation of graph operations(CREATE, RANK, PATH, CLUSTER), design and implement the backend server and modify the Rogas' query engine in order to fitting the front-end.
- Omid Rezvani (*mojtaba.rezvani@anu.edu.au*): implement the local community search functionality.
- Chong Feng (*u4943054@anu.edu.au*): implment the node-tree data structure and query caches for optimisation.
