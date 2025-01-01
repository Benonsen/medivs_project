import numpy as np
import vtk

def initCSOList():
    setupCSOList()
    registerForNotification()


def setupCSOList():
    csoList = _getCSOList()


def registerForNotification():
    csoList = _getCSOList()
    csoList.registerForNotification(csoList.NOTIFICATION_CSO_FINISHED, ctx, "csoFinished")

def csoFinished(_arg):
    csoList = _getCSOList()
    if len(csoList.getCSOs()) == 2:
      directionVectors = []
      for cso in csoList.getCSOs():
          # see https://slicer.readthedocs.io/en/latest/developer_guide/script_repository.html#measure-angle-between-two-markup-lines
          # returns all important points of the line, just use the first and the last one as start/ending points and create using these two points a vector for the line
          path_points = cso.getPathPoints()
          start = np.array(path_points[0:3])
          end = np.array(path_points[-3:])
          # todo: only use x and y coordinates and ignore z
          #start = start[0:1]
          #end = end[0:1]

          directionVector = (end - start) / np.linalg.norm(end - start)
          directionVectors.append(directionVector)     

      
      radians = vtk.vtkMath.AngleBetweenVectors(directionVectors[0], directionVectors[1])
      cobb_angle = vtk.vtkMath.DegreesFromRadians(radians)
      ctx.field("baseClassification").value = classify(cobb_angle)
      ctx.field("baseAngle0").value = "Cobb-angle: " + str(round(cobb_angle, 2)) + "°"

    if len(csoList.getCSOs()) > 2:
        csoList.removeAll()
          
def classify(angle):
    # according to: A Deep Learning Approach for Automatic Scoliosis Cobb Angle Identification
    # https://ieeexplore.ieee.org/document/9817290
    # ACCEPTED CLINICAL COBB ANGLE SCOLIOSIS CATEGORY
    if angle <= 10: 
        return "Normal spine"
    if angle <= 20:
        return "Mild scoliosis"
    if angle <= 40:
        return "Moderate scoliosis"
    if angle > 40:
        return "Severe scoliosis"
  

def _getCSOList():
    return ctx.field("CSOListContainer.outCSOList").object()
  

