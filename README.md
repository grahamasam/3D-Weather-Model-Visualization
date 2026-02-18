```
3D Weather Model Visualization
Graham Asam

______________________________

To run the visualization using the provided files, run the command:

python atmosphere_vis.py --folder1 clm_2025-04-08 0.0001 --folder2 temperature_2025-04-08 279 --pressure pressure_layer_2025-04-08

NOTE: requires the 'vtk_camera.py' helper file. It has been included in the submission files.
      requires 'vtk' and 'PyQt6'

______________________________
```
Example Images:

<table>
  <tr>
    <td><img src="https://github.com/grahamasam/3D-Weather-Model-Visualization/blob/main/report_images/Screenshot00000.png?raw=true" width="450"></td>
    <td><img src="https://github.com/grahamasam/3D-Weather-Model-Visualization/blob/main/report_images/Screenshot00001.png?raw=true" width="450"></td>
  </tr>
  <tr>
    <td><img src="https://github.com/grahamasam/3D-Weather-Model-Visualization/blob/main/report_images/cloud%20height%20diff.png?raw=true" width="450"></td>
    <td><img src="https://github.com/grahamasam/3D-Weather-Model-Visualization/blob/main/report_images/cold%20front%20fold.png?raw=true" width="450"></td>
  </tr>
  <tr>
    <td><img src="https://github.com/grahamasam/3D-Weather-Model-Visualization/blob/main/report_images/differing%20cloud%20height.png?raw=true" width="450"></td>
    <td><img src="https://github.com/grahamasam/3D-Weather-Model-Visualization/blob/main/report_images/precip%20and%20cold%20front.png?raw=true" width="450"></td>
  </tr>
</table>

```
______________________________

Usage for atmosphere.py:

python atmosphere_vis --folder1 <name of folder1> <isovalue> --folder2 <name of folder2> <isovalue> --pressure <name of pressure layer folder>

  ** --folder1 ** takes in two values:
    <name of folder1> <- the name of the folder containing the .vti files for all the 3d 
                         arrays for a particular variable to be visualized (see folder 
                         "temperature_2025_4-08" or "clm_2024-04-08" for an example). 
                         These files can be generated for any date in the HRRR archive 
                         using the "combo_grab_volume.py" script. Read 'Get Data' section 
                         for usage details.
    <isovalue>        <- the isovalue that will be used to extract the isosurface for the 
                         folder1 model variable.

  ** --folder2 ** same as folder1, arrays for a different variable and isovalue to visualize.

  ** --pressure ** takes in one value:
    <name of pressure layer folder> <- the name of the folder containing the .vti files for 
                                       all the arrays containing the height of each grid 
                                       point for the 1000 hPa pressure layer (see folder 
                                       "pressure_layer_2025-04-08" for an example). These 
                                       files can be generated for any date in the HRRR archive 
                                       using the "pressure_layer_time_extract.py" script. 
                                       Read 'Get Data' section for usage details.

______________________________

Get Data:

combo_grab_volume.py  

  NOTE: the imports 'numpy', 'pandas', 'Herbie', and 'pygrib' are required to run the
        script.
	
  Install pygrib with conda (annoying dependencies required otherwise):
    'conda install -c conda-forge pygrib'
  Install Herbie with pip (no conda installation avialable):
    'pip install herbie-data'

  Usage: python combo_grab_volume.py

  Several global variables at the top of the file control what information is retrieved.
    VARIABLE - change what variable is extracted from the GRIB2 file.
               A list of possible variable names is included at the top of the 
               "combo_grab_volume.py" file.
    DATE - change what date the data is taken from.
    GRIB_FILE_PATH - a temporary file is created at this location to store the
                     GRIB2 file while information is extracted.
    START_TIME - The timestep to begin extracting data from on date DATE.
                 (times are of form 0,1,2,...,24 for a single day)
    END_TIME - The timestep to end extracting data from on date DATE.

pressure_layer_time_extract.py

  NOTE: the imports 'numpy', 'pandas', 'Herbie', and 'pygrib' are required to run the
        script.
  
  Install pygrib with conda (annoying dependencies required otherwise):
    'conda install -c conda-forge pygrib'
  Install Herbie with pip (no conda installation avialable):
    'pip install herbie-data'

  Usage: python pressure_layer_time_extract.py

  Same global variables as combo_grab_volume.py, with one additional variable.
    TARGET_LEVEL - change which pressure layer is extracted (HRRR has pressure layers
                   at 25 hPa increments: 1000, 975, 950, ...).
```







