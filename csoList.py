import numpy as np
import vtk


def initCSOList():
    registerForNotification()


def registerForNotification():
    csoList = _getCSOList()
    csoList.removeAll()
    csoList.registerForNotification(csoList.NOTIFICATION_CSO_FINISHED, ctx, "csoFinished")


def csoFinished(_arg):
    csoList = _getCSOList()
    if len(csoList.getCSOs()) < 2: 
        ctx.field("baseFirstVector").value = "[]"
        ctx.field("baseSecondVector").value = "[]"

    if len(csoList.getCSOs()) == 2:
        directionVectors = []
        startVectors = []
        endVectors = []
        for cso in csoList.getCSOs():
            # see https://slicer.readthedocs.io/en/latest/developer_guide/script_repository.html#measure-angle-between-two-markup-lines
            # returns all important points of the line, just use the first and the last one as start/ending points and create using these two points a vector for the line
            path_points = cso.getPathPoints()
            start = np.array(path_points[0:3])
            startVectors.append(start)
            end = np.array(path_points[-3:])
            endVectors.append(end)
            directionVector = (end - start)
            directionVectors.append(directionVector)

        a = [directionVectors[0][1], directionVectors[0][0] * -1, 1]
        b = [directionVectors[1][1], directionVectors[1][0] * -1, 1]
        radians = vtk.vtkMath.AngleBetweenVectors(a, b)
        cobb_angle = vtk.vtkMath.DegreesFromRadians(radians)
        ctx.field("baseClassification").value = classify(cobb_angle)
        ctx.field("baseAngle0").value = "Cobb-angle: " + str(round(cobb_angle, 2)) + "°"
        str_arr1 = " ".join(map(str, (directionVectors[0] * -10) + startVectors[0]))
        str_arr2 = " ".join(map(str, (directionVectors[0] * 10) + startVectors[0]))
        ctx.field("baseFirstVector").value = f"[{str_arr1}, {str_arr2}]"
        str_arr1 = " ".join(map(str, (directionVectors[1] * -10) + startVectors[1]))
        str_arr2 = " ".join(map(str, (directionVectors[1] * 10) + startVectors[1]))
        ctx.field("baseSecondVector").value = f"[{str_arr1}, {str_arr2}]"

    if len(csoList.getCSOs()) >= 2:
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
