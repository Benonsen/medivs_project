import numpy as np
import vtk

def initCSOList():
    registerForNotification()

def registerForNotification():
    csoList = _getCSOList()
    csoList.registerForNotification(csoList.NOTIFICATION_CSO_FINISHED, ctx, "csoFinished")

def csoFinished(_arg):
    csoList = _getCSOList()
    if len(csoList.getCSOs()) == 2:
      directionVectors = []
      startVectors = []
      endVectors = []
      for cso in csoList.getCSOs():
          path_points = cso.getPathPoints()
          start = np.array(path_points[0:3])
          startVectors.append(start)
          end = np.array(path_points[-3:])
          endVectors.append(end)
          directionVector = (end - start)
          directionVectors.append(directionVector)  
      
      radians = vtk.vtkMath.AngleBetweenVectors(directionVectors[0], directionVectors[1])
      cobb_angle = vtk.vtkMath.DegreesFromRadians(radians)
      ctx.field("baseClassification").value = classify(cobb_angle)
      ctx.field("baseAngle0").value = "Cobb-angle: " + str(round(cobb_angle, 2)) + "°"
      str_arr1 = " ".join(map(str, (directionVectors[0] * -10) + startVectors[0])) 
      str_arr2 = " ".join(map(str, (directionVectors[0] * 10) + startVectors[0]))  
      ctx.field("baseFirstVector").value = f"[{str_arr1}, {str_arr2}]"
      str_arr1 = " ".join(map(str, (directionVectors[1] * -10) + startVectors[1])) 
      str_arr2 = " ".join(map(str, (directionVectors[1] * 10) + startVectors[1]))  
      ctx.field("baseSecondVector").value = f"[{str_arr1}, {str_arr2}]"

    if len(csoList.getCSOs()) > 2:
        csoList.removeAll()
          
def classify(angle):
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