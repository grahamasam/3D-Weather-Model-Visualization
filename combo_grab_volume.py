from herbie import Herbie
import pandas as pd
import numpy as np
import pygrib  # For reading GRIB2 files
import vtk
from vtk.util.numpy_support import numpy_to_vtk
import requests
import os

"""
  Interesting variables in GRIB2 file:
  - 'Temperature'
  - 'Cloud mixing ratio'
  - 'Geopotential height'
  - 'Relative humidity'
  - 'Vertical velocity'
  - 'Absolute vorticity'
  - 'Dew point temperature'
  - 'Grauple (snow pellets)'
"""

VARIABLE = "Absolute vorticity"
GRIB_FILE_PATH = "temp_hrrr.grib2"
DATE = "2025-04-07"
START_TIME = 0
END_TIME = 5

def extract():
  # Define the date and forecast hour
  date = DATE

  for time in range(START_TIME, END_TIME):
    run_time = pd.Timestamp(f"{date} {time}:00")
    H = Herbie(run_time, model="hrrr", product="prs", fxx=0)

    records = H.inventory("HGT")
    print(records.head(10))  # Print the first 10 records

    # Get the remote GRIB2 file URL
    grib_url = H.grib
    print(grib_url)

    # Stream the file to a temporary location
    response = requests.get(grib_url, stream=True)
    response.raise_for_status()

    # Save the file locally
    with open(GRIB_FILE_PATH, "wb") as f:
      f.write(response.content)

    # extract VARIABLE 3d array
    convert(GRIB_FILE_PATH, date, time)

  os.remove(GRIB_FILE_PATH)


def convert(file_name, date, time):
  # Read GRIB2 Data
  grib_file = file_name 
  print(f"{VARIABLE}")

  # Open the GRIB2 file
  grbs = pygrib.open(grib_file)
  temp_msgs = grbs.select(name={VARIABLE}, typeOfLevel='isobaricInhPa')
  temp_msgs = [grb for grb in temp_msgs if 400 <= grb.level <= 1000]
  temp_msgs.sort(key=lambda grb: grb.level)
  grbs.close()

  # Initialize array with shape (num_levels, y, x)
  # Prepare array dimensions
  num_levels = len(temp_msgs)
  ny, nx = temp_msgs[0].values.shape
  temperature_3d = np.zeros((num_levels, ny, nx), dtype=np.float32)

  print(enumerate(temp_msgs))
  
  # Fill the array
  for i, grb in enumerate(temp_msgs):
    try:
      print(f"Reading level {grb.level} hPa ({i + 1}/{num_levels})")
      temperature_3d[num_levels-i-1, :, :] = grb.values
    except Exception as e:
      print(f"Error at level {grb.level} hPa: {e}")

  # Convert to vtkImageData ===
  nz, ny, nx = temperature_3d.shape 

  image_data = vtk.vtkImageData()
  image_data.SetDimensions(nx, ny, nz) 
  image_data.SetSpacing(1.0, 1.0, 1.0) 
  image_data.SetOrigin(0.0, 0.0, 0.0)

  temperature_flat = temperature_3d.ravel(order="C")
  vtk_array = numpy_to_vtk(num_array=temperature_flat, deep=True, array_type=vtk.VTK_FLOAT)
  vtk_array.SetName(f"{VARIABLE}")
  image_data.GetPointData().SetScalars(vtk_array)

  # Write to .vti file ===
  writer = vtk.vtkXMLImageDataWriter()
  writer.SetFileName(f"{VARIABLE}_{date}_{time:02d}.vti")
  writer.SetInputData(image_data)
  writer.Write()

  print(f"Successfully saved temperature volume as '{VARIABLE}.vti'")


if __name__ == '__main__':
  extract()