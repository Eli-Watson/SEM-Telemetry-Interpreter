 ____  _____ __  __  ____                 _
/ ___|| ____|  \/  |/ ___|_ __ __ _ _ __ | |__
\___ \|  _| | |\/| | |  _| '__/ _` | '_ \| '_ \
 ___) | |___| |  | | |_| | | | (_| | |_) | | | |
|____/|_____|_|  |_|\____|_|  \__,_| .__/|_| |_|
                                   |_|

Python script (borderline application) to create graphs using telemetry data collected and provided by Shell and Schmitd Elektronik at the Shell Eco Marathon. 
By Eli Watson

Telemetry reffrence: https://telemetry.sem-app.com/wiki/doku.php/telemetry_data/channel_descriptions

## Get Started
### Installation
1. Install prerequisites Python, Plotly, Pandas, pyfiglet using package manager of choice
2. clone the repo
3. place telemetry data in "Data" with corresponding sub folder
3. run "python SEMGraph.py" and start making graphs!

### User guide
if you are ever unsure of a command, simply type 'help' <command name> to get a short discription of the command.

#### Commands:
- graph: creates a set of useful graphs from one dataset
- graph_select: lets you choose a spesific graph to create
- help: shows info about commands
- quit: quits the application