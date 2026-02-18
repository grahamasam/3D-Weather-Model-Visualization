import numpy as np
import pygrib
import vtk
from vtk.util.numpy_support import numpy_to_vtk
import os
import requests
from herbie import Herbie
import pandas as pd

VARIABLE = "Geopotential height"
GRIB_FILE_PATH = "temp_hrrr.grib2"
TARGET_LEVEL = 1000
DATE = "2025-04-07"
START_TIME = 0
END_TIME = 5

def extract():
  # Define the date
  date = DATE

  for time in range(START_TIME, END_TIME):
    run_time = pd.Timestamp(f"{date} {time}:00")
    H = Herbie(run_time, model="hrrr", product="prs", fxx=0)

    records = H.inventory("HGT")
    print(records.head(10))  # Print first 10 records

    # Get the remote GRIB2 file URL
    grib_url = H.grib
    print(grib_url)

    # Stream the file to a temporary location
    response = requests.get(grib_url, stream=True)
    response.raise_for_status()

    # Save the file locally
    with open(GRIB_FILE_PATH, "wb") as f:
      f.write(response.content)

    # extract pressure layer geopotential height values
    convert(GRIB_FILE_PATH, date, time)

  os.remove(GRIB_FILE_PATH)

def convert(file_name, date, time):
  grbs = pygrib.open(file_name)

  # Get the layer for the target pressure level
  try:
    target_grb = grbs.select(name=VARIABLE, typeOfLevel='isobaricInhPa', level=TARGET_LEVEL)[0]
  except IndexError:
    print(f"No data found for {VARIABLE} at {TARGET_LEVEL} hPa")
    grbs.close()
    return

  values_2d = target_grb.values.astype(np.float32)
  grbs.close()

  ny, nx = values_2d.shape

  # Create 2D vtkImageData with Z=1
  image_data = vtk.vtkImageData()
  image_data.SetDimensions(nx, ny, 1)
  image_data.SetSpacing(1.0, 1.0, 1.0)
  image_data.SetOrigin(0.0, 0.0, 0.0)

  # Flatten array and convert
  flat_array = values_2d.ravel(order="C")
  vtk_array = numpy_to_vtk(num_array=flat_array, deep=True, array_type=vtk.VTK_FLOAT)
  vtk_array.SetName(f"{VARIABLE}_{TARGET_LEVEL}hPa")
  image_data.GetPointData().SetScalars(vtk_array)

  # Write to .vti
  output_filename = f"{VARIABLE}_{TARGET_LEVEL}hPa_{date}_{time:02d}.vti"
  writer = vtk.vtkXMLImageDataWriter()
  writer.SetFileName(output_filename)
  writer.SetInputData(image_data)
  writer.Write()

  print(f"Saved pressure layer: {output_filename}")


if __name__ == '__main__':
  extract()

