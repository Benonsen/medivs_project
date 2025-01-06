import vtk
from pathlib import Path
from mevis import *

def _getLabels():
    labels = [
        *(f'L{i:02d}' for i in range( 5, 0, -1)),
        *(f'T{i:02d}' for i in range(12, 0, -1)),
        *(f'C{i:02d}' for i in range( 7, 0, -1)),
    ]
    labels = list(filter(lambda label: ctx.hasField(f'v{label}'), labels))
    return labels

def _getConnectedAndUnconnectedLabels():
    connected = list(filter(lambda label: ctx.field(f'v{label}').outputCount() > 0, _getLabels()))
    unconnected = list(filter(lambda label: label not in connected, _getLabels()))
    return (connected, unconnected)

def _getOutVertebraField(label):
    return ctx.field(f'v{label}')

def _getInCSODirectory():
    return ctx.field('spineCSOsDirectoryName')

def _getCombineCSOsModule():
    return ctx.module('CombineCSOs')

    
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

combineCSOsModules = {}
csoToSurfaceModules = {}

def init():
    for moduleName in ctx.modules():
        if str(moduleName).startswith('CombineCSO') or str(moduleName).startswith('CSOToSurface'):
            ctx.module(moduleName).remove()
    
    inputBaseImage = ctx.field('baseImage')
    ctx.field('ImageResample.input0').connectFrom(inputBaseImage)
    
    ctx.field('resampledImage').connectFrom(ctx.field('ImageResample.output0'))
    
    global combineCSOsModules, csoToSurfaceModules
    extendedLabels = [*_getLabels(), 'Other']
    combineCSOsModules = {label: ctx.addLocalModule('CombineCSOs') for label in extendedLabels}
    csoToSurfaceModules = {label: ctx.addModule('CSOToSurface') for label in extendedLabels}
        
    for label in extendedLabels:
        toSurfaceModule = csoToSurfaceModules[label]
        toSurfaceModule.field('input0').connectFrom(ctx.field('ImageResample.output0'))
        
        combineModule = combineCSOsModules[label]
        toSurfaceModule.field('inCSO').connectFrom(combineModule.call('_getOutCombinedCSOList'))
        
        _getOutVertebraField(label).connectFrom(toSurfaceModule.field('outWEM'))
        

def run():
    global combineCSOsModules, csoToSurfaceModules
    for combineCSOsModule in combineCSOsModules.values():
        combineCSOsModule.field('spineCSOsDirectoryName').setPersistentStringValue(ctx.expandFilename(_getInCSODirectory().stringValue()))
    
    [connected, unconnected] = _getConnectedAndUnconnectedLabels()

    otherCombineCSOsModule = combineCSOsModules['Other']
    otherCombineCSOsModule.field('vertebraLabels').setStringValue(','.join(unconnected))
    otherCombineCSOsModule.call('combineCSOs')
    
    for label in connected:
        module = combineCSOsModules[label]
        module.field('vertebraLabels').setPersistentStringValue(label)
        module.call('combineCSOs')

    
def destroy():
        global combineCSOsModules, csoToSurfaceModules
        combineCSOsModules.clear()
        csoToSurfaceModules.clear()
        