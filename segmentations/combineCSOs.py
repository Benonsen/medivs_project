import vtk
from pathlib import Path
from mevis import *

outCSOList = None


def _getOutCombinedCSOList():
    return ctx.field("outCombinedCSOList")

def _getInCSODirectory():
    return ctx.field("spineCSOsDirectoryName")


def combineCSOs():
    dirName = ctx.expandFilename(_getInCSODirectory().stringValue())
    if not (MLABFileManager.exists(dirName) or MLABFileManager.isDir(dirName)):
        ctx.logWarning("Directory does not exist")
        return

    dir = Path(dirName)
    csoFiles = list(dir.glob('*.cso'))
    if len(csoFiles) == 0:
        ctx.logWarning("No CSOs in directory")
    
    global outCSOList
    outCSOList = MLAB.createMLBaseObject("CSOList")
    uniqueCsoId = 0
    for file in csoFiles:
        csoList = MLAB.createMLBaseObject("CSOList")
        if not csoList.loadFrom(str(file)):
            ctx.logWarning(f'Error loading CSO from {file}')
        
        group = outCSOList.addGroup(file.stem)
        groupId = group.getId()
        for cso in csoList.getCSOs():
            addedCSO = outCSOList.addCSOCopy(cso)
            outCSOList.combineCSOandGroup(addedCSO.getId(), groupId)
        
    _getOutCombinedCSOList().setObject(outCSOList)

def handleDirectoryChange():
    networkDirStr = '$(NETWORK)'
    expandedNetworkDirStr = ctx.expandFilename(networkDirStr)
    networkDir = Path(expandedNetworkDirStr)
    
    inDirStr = ctx.expandFilename(_getInCSODirectory().stringValue())
    inDir = Path(inDirStr)
    
    if inDir.is_relative_to(networkDir):
        relativePath = inDir.relative_to(networkDir)
        prependedPath = Path(networkDirStr / relativePath)
        _getInCSODirectory().setValue(str(prependedPath))
