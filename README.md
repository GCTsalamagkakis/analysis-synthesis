# Description
 Analysis and synthesis tool for sequential circuits made with Python.  
<br>
Final product should look like this:
<br>
Analysis:
<br>
![Photo Link](http://i.epvpimg.com/48Nnbab.png)
<br>
Synthesis:
<br>
![Photo Link](http://i.epvpimg.com/D6Q4eab.png)

# Modules required
* PyQt5
* Anytree

# Installation
1. Install python 3+
2. `pip install pyqt5` (Required for UI)
3. `pip install anytree` (Required for Synthesis)
4. Run `python main.py`

# Analysis
User submits a json file with gates information.  
For example:
```
"AN_ID": {
  "type": "and",
  "inputs": [
    {"id": "SOME_ID"},{"id": "SOME_OTHER_ID"}
  ],
  "outputs": [
    {"id": "SOME_OTHER_ID"}
  ],
  "isGate": true
}
```
###### All id's are numeric and cannot be duplicates.
For more examples check [here](https://github.com/GCTsalamagkakis/analysis-synthesis/blob/master/example-Analysis/example1.json).

# Synthesis
User submits a txt file with states information.  
For example:
```
0 --> 0 (0/0)
0 --> 0 (1/0)
1 --> 1 (0/0)
1 --> 1 (1/1)
```
###### One line per state, all states should be included even if not used.
###### States should be in the exact format given above.
For more examples check [here](https://github.com/GCTsalamagkakis/analysis-synthesis/blob/master/examples-Synthesis/example1.txt).

# Restrictions
* Files for Analysis must be json.
* Files for Synthesis must be txt.
* Synthesis supports up to 4 variables.
* For json and txt files format check the appropriate examples folders.
