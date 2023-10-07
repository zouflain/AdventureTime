from os import listdir
from os.path import dirname
__all__ = [i[:-3] for i in listdir(dirname(__file__)) if not i.startswith('__') and i.endswith('.py')]

'''
import os, sys
dir_path = os.path.dirname(os.path.abspath(__file__))
files_in_dir = [f[:-3] for f in os.listdir(dir_path) if f.endswith('.py') and f != '__init__.py']
for f in files_in_dir:
    mod = __import__('.'.join([__name__, f]), fromlist=[f])
    for i in [getattr(mod, x) for x in dir(mod)]:
        try:
            setattr(sys.modules[__name__], i.__name__, i)
        except:
            pass

'''

"""
import os, sys
import inspect
dir_path = os.path.dirname(os.path.abspath(__file__))
files_in_dir = [f[:-3] for f in os.listdir(dir_path) if f.endswith('.py') and f != '__init__.py']
for f in files_in_dir:
    mod = __import__('.'.join([__name__, f]), fromlist=[f])
    for i in [getattr(mod, x) for x in dir(mod)]:
        try:
            if inspect.isclass(i):
                setattr(sys.modules[__name__], i.__name__, i)
                print(i.__name__)
        except:
            pass
del f
del mod
del i
"""