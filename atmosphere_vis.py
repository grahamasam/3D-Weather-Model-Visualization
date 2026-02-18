from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QGridLayout, QPushButton, QTextEdit, QCheckBox, QLabel, QSlider
#import PyQt6.QtCore as QtCore
from PyQt6.QtCore import Qt
import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import argparse
import sys
from vtk_camera import save_camera, load_camera
import os

NA_IMAGE_PATH = "images/NA_MAP_NO_BORDER_WHITE.png"
HRRR_WIDTH = 1798
HRRR_HEIGHT = 1058
BLANK_IMAGE = "images/blank_img.png"

frame_counter = 0
default_cam = {"position": [671.46120300504, -2054.1340881372676, 1786.9861600854017], "focal_point": [833.3877526949775, -20.752970430237255, 379.0011417472582], "view_up": [-0.002320196264332275, 0.5694042877567462, 0.8220543618116307], "clipping_range": [2193.398106044568, 4488.309829557098], "angle": 30.0}

def set_camera(cam):
  camera = vtk.vtkCamera()
  camera.SetPosition(cam['position'])
  camera.SetFocalPoint(cam['focal_point'])
  camera.SetViewUp(cam['view_up'])
  camera.SetClippingRange(cam['clipping_range'])
  if 'angle' in cam.keys():
    camera.SetViewAngle(cam['angle'])
  return camera

def save_frame(window, log):
  global frame_counter

  file_name = "Screenshot" + str(frame_counter).zfill(5) + ".png"
  image = vtk.vtkWindowToImageFilter()
  image.SetInput(window)
  png_writer = vtk.vtkPNGWriter()
  png_writer.SetInputConnection(image.GetOutputPort())
  png_writer.SetFileName(file_name)
  window.Render()
  png_writer.Write()
  frame_counter += 1
  print(file_name + " has been successfully exported")
  log.insertPlainText('Exported {}\n'.format(file_name))

def make_map_actor(image_path, height, width):
  reader = vtk.vtkPNGReader()
  reader.SetFileName(image_path)
  reader.Update()

  plane = vtk.vtkPlaneSource()
  plane.SetOrigin(0.0, 0.0, 0.0)
  plane.SetPoint1(width, 0.0, 0.0)
  plane.SetPoint2(0.0, height, 0.0)
  plane.Update()

  texture = vtk.vtkTexture()
  texture.SetInputConnection(reader.GetOutputPort())
  #texture.InterpolateOn()

  mapper = vtk.vtkPolyDataMapper()
  mapper.SetInputConnection(plane.GetOutputPort())

  actor = vtk.vtkActor()
  actor.SetMapper(mapper)
  actor.SetTexture(texture)

  return actor

def make_pressure_layer_actor(image_data, height_data, scale_factor):
  # create height map representation of elevation with vtkWarpScalar
  geometry_filter = vtk.vtkImageDataGeometryFilter()
  geometry_filter.SetInputData(height_data)
  geometry_filter.Update()

  geometry_data = geometry_filter.GetOutput()

  warp = vtk.vtkWarpScalar()
  warp.SetInputData(geometry_data)
  warp.SetScaleFactor(scale_factor)
  warp.Update()

  # texture-map the blank image onto the height map geometry
  texture = vtk.vtkTexture()
  texture.SetInputData(image_data)
  texture.InterpolateOn()

  mapper = vtk.vtkPolyDataMapper()
  mapper.SetInputConnection(warp.GetOutputPort())
  mapper.ScalarVisibilityOff()

  actor = vtk.vtkActor()
  actor.SetMapper(mapper)
  actor.SetTexture(texture)

  return actor

def make_variable_contour_filters(image_data, isovalue):
  contour_filter = vtk.vtkContourFilter()
  contour_filter.SetInputData(image_data)
  contour_filter.SetValue(0, isovalue) 
  contour_filter.Update()

  return contour_filter


class Ui_MainWindow(object):
  def setupUi(self, MainWindow):
    MainWindow.setObjectName('Main Window')
    MainWindow.setWindowTitle('Atmosphere_vis.py')

    self.centralWidget = QWidget(MainWindow)
    self.gridlayout = QGridLayout(self.centralWidget)
    self.vtkWidget = QVTKRenderWindowInteractor(self.centralWidget)

    # Quit button
    self.push_quit = QPushButton()
    self.push_quit.setText('Quit')
    # screenshot button
    self.push_screenshot = QPushButton()
    self.push_screenshot.setText('Save screenshot')
    # save camera settings button
    self.push_camera = QPushButton()
    self.push_camera.setText('Save camera')
    # text window
    self.log = QTextEdit()
    self.log.setReadOnly(True)

    # Isovalue slider
    self.time_label = QLabel("Time:")
    self.folder1_time_slider = QSlider()

    # plane boxes and labels
    self.p1_label = QLabel("Folder 1:")
    self.p2_label = QLabel("Folder 2:")
    self.p3_label = QLabel("Pressure Surface:")
    self.map_label = QLabel("Map:")
    self.p1_check = QCheckBox()
    self.p2_check = QCheckBox()
    self.p3_check = QCheckBox()
    self.map_check = QCheckBox()
    self.p1_check.setChecked(True)
    self.p2_check.setChecked(True)
    self.p3_check.setChecked(True)
    self.map_check.setChecked(True)

    # subwidget and grid to put boxes in
    self.subwidget = QWidget()
    self.subgrid = QGridLayout(self.subwidget)
    self.subwidget.setStyleSheet(
      "QWidget#subwidget { border: 2px solid black; border-radius: 5px; padding: 5px; }"
    )
    self.subwidget.setObjectName("subwidget")  # Name widget so styling only applies to outside of box

    self.subgrid.addWidget(self.p1_label, 0, 0, 1, 1)
    self.subgrid.addWidget(self.p1_check, 0, 1, 1, 1)
    self.subgrid.addWidget(self.p2_label, 0, 2, 1, 1)
    self.subgrid.addWidget(self.p2_check, 0, 3, 1, 1)
    self.subgrid.addWidget(self.p3_label, 0, 4, 1, 1)
    self.subgrid.addWidget(self.p3_check, 0, 5, 1, 1)
    self.subgrid.addWidget(self.map_label, 0, 6, 1, 1)
    self.subgrid.addWidget(self.map_check, 0, 7, 1, 1)

    self.gridlayout.addWidget(self.vtkWidget, 0, 0, 5, 5)
    self.gridlayout.addWidget(self.log, 2, 6, 1, 1)
    self.gridlayout.addWidget(self.push_quit, 4, 6, 1, 1)
    self.gridlayout.addWidget(self.time_label, 5, 0, 1, 3)
    self.gridlayout.addWidget(self.folder1_time_slider, 5, 1, 1, 3)
    self.gridlayout.addWidget(self.push_screenshot, 0, 6, 1, 1)
    self.gridlayout.addWidget(self.push_camera, 1, 6, 1, 1)
    self.gridlayout.addWidget(self.subwidget, 6, 0, 1, 2)

    self.gridlayout.setColumnStretch(2, 5)  # stretch slider column
    self.gridlayout.setColumnStretch(6, 1)  # relative to log and buttons

    MainWindow.setCentralWidget(self.centralWidget)

class IsoVis(QMainWindow):
  def __init__(self, parent = None):
    QMainWindow.__init__(self, parent)
    self.ui = Ui_MainWindow()
    self.ui.setupUi(self)

    self.ren = vtk.vtkRenderer()

    self.current_time = 0

    # === load map image ===
    self.map_actor = make_map_actor(NA_IMAGE_PATH, HRRR_HEIGHT, HRRR_WIDTH)
    x, y, z = self.map_actor.GetPosition()
    self.map_actor.SetPosition(x, y, z - 100.0)
    self.ren.AddActor(self.map_actor)

    self.scale_factor = 0.5

    self.isovalue1 = float(args.folder1[1])
    self.folder1_actors = []
    self.folder1_contour_filters = []

    var_folder_path = args.folder1[0]
    filenames1 = os.listdir(var_folder_path)

    # ==== TEMPERATURE CONTOUR ====
    for file in filenames1:
      # === Read VTI file ===
      reader = vtk.vtkXMLImageDataReader()
      reader.SetFileName(os.path.join(var_folder_path, file))
      reader.Update()

      print(os.path.join(var_folder_path, file))

      image_data = reader.GetOutput()

      new_contour_filter = make_variable_contour_filters(image_data, self.isovalue1)
      self.folder1_contour_filters.append(new_contour_filter)
    
      # === Mapper and Actor ===
      mapper = vtk.vtkPolyDataMapper()
      mapper.SetInputConnection(new_contour_filter.GetOutputPort())
      mapper.ScalarVisibilityOn()

      temp_actor = vtk.vtkActor()
      temp_actor.SetMapper(mapper)

      temp_actor.SetScale(1.0,1.0,5.0)

      self.folder1_actors.append(temp_actor)

    self.isovalue2 = float(args.folder2[1])
    self.folder2_actors = []
    self.folder2_contour_filters = []

    var_folder2_path = args.folder2[0]
    filenames2 = os.listdir(var_folder2_path)

    # ==== TEMPERATURE CONTOUR ====
    for file in filenames2:
      # === Read VTI file ===
      reader = vtk.vtkXMLImageDataReader()
      reader.SetFileName(os.path.join(var_folder2_path, file))
      reader.Update()

      print(os.path.join(var_folder2_path, file))

      image_data = reader.GetOutput()

      new_contour_filter = make_variable_contour_filters(image_data, self.isovalue2)
      self.folder2_contour_filters.append(new_contour_filter)
    
      # === Mapper and Actor ===
      mapper = vtk.vtkPolyDataMapper()
      mapper.SetInputConnection(new_contour_filter.GetOutputPort())
      mapper.ScalarVisibilityOn()

      temp_actor = vtk.vtkActor()
      temp_actor.SetMapper(mapper)

      temp_actor.SetScale(1.0,1.0,5.0)
      temp_actor.GetProperty().SetOpacity(0.5)

      self.folder2_actors.append(temp_actor)


    self.folder3_actors = []

    var_folder3_path = args.pressure
    filenames3 = os.listdir(var_folder3_path)

    for file in filenames3:
      # Read the image
      image_reader = vtk.vtkPNGReader()
      image_reader.SetFileName(BLANK_IMAGE)
      image_reader.Update()

      image_data = image_reader.GetOutput()
      # Read the height map
      height_reader = vtk.vtkXMLImageDataReader()
      height_reader.SetFileName(os.path.join(var_folder3_path, file))
      height_reader.Update()

      print(os.path.join(var_folder3_path, file))

      heights = height_reader.GetOutput()

      actor = make_pressure_layer_actor(image_data, heights, self.scale_factor)
      x, y, z = actor.GetPosition()
      actor.SetPosition(x, y, z - 100.0)
      actor.GetProperty().SetOpacity(0.8)
      self.folder3_actors.append(actor)

    self.ren.SetBackground(249/255, 242/255, 237/255) 
    #self.ren.SetUseDepthPeeling(True) # enable depth peeling to properly visualize overlapping transparent meshes
    self.ui.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
    self.iren = self.ui.vtkWidget.GetRenderWindow().GetInteractor()

    # set camera position (if camera arg specified)
    if args.camera:
      new_camera = load_camera(args.camera)
      self.ren.SetActiveCamera(new_camera)
    else:
      self.ren.SetActiveCamera(set_camera(default_cam))

    # Setting up widgets
    # create xyz compass widget
    axes = vtk.vtkAxesActor()
    self.compass_widget = vtk.vtkOrientationMarkerWidget()
    self.compass_widget.SetOutlineColor(1, 1, 1)
    self.compass_widget.SetOrientationMarker(axes) 
    self.compass_widget.SetInteractor(self.iren)
    self.compass_widget.SetViewport(0, 0.8, 0.1, 1.0) # put in top left
    self.compass_widget.SetEnabled(True)
    self.compass_widget.InteractiveOff()

    # Setting up widgets
    def slider_setup(slider, val, bounds, interv):
      slider.setOrientation(Qt.Orientation.Horizontal)
      slider.setValue(int(val))
      slider.setTracking(False)
      slider.setTickInterval(interv)
      slider.setTickPosition(QSlider.TickPosition.TicksAbove)
      slider.setRange(bounds[0], bounds[1])

    slider_setup(self.ui.folder1_time_slider, self.current_time, [0, len(self.folder1_actors) - 1], 1)
    self.slider_callback(self.current_time)

  def screenshot_callback(self):
    save_frame(self.ui.vtkWidget.GetRenderWindow(), self.ui.log)

  def save_camera_callback(self):
    save_camera(self.ren.GetActiveCamera(), self.ren)
    self.ui.log.insertPlainText('Camera position saved\n')

  def quit_callback(self):
    sys.exit()
  
  def slider_callback(self, val):
    self.current_time = val
    # remove previous actor
    if self.ui.p1_check.isChecked():
      for actor in self.folder1_actors:
        self.ren.RemoveActor(actor)
      # add active actor
      self.ren.AddActor(self.folder1_actors[val])

    # remove previous actor
    if self.ui.p2_check.isChecked():
      for actor in self.folder2_actors:
        self.ren.RemoveActor(actor)
      # add active actor
      self.ren.AddActor(self.folder2_actors[val])

    # remove previous actor
    if self.ui.p3_check.isChecked():
      for actor in self.folder3_actors:
        self.ren.RemoveActor(actor)
      # add active actor
      self.ren.AddActor(self.folder3_actors[val])

    self.ui.log.insertPlainText('Displaying time {}\n'.format(val))
    self.ui.vtkWidget.GetRenderWindow().Render()

  def checkbox_callback(self):
    sender = self.sender()

    if sender is self.ui.p1_check:
      if self.ui.p1_check.isChecked():
        self.ren.AddActor(self.folder1_actors[self.current_time])
      else:
        self.ren.RemoveActor(self.folder1_actors[self.current_time])
    elif sender is self.ui.p2_check:
      if self.ui.p2_check.isChecked():
        self.ren.AddActor(self.folder2_actors[self.current_time])
      else:
        self.ren.RemoveActor(self.folder2_actors[self.current_time])
    elif sender is self.ui.p3_check:
      if self.ui.p3_check.isChecked():
        self.ren.AddActor(self.folder3_actors[self.current_time])
      else:
        self.ren.RemoveActor(self.folder3_actors[self.current_time])
    elif sender is self.ui.map_check:
      if self.ui.map_check.isChecked():
        self.ren.AddActor(self.map_actor)
      else:
        self.ren.RemoveActor(self.map_actor)

    self.ui.vtkWidget.GetRenderWindow().Render()

class CustomArgumentParser(argparse.ArgumentParser):
  def error(self, message):
    print(f"Error: {message}\n")
    print("Usage: python atmosphere_vis --folder1 <name of folder1> <isovalue> --folder2 <name of folder2> <isovalue> --pressure <name of pressure layer folder>\n")
    sys.exit(2)

if __name__ == '__main__':
  parser = CustomArgumentParser()
  parser.add_argument('--folder1', type=str, nargs=2, required=True, help='variable arrays folder')
  parser.add_argument('--folder2', type=str, nargs=2, required=True, help='variable arrays folder 2')
  parser.add_argument('--pressure', type=str, required=True, help='name of pressure layer folder')
  parser.add_argument('--camera', type=str, help='camera position')

  args = parser.parse_args()

  # initialize app and window
  app = QApplication(sys.argv)
  window = IsoVis()
  window.show()
  window.setWindowState(Qt.WindowState.WindowMaximized)
  window.iren.Initialize()

  window.compass_widget.On()

  # connect callback functions to their GUI elements
  window.ui.push_quit.clicked.connect(window.quit_callback)
  window.ui.push_screenshot.clicked.connect(window.screenshot_callback)
  window.ui.push_camera.clicked.connect(window.save_camera_callback)
  # time slider connection
  window.ui.folder1_time_slider.valueChanged.connect(window.slider_callback)
  # checkbox connection
  window.ui.p1_check.stateChanged.connect(window.checkbox_callback)
  window.ui.p2_check.stateChanged.connect(window.checkbox_callback)
  window.ui.p3_check.stateChanged.connect(window.checkbox_callback)
  window.ui.map_check.stateChanged.connect(window.checkbox_callback)
  sys.exit(app.exec())