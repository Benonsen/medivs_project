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
      for cso in csoList.getCSOs():
          path_points = cso.getPathPoints()
          start = np.array(path_points[0:3])
          end = np.array(path_points[-3:])
          directionVector = (end - start) / np.linalg.norm(end - start)
          directionVectors.append(directionVector)  
      
      radians = vtk.vtkMath.AngleBetweenVectors(directionVectors[0], directionVectors[1])
      cobb_angle = vtk.vtkMath.DegreesFromRadians(radians)
      ctx.field("baseClassification").value = classify(cobb_angle)
      ctx.field("baseAngle0").value = "Cobb-angle: " + str(round(cobb_angle, 2)) + "°"
      str_arr1 = " ".join(map(str, directionVectors[1] + start)) 
      str_arr2 = " ".join(map(str, (directionVectors[1] + start) * 10))  
      ctx.field("baseFirstVector").value = f"[{str_arr1}, {str_arr2}]"
      ctx.field("baseSecondVector").value = "[ " + str(directionVectors[1] * 5) + " ]"

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