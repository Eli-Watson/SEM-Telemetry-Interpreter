#  ____  _____ __  __  ____                 _
# / ___|| ____|  \/  |/ ___|_ __ __ _ _ __ | |__
# \___ \|  _| | |\/| | |  _| '__/ _` | '_ \| '_ \
#  ___) | |___| |  | | |_| | | | (_| | |_) | | | |
# |____/|_____|_|  |_|\____|_|  \__,_| .__/|_| |_|
#                                    |_|
# Shell Eco Marathon Graphing Tool
# By Eli Watson
# my attempt at a cli python program - Eli Watson 4/3/25 (Comp Softmore Year)
# I hope that this script is helpful in making graphs to interpret the telemetry data put out by shell.
# Special Thanks to Marcus Schmitd from Schmitd Elektronik for helping me learn all this and all the work they have done for SEM
# https://schmid-elektronik.ch/racebootcamp/
# https://telemetry.sem-app.com/wiki/doku.php/telemetry_data/channel_descriptions

import cmd
import os
import pandas as pd
import plotly.io as pio
import plotly.graph_objects as go
import pyfiglet
from colorama import Fore, init
import inquirer

# option for colorama to reset the color after each use, otherwise it changes for the entire program
init(autoreset=True)

class CLI(cmd.Cmd):
    prompt = '>> '
    welcome = 'Welcome to the Shell Eco Marathon Graphing (SEMGraph) tool. By Eli Watson, Bearcat Motorsports'

    # Helper Functions
    def print_banner(self):
        banner = pyfiglet.figlet_format("SEMGraph", font="standard")
        print(Fore.RED + banner)

    def preloop(self):
        # This method is automatically called before the CmdLoop starts.
        self.print_banner()  
        print(self.welcome)
        print('Type "Help" for a list of available options')

    def select_data_file(self):
        """Helper method to handle file selection process using inquirer."""
        print('What Data Directory would you like to list? Select from the list below with your arrow keys. Hit Enter over the option you want.')

        questions = [
            inquirer.List(
                "Dir",
                message=Fore.RED + "What Data dir would you like to list?",
                choices=["Urban", "Proto", "Sample"],
            ),
        ]
        question_dir = inquirer.prompt(questions)["Dir"]
        selected_dir = question_dir
        dir_to_list = ''

        match selected_dir:
            case "Urban":
                dir_to_list = "./Data/Urban/"
            case "Proto":
                dir_to_list = "./Data/Proto/"
            case "Sample":
                dir_to_list = "./Data/Sample/"

        if os.path.exists(dir_to_list):
            print(Fore.RED + f"Listing files in {dir_to_list}:")
            files = self.list_files_recursive(dir_to_list)
        else:
            print(Fore.YELLOW + f"Directory {dir_to_list} does not exist.")
            return None, None

        # inquirer prompt to select a file to graph
        if files:
            questions_files = [
                inquirer.List(
                    "graph_file",
                    message="Which file would you like to graph?",
                    choices=files,
                ),
            ]
            graphing_source = inquirer.prompt(questions_files)["graph_file"]
            print(graphing_source)
            file_path = os.path.join(dir_to_list, graphing_source)

            if not os.path.exists(file_path):
                print(Fore.YELLOW + f"Error: The file '{graphing_source}' does not exist in the directory '{dir_to_list}'")
                return None, None

            return file_path, dir_to_list
        else:
            print(Fore.YELLOW + f"No files found in {dir_to_list}.")
            return None, None

    def list_files_recursive(self, dir_path):
        """Recursively lists all files in a directory and its subdirectories."""
        all_files = []
        
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                # Append the full relative path of each file found
                relative_path = os.path.relpath(os.path.join(root, file), dir_path)
                all_files.append(relative_path)
        
        return all_files

    # These are the actual graphs being generated
    def generate_graph(self, df, graph_type):
        """Helper method to generate graphs based on user selection."""
        match graph_type:
            case 'Map':
                print('Generating map...')
                fig = df.plot(x='gps_longitude', y='gps_latitude', color='lap_lap')
            
            case 'Speed-Dist':
                print('Generating speed-dist...')
                fig = df.plot(x='lap_dist', y='gps_speed', color='lap_lap')
            
            case 'Map-Flow':
                print('Generating map-flow...')
                fig = df.plot(x='gps_longitude', y='gps_latitude', color='lfm_instantflow', kind='scatter', facet_col='lap_lap', facet_col_wrap=4)
            
            case 'Flow-Dist':
                print('Generating flow-dist...')
                fig = df.plot(x='lap_dist', y='lfm_instantflow', color='lap_lap')
            
            case 'Acel-Speed-Dotplot':
                print('Generating acel-speed-dotplot...')
                df['acceleration'] = 0.
                df['consumption'] = 0.
                window_len = 30

                for ind in range(window_len, len(df)):
                    ind_prev = ind - window_len
                    df.loc[ind, 'acceleration'] = (df.loc[ind, 'gps_speed'] - df.loc[ind_prev, 'gps_speed']) / (df.loc[ind, 'obc_timestamp'] - df.loc[ind_prev, 'obc_timestamp'])
                    df.loc[ind, 'consumption'] = (df.loc[ind, 'lfm_integratedcorrflow'] - df.loc[ind_prev, 'lfm_integratedcorrflow']) / (df.loc[ind, 'obc_timestamp'] - df.loc[ind_prev, 'obc_timestamp'])

                fig = df.plot.scatter(x='acceleration', y='gps_speed', color='consumption')
            
            case 'CorrFlow-Dist':
                print('Generating CorrFlow-Dist')
                fig = df.plot(x='lap_dist', y='lap_lfm_integratedcorrflow', color='lap_lap')
            
            case 'Joule-Dist':
                print('Generating joule-dist...')
                fig = df.plot(x='lap_dist', y='lap_jm3_netjoule', color='lap_lap')
            
            case 'BE-Joule-map':
                print('Generating BE-Joule-map...')
                fig = df.plot(x='gps_longitude', y='gps_latitude', color='jm3_current', kind='scatter', facet_col='lap_lap', facet_col_wrap=4)
            
            case 'Current-Dist':
                print('Generating Current-dist...')
                fig = df.plot(x='lap_dist', y='jm3_current', color='lap_lap')
            
        fig.show()

    # Commands 
    def do_quit(self, line):
        """Exit the CLI."""
        print(Fore.RED + "Are you sure you want to quit?")
        confirmquit = input("y or n: ")
        if confirmquit.lower() == "y":
            quit()
        else:
            print("Quit cancelled")

    def do_graph_select(self, line):
        """Generate a specific graph from a list of options."""
        print("Generating Graph...")

        file_path, _ = self.select_data_file()
        if not file_path:
            return
        
        # Read the data
        pd.options.plotting.backend = 'plotly'
        pio.templates.default = 'plotly_dark'
        try:
            df = pd.read_csv(file_path, sep=',', low_memory=False)
            df = df.loc[df['lap_dist'] < 4000]
        except Exception as e:
            print(Fore.YELLOW + f"Error reading CSV file: {e}")
            return

        # Graph Descriptions
        print(Fore.RED + "What graph type would you like to generate?")
        print('')
        print(Fore.RED + 'Engine Type Agnostic')
        print("Map: a map of the course using GPS")
        print("Speed-dist: Speed at different distances")
        print(Fore.RED + 'ICE Specific:')
        print("Map-Flow: A GPS map of the track overlayed with data from the flow meter")
        print("Flow-Dist: Flow rate at different distances")
        print("Acel-Speed-Dotplot: Dotplot of acceleration, speed, and fuel consumption")
        print("CorrFlow-Dist: The lifetime fuel flow in relation to distance")
        print(Fore.RED + "BE Specific:")
        print("Joule-Dist: Net amount of energy used at different distances")
        print("BE-Joule-map: A GPS map of the course overlayed by energy consumption")
        print("Current-Dist: Current consumption at different points in the track")

        # Uses inquirer to select from a list
        questions = [
            inquirer.List(
                "type",
                message=Fore.RED + "Select a Graph",
                choices=["Map", "Speed-Dist", "Map-Flow", "Flow-Dist", "Acel-Speed-Dotplot", 'CorrFlow-Dist', "Joule-Dist",  'BE-Joule-map', 'Current-Dist',]
            ),
        ]
        graph_type = inquirer.prompt(questions)["type"]
        print(graph_type)
        self.generate_graph(df, graph_type)

    def do_graph(self, line):
        """Generate standard graphs from the telemetry data."""
        print("Generating Standard Graph Set.")
        
        file_path, _ = self.select_data_file()
        if not file_path:
            return
        
        # Read the data
        pd.options.plotting.backend = 'plotly'
        pio.templates.default = 'plotly_dark'

        try:
            df = pd.read_csv(file_path, sep=',', low_memory=False)
            df = df.loc[df['lap_dist'] < 4000]
        except Exception as e:
            print(Fore.YELLOW + f"Error reading CSV file: {e}")
            return

        # Generate multiple graphs
        print("Generating graphs...")
        self.generate_graph(df, 'map')
        self.generate_graph(df, 'map-flow')
        self.generate_graph(df, 'flow-dist')
        self.generate_graph(df, 'CorrFlow-Dist')
        self.generate_graph(df, 'speed-dist')
        self.generate_graph(df, 'acel-speed-dotplot')

if __name__ == '__main__':
    CLI().cmdloop()
