def _wemRendererModule():
    return ctx.module('SoWEMRenderer')

def init():
    _wemRendererModule().field('inWEM').connectFrom(ctx.field('inWEM'))
    ctx.field('self').connectFrom(_wemRendererModule().field('self'))
    handleColorChange()
    
def handleColorChange():
    _wemRendererModule().field('faceDiffuseColor').setColorValue(ctx.field('diffuseColor').colorValue())