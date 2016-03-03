#![Logo](https://cecs.anu.edu.au/sites/default/files/styles/anu_doublenarrow_440_scale/public/images/rogas-web.jpg?itok=JfEfhc1_)
Rogas is a project for Network Analytics

Currently the Rogas project contains a framework for network analytics called RG Framework. 
It not only can provides a high-level declarative query language to 
formulate analysis queries, but also can unify different graph algorithms 
within the relational environment for query processing.
<br>
<br>
The RG framework has three main components: (1) a hybrid data model, which 
integrates graphs with relations so that we have these two types of data 
structures respectively for network analysis and relational analysis; 
(2) a SQL-like query language, which extends standard SQL with 
graph constructing, ranking, clustering, and path finding operations; 
(3) a query engine, which is built upon PostgreSQL and can efficiently process 
network analysis queries using various graph systems and 
their supporting algorithms.
<br>
<br>
Here is the prototype implementation of the RG Framework. The prototype
is developed in **Python 2.7** with the official PostgreSQL client library – libpq. 
We use **Psycopg**, the current mature wrapper for the libpq, as the 
PostgreSQL adapter. For the GUI, we use **TkInter**, **PIL**, and **pylsytable**
for window development, image formating and table-like printing. In terms of 
graph algorithms, currently, we take advantage of **Graph-tool**, **SNAP** and 
**NetworkX** for algorithms support.
<br>
<br>
Here are the links for the python packages above:
<br>
(suggest to use Ubuntu or other Linux systems, Mac and Windows are hard to install all these packages)
* Psycopg: http://initd.org/psycopg/
* TkInter: https://wiki.python.org/moin/TkInter
* Pillow for PIL: https://python-pillow.github.io/  (Require Pillow 3.1 or above)
* pylsytable: https://github.com/Leviathan1995/Pylsy?files=1
* Graph-tool: http://graph-tool.skewed.de/
* SNAP: http://snap.stanford.edu/snappy/index.html
* NetworkX: http://networkx.github.io/
<br>
<br>
Before runing the prototype, ensure the system is Ubuntu and all the external 
python packages mentioned above are installed correctly. 
<br>
<br>
*Notice that pillow is 
the latest package for PIL and it is not compatible with the old PIL package. 
If your have already had PIL in your python dist-packages (/usr/lib/python2.7/dist-packages/),
please delete the original PIL and install the new Pillow package. If you are using Eclipse or 
other IDE I suggest using source code to install Pillow so that the unresolved import 
issues of the IDE can be solved.* 
<br>
<br>
You also need to change the code of the *queryConsole.start()* method a bit 
to connect your own PostgreSQL database. Then you can start the prototype 
by running the *GUI_Console* program.
<br>
<br>
More details about the RG framework, please refer to 
the thesis "Towards a Unified Framework for Network Analytics" collected in 
Australian National University (the link is to be published). You can also 
contact *u5506264@anu.edu.au* or *qing.wang@anu.edu.au* for more information.
