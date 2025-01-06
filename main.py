#/**
# * Copyright (C) 2007 Free Software Foundation, Inc. <https://fsf.org/> 
# * Written 2024 - by Stefano Padiglioni
# * University of Vienna, Departement of Pharmaceutical Technology
# * This Code is OpenSource, can be distributed freely and modified.
# * I opted for FreeSimpleGUI instead of PySimpleGUI since it is a forke of the OpensSource version. 
# * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either expressed or implied.
# */

import FreeSimpleGUI as sg
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from scipy import signal


##################################################################

#Define the Bin Size Here, equals number of rows in excel export

#binbin = 250

#Define the Range where to search for the Min Pressure (Sub Phase Inj.)
#window_range = 10000

##################################################################



#Create Image of Plot for Application (Static)
def draw_figure(canvas, figure):
    if canvas.children:
        for child in canvas.winfo_children():
            child.destroy()
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg


def read_csv_with_dynamic_header_skip(file_path):
    """
    Reads a CSV file, skipping rows until the header line is found.

    Parameters:
        file_path (str): The path to the CSV file.
        header_start (str): The start of the header line to find.

    Returns:
        pd.DataFrame: The DataFrame containing the CSV data.
    """
    # Open the file and find the header line
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    # Find the index of the header line
    header_index = next((i for i, line in enumerate(lines) if line.startswith("Nr;")), None)
    
    if header_index is None:
        raise ValueError(f"No header line starting with 'Nr;' found in the file.")
    
    return header_index

#Bin and average the data, Option = 1 for Default and Option = 2 only for Subphase
def bin_data_average (dt, Area_Range, option):
    #Combine common Area
    df_new = []

    for i in filenames:
        df_filtered = dt[dt["Dataframe_Indexing"]==i.split('/')[-1]]
        df_filtered[option].mask((df_filtered[option] < min(Area_Range)) | (df_filtered[option] > max(Area_Range)), inplace=True)
        df_new.append(df_filtered)
    
    #Combine and remove Nan Rows
    df_filtered = pd.concat(df_new, ignore_index=True)
    df_removed_nan = df_filtered.dropna(axis=0).reset_index(drop=True)
    
    #Import bin from Input
    try:
        binbin = int(values['-bin-'])

    except Exception as e:
        sg.popup(f'Error reading files (Default Value will be Used): {e}')
        binbin = 250

    #Create bins
    bins = np.linspace(min(Area_Range), max(Area_Range), binbin)

    #Separate by filename
    index = 0
    for i in filenames:
        df_filtered = df_removed_nan[df_removed_nan["Dataframe_Indexing"]==i.split('/')[-1]]
        df_filtered = df_filtered.loc[:, ~dfs.columns.isin(['Dataframe_Indexing'])]

        #Bin the data
        df_filtered["bin"] = pd.cut(df_filtered[option],bins, labels=False)
        binned_means = df_filtered.groupby('bin').mean()
        binned_means = binned_means.drop(columns='bin', errors='ignore')

        if index == 0:
            df_side_by_side = binned_means
        else:
            df_side_by_side = pd.concat([df_side_by_side, binned_means.reset_index(drop=True)], axis=1)
        index +=1
    
    return df_side_by_side


#Separate Dataframe to side by side for export
def separate_raw (dt):

    #Combine 
    df_new = []

    #Separate by filename
    index = 0
    for i in filenames:
        df_new = dt[dt["Dataframe_Indexing"]==i.split('/')[-1]]
        df_new = df_new.loc[:, ~dfs.columns.isin(['Dataframe_Indexing'])]

        df_new = df_new.add_suffix("File_" + str(index), axis=1)

        if index == 0:
            df_side_by_side_raw = df_new
        else:
            df_side_by_side_raw = pd.concat([df_side_by_side_raw, df_new.reset_index(drop=True)], axis=1)
        index +=1
    
    return df_side_by_side_raw

#Plotting
def plot_graphs(ax, df, xx, yy, av_df):

    for file in df["Dataframe_Indexing"].unique():
        dt_file = df[dataframe["Dataframe_Indexing"] == file]
        ax.plot(dt_file[xx].values, dt_file[yy].values, label=file.split('/')[-1])
                
    #Plot the average
    if not av_df.empty:
        ax.plot(av_df[xx].values, av_df[yy].values, label="Averaged")

    ax.set(xlabel=xx, ylabel=yy)
    ax.grid()

    #Show legend or not
    if values['-check_legend-'] == True:
        plt.legend()

    return fig



#Theme selection
sg.theme('DefaultNoMoreNagging')


# Define the menu layout
menu_def = [['File', ['Open', 'Save Binned Data', 'Save Raw Data'],],
            ['Help', "Info"]]

headings = ['Nr', 'TotalArea', 'Area', 'DeltaArea', 'DeltaMolecules', 'Pressure', 'Tension', 'Mode', 'Time', 'Temp', 'Potential', 'Radioactivity', 'area_mols','Compressibility modulus','Smoothened Compressibility modulus']

plots_list = ['Default', 'Compressibility modulus', 'Smoothened_Compr']


# Define the window layout

frame_layout1 = [
            [sg.Text('Choose x-axe'), sg.Combo(headings, expand_x=True,default_value=headings[2], enable_events=True,  readonly=False, key='-x_axes-')],
            [sg.Text('Choose y-axe'), sg.Combo(headings, expand_x=True,default_value=headings[5], enable_events=True,  readonly=False, key='-y_axes-')],
            [sg.Checkbox('Show Legend', default=True, key='-check_legend-', enable_events=True), sg.Checkbox('Sub-Phase Inj.', default=False, key='-check_subinj-', enable_events=True), sg.Checkbox('Cut', default=False, disabled=True, key='-cut-', enable_events=True), sg.Button('Refresh', key='-btn-refresh-',disabled=True, enable_events=True)]                 
    ]


sping_option = list(range(2,201,1))

frame_layout2 = [
            [sg.Text('Choose Plot Type'), sg.Combo(plots_list, default_value=plots_list[0] ,expand_x=True, enable_events=True,  readonly=False, key='-Plots-')],
            [sg.Text('Curve smoothening n='), sg.Spin(sping_option, s=(200,2), enable_events=True, key='-spin_curve-', size=(10,20))],  
            [sg.Button('Analyze Graph', key='-btn-analyze-', enable_events=True), sg.Text('Bin Size: '), sg.Input(default_text='250', key='-bin-', size=(10,20)), sg.Text('Cut Pos: '), sg.Input(default_text='1000', key='-cut_pos-', size=(10,20))],
                           
    ]

layout = [
    [sg.Menu(menu_def)],
    [sg.Canvas(key='-CANVAS-', size=(500, 400)), [sg.Frame('Plot', frame_layout1), sg.Frame('Options', frame_layout2)]],
    [sg.Text('Select Table'), sg.Combo("Empty", expand_x=True, enable_events=True,  readonly=False, key='-list_tables-')],
    [sg.Table(values=[[]], headings=headings, key='-TABLE-', auto_size_columns=True, display_row_numbers=True, justification='left', vertical_scroll_only=False)]
]

# Create the Window with a reasonable size
window = sg.Window('Langmuirer', layout, size=(950, 780), finalize=True, resizable=False)
dataframe = pd.Series({'A' : []})


#Main
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break
    elif event == 'Open' or event == '-btn-refresh-':
        if event == 'Open':
            filenames = sg.popup_get_file('Select files', multiple_files=True, file_types=(("NTB Files", "*.ntb"),("All Files", "*")), no_window=True)
            try:
                if filenames:
                    window['-btn-refresh-'].update(disabled = False)
            except:
                sg.popup(f'Error no files selected')

        if filenames:
        
            if values['-check_subinj-'] == False:
                window['-Plots-'].update(set_to_index=0, value=plots_list[0], values=plots_list, disabled = False)
                window['-spin_curve-'].update(disabled = False)
                window['-x_axes-'].update(set_to_index=2, value=headings[2], values=headings)
                window['-y_axes-'].update(set_to_index=5,value=headings[5], values=headings)
                
            else:
                window['-x_axes-'].update(set_to_index=8, value=headings[8], values=headings)
                window['-y_axes-'].update(set_to_index=5, value=headings[5], values=headings)
        

            try:
                #Initialize Plot
                fig, ax = plt.subplots()
                
                # Read multiple CSV files into a single DataFrame and group
                appended_data = []
                index = 0

                #Isotherm or Sub Phase inj Mode
                if values['-check_subinj-'] == False:
                    option_av = 0 #Default method for Isotherm
                    option_txt = "Area"
                else:
                    option_av = 1 #Adapted for the Sub Phase
                    option_txt = "Time"
              

                for file in filenames:
                    
                    dfs = None

                    #Check which rows to skip
                    skiprows_out = read_csv_with_dynamic_header_skip(file)

                    dfs = pd.read_csv(file, skiprows=skiprows_out, delimiter=";", dtype=float)

                    
                    #Cut the Subphase to lowest dip
                    if values['-cut-'] == True:
                        #Import value
                        try:
                            window_range = int(values['-cut_pos-'])

                        except Exception as e:
                            sg.popup(f'Error reading files (Default Value will be Used): {e}')
                            window_range = 1000

                        min_indx = dfs["Pressure"][0:window_range].idxmin()

                        #Moving the Time to the left, also the max values need to be moved
                        dfs["Time"]-=dfs["Time"][min_indx]

                        dfs = dfs[min_indx:]
                        

                    else:
                        pass
                        

                    #Search for absolute min/max area value, needed for average
                
                    if index == 0:

                        max_var = dfs[option_txt].max(numeric_only=True).max()
                        min_var = dfs[option_txt].min(numeric_only=True).min()
                            
                    else:

                        #Fin max bin value
                        if max_var > dfs[option_txt].max(numeric_only=True).max():
                            max_var = dfs[option_txt].max(numeric_only=True).max()
                     
                        #Find min bin value
                        if min_var < dfs[option_txt].min(numeric_only=True).min():
                            min_var = dfs[option_txt].min(numeric_only=True).min()


                    index += 1


                    #Add indexing
                    dfs["Dataframe_Indexing"] = file.split('/')[-1]
                    
                    if values['-check_subinj-'] == False:

                        #Compressibility modulus
                        dfs["Compressibility modulus"] = -dfs["Area"] * (dfs["Pressure"].sort_values(ascending=True).diff()/dfs["Area"].diff())
                        
                        #Column for Smoothened value
                        dfs["Smoothened Compressibility modulus"] = dfs["Area"].empty

                        ax.set_title("Isotherm")
                    else:
                        ax.set_title("Subphase Injection")


                    #Plot
                    ax.plot(dfs[values['-x_axes-']].values, dfs[values['-y_axes-']].values, label=file.split('/')[-1])

                    #append Dataframes
                    appended_data.append(dfs)

                    #Combine Dataframes
                    dataframe = pd.concat(appended_data, ignore_index=True)
                        
                    
                #Return binned and averaged values
             
                Area_Range = [min_var, max_var]
  
                df_side_by_side = bin_data_average(dataframe, Area_Range, option_txt)
        
                #Calculate the averaged and plot
                averaged_df = df_side_by_side.groupby(axis=1, level=0).mean()
                ax.plot(averaged_df[values['-x_axes-']].values, averaged_df[values['-y_axes-']].values, label="Averaged")
                ax.set(xlabel=values['-x_axes-'], ylabel=values['-y_axes-'])
                ax.grid()

                #Grid
                if values['-check_legend-'] == True:
                    plt.legend()
                else:
                    pass

                # Create Figure from plot   
                draw_figure(window['-CANVAS-'].TKCanvas, fig)
                    
                # Update the table and list
                window['-TABLE-'].update(values=dfs.loc[:, ~dfs.columns.isin(['Dataframe_Indexing'])].values.tolist())
                window['-list_tables-'].update(values=dataframe["Dataframe_Indexing"].unique().tolist())

                if event == 'Open':
                    sg.popup('Files Uploaded Successfully')
    
            except Exception as e:
                sg.popup(f'Error reading files: {e}')

    elif event == "Info":
        sg.popup('There is no Help!')

    elif event == "Save Binned Data":
        file_save_loc = sg.popup_get_file('Save Binned Data', save_as=True, default_extension = ".xlsx", no_window=True)
        
        #export
        try:
            sg.popup_auto_close("Saving...")
            df_av = averaged_df.add_suffix('_average')
            df_export = pd.concat([df_side_by_side, df_av.reset_index(drop=True)], axis=1)
            df_export.to_excel(file_save_loc, engine='xlsxwriter')
            sg.popup_auto_close("Done!")

        except Exception as e:
            sg.popup(f'Error reading files: {e}')

    elif event == "Save Raw Data":
        file_save_loc = sg.popup_get_file('Save Raw Data', save_as=True, default_extension = ".xlsx", no_window=True)
        
        #export
        try:
            sg.popup_auto_close("Saving...")
            
            df_export = separate_raw(dataframe)
            df_export.to_excel(file_save_loc, engine='xlsxwriter')
            sg.popup_auto_close("Done!")

        except Exception as e:
            sg.popup(f'Error reading files: {e}')


    #Update Graph with combo selection
    if event == '-x_axes-' or event == '-y_axes-' or event == '-Plots-':
        if values['-Plots-'] == 'Default':
            #Set plot combo box to default
            window['-Plots-'].update(set_to_index=0, value=plots_list[0], values=plots_list)

            if values['-Plots-'] == "Default":
                if not dataframe.empty:
                    
                    fig, ax = plt.subplots()

                    fig = plot_graphs(ax, dataframe,values['-x_axes-'], values['-y_axes-'], averaged_df)

                    draw_figure(window['-CANVAS-'].TKCanvas, fig)
                    
                    #Update the table
                    window['-TABLE-'].update(values=dfs.values.tolist())


    #Analyze via Matplotlib
    if event == '-btn-analyze-':
    
        if not dataframe.empty:

            fig, ax = plt.subplots()

            if values['-Plots-'] == "Default":  
                
                fig = plot_graphs(ax, dataframe, values['-x_axes-'], values['-y_axes-'], averaged_df)

            elif values['-Plots-'] == "Compressibility modulus":  

                fig = plot_graphs(ax, dataframe, "Pressure", "Compressibility modulus", pd.DataFrame({'A' : []}))   

            fig.show()
                

    #Update Table after selection
    if event == '-list_tables-':
        if not dataframe.empty:
           dfs_filtered = dataframe[dataframe["Dataframe_Indexing"]==values['-list_tables-']]
           window['-TABLE-'].update(values=dfs_filtered.loc[:, ~dfs_filtered.columns.isin(['Dataframe_Indexing'])].values.tolist())
    


    #Compressibility modulus
    if event == '-Plots-':
        if not dataframe.empty:
            if values['-Plots-'] == "Compressibility modulus":
                
                fig, ax = plt.subplots()

                fig = plot_graphs(ax, dataframe, "Pressure", "Compressibility modulus", pd.DataFrame({'A' : []}))  

                ax.set(xlabel='Surface Pressure', ylabel='Compressibility modulus')
                ax.set_title("Compressibility modulus smoothened")

                draw_figure(window['-CANVAS-'].TKCanvas, fig)



    #Smoothened COmpressibility
    if event == '-Plots-' or event == '-spin_curve-':
        if not dataframe.empty and values['-Plots-'] == "Smoothened_Compr":
            
                n = values['-spin_curve-']  # the larger n is, the smoother curve will be
                b = [1.0 / n] * n
                a = 1
                
                fig, ax = plt.subplots()

                for file in dataframe["Dataframe_Indexing"].unique():
                    dt_file = dataframe[dataframe["Dataframe_Indexing"] == file]
                    data = dt_file["Compressibility modulus"].fillna(0)
                    yy = signal.filtfilt(b, a, data.to_numpy())
                    dataframe.loc[dataframe["Dataframe_Indexing"] == file, "Smoothened Compressibility modulus"] = yy
                    ax.plot(dt_file["Pressure"].values, yy, label=file.split('/')[-1])

                ax.set(xlabel='Surface Pressure', ylabel='Compressibility modulus')
                ax.set_title("Compressibility modulus smoothened")
                ax.grid()
                
                #Show legend or not
                if values['-check_legend-'] == True:
                    plt.legend()

                draw_figure(window['-CANVAS-'].TKCanvas, fig)

                # Update the table and list
                window['-list_tables-'].update(set_to_index=0, values=dataframe["Dataframe_Indexing"].unique().tolist())
                window['-TABLE-'].update(values=dfs.loc[:, ~dfs.columns.isin(['Dataframe_Indexing'])].values.tolist())


    #Subphase      
    if event == '-check_subinj-':
        if values['-check_subinj-'] == True:
            window['-spin_curve-'].update(disabled = True)
            window['-Plots-'].update(disabled = True) 
            window['-x_axes-'].update(set_to_index=8, value=headings[8], values=headings)
            window['-y_axes-'].update(set_to_index=5,value=headings[5], values=headings)
            window['-cut-'].update(disabled = False)
    
        else:
            window['-spin_curve-'].update(disabled = False)
            window['-Plots-'].update(disabled = False)
            window['-x_axes-'].update(set_to_index=2, value=headings[2], values=headings)
            window['-y_axes-'].update(set_to_index=5,value=headings[5], values=headings) 
            window['-cut-'].update(disabled = True)
      
    #Cut
    if event == '-cut-':
        if values['-cut-']:
            window['-check_subinj-'].update(disabled = True)
        else:
            window['-check_subinj-'].update(disabled = False)


window.close()
