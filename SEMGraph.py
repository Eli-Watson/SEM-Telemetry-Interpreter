# Bearcat Motorsports Data Visualization Cli Tool
# my attempt at a cli python program - Eli Watson 4/3/25 (Comp Softmore Year)
#Goals of script :
#- Be able to select wether or not to use the newest data set or manually enter wich one
#- Be able to select what out of the preset graphs is needed
#- Be able to output to a more human readable format

import cmd
import os
import pandas as pd
import plotly.io as pio
import plotly.graph_objects as go

class CLI(cmd.Cmd):
    prompt = '>> '
    intro = 'Welcome to the Shell Eco Marathon Graphing (SEMGraph) tool. Type "help" for available commands. By Eli Watson'
    def do_quit(self, line):
        """Exit the CLI."""
        print("Are you sure you want to quit?")
        confirmquit = input("y or n: ")
        if confirmquit.lower() == "y":
            return True
        else:
            print("Quit cancelled")

    def select_data_file(self):
        """Helper method to handle file selection process."""
        print('What Data Directory would you like to list? U for Urban P for Proto or S for Sample data?')
        selected_dir = input('u, p, or s? ')
        dir_to_list = ''
        match selected_dir:
            case "u":
                dir_to_list = "./Data/Urban/"
            case "p":
                dir_to_list = "./Data/Proto/"
            case "s":
                dir_to_list = "./Data/Sample/"
            case _:
                print("Invalid selection. Please choose 'u', 'p', or 's'.")
                return None, None

        if os.path.exists(dir_to_list):
            files = os.listdir(dir_to_list)
            print(f"Files in {dir_to_list}:")
            for file in files:
                print(file)
        else:
            print(f"Directory {dir_to_list} does not exist.")
            return None, None

        # Ask for the file to graph
        graphing_source = input("What Data file would you like to Graph? (Enter the file name): ")
        file_path = os.path.join(dir_to_list, graphing_source)
        
        if not os.path.exists(file_path):
            print(f"Error: The file '{graphing_source}' does not exist in the directory '{dir_to_list}'")
            return None, None

        return file_path, dir_to_list

    def generate_graph(self, df, graph_type):
        """Helper method to generate graphs based on user selection."""
        if graph_type == 'map':
            print('Generating map...')
            fig = df.plot(x='gps_longitude', y='gps_latitude', color='lap_lap')
        elif graph_type == 'map-flow':
            print('Generating map-flow...')
            fig = df.plot(x='gps_longitude', y='gps_latitude', color='lfm_instantflow', kind='scatter', facet_col='lap_lap', facet_col_wrap=4)
        elif graph_type == 'flow-dist':
            print('Generating flow-dist...')
            fig = df.plot(x='lap_dist', y='lfm_instantflow', color='lap_lap')
        elif graph_type == 'joule-dist':
            print('Generating joule-dist...')
            fig = df.plot(x='lap_dist', y='lap_jm3_netjoule', color='lap_lap')
        elif graph_type == 'speed-dist':
            print('Generating speed-dist...')
            fig = df.plot(x='lap_dist', y='gps_speed', color='lap_lap')
        elif graph_type == 'acel-speed-dotplot':
            print('Generating acel-speed-dotplot...')
            df['acceleration'] = 0.
            df['consumption'] = 0.
            window_len = 30

            for ind in range(window_len, len(df)):
                ind_prev = ind - window_len
                df.loc[ind, 'acceleration'] = (df.loc[ind, 'gps_speed'] - df.loc[ind_prev, 'gps_speed']) / (df.loc[ind, 'obc_timestamp'] - df.loc[ind_prev, 'obc_timestamp'])
                df.loc[ind, 'consumption'] = (df.loc[ind, 'lfm_integratedcorrflow'] - df.loc[ind_prev, 'lfm_integratedcorrflow']) / (df.loc[ind, 'obc_timestamp'] - df.loc[ind_prev, 'obc_timestamp'])

            fig = df.plot.scatter(x='acceleration', y='gps_speed', color='consumption')

        fig.show()

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
            print(f"Error reading CSV file: {e}")
            return

        # Ask for the graph type
        print("What graph type would you like to generate?")
        print('')
        print("map: a map of the course using GPS")
        print("map-flow: A GPS map of the track overlayed with data from flow meter")
        print("flow-dist: Flow rate at different distances")
        print("joule-dist: Net amount of energy used at different distances")
        print("speed-dist: Speed at different distances")
        print("acel-speed-dotplot: Dotplot of acceleration, speed and fuel consumption")
        print('')

        graph_type = input("What graph would you like to generate?: ")
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
            print(f"Error reading CSV file: {e}")
            return

        # Generate multiple graphs
        print("Generating graphs...")
        self.generate_graph(df, 'map')
        self.generate_graph(df, 'map-flow')
        self.generate_graph(df, 'flow-dist')
        self.generate_graph(df, 'joule-dist')
        self.generate_graph(df, 'speed-dist')
        self.generate_graph(df, 'acel-speed-dotplot')

if __name__ == '__main__':
    CLI().cmdloop()
