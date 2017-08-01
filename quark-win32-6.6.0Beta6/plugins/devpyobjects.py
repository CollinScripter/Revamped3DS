
#$Header: /cvsroot/quark/runtime/plugins/devpyobjects.py,v 1.2 2010/02/23 18:38:24 danielpharos Exp $

# -----

#How to use this file:
#
# 1) Import it using the console:
#    > import plugins.devpyobjects
#
# 2) Run it:
#    > plugins.devpyobjects.OutputPyObjects()
#
#
# The output file will be dropped in QuArK's log directory.
#
# -----
#
# If you want to compare different logs (for instance, in order to find python object leaks),
# you can specify the filename (without extension) of the output log, so you can easily make a 'before' and 'after' log.
#

import quarkx

def OutputPyObjects(filename='python_objects'):
    import gc
    f = open(quarkx.logpath+filename+'.log', 'w')
    try:
        f.write(str(gc.get_objects()))
    finally:
        f.close()
    print 'OutputPyObjects: DONE!'

# ----------- REVISION HISTORY ------------
#
# $Log: devpyobjects.py,v $
# Revision 1.2  2010/02/23 18:38:24  danielpharos
# Added LOG_SUBDIRECTORY; not set right now.
#
# Revision 1.1  2010/02/21 20:30:08  danielpharos
# Added a plugin for outputting all current Python objects in memory (see file for usage).
#
