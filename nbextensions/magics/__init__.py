from .templates import TemplateMagics
from .argo import ArgoMagics
from .nbvars import load_nbvars, NBVarsMagics

_loaded = False
def load_ipython_extension(ipython, **kwargs):
    global _loaded
    if not _loaded:
        ipython.register_magics(TemplateMagics(ipython, **kwargs))
        ipython.register_magics(ArgoMagics(ipython, **kwargs))
        ipython.register_magics(NBVarsMagics(ipython, **kwargs))        
        _loaded = True

def unload_ipython_extension(ipython):
    global _loaded
    if _loaded:
        magic = ipython.magics_manager.registry.pop('TemplateMagics')
        magic = ipython.magics_manager.registry.pop('ArgoMagics')
        magic = ipython.magics_manager.registry.pop('NBVarsMagics')       
        _loaded = False

