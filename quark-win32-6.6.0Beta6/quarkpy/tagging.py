# QuArK -- Quake Army Knife
# Copyright (C) 2005 Peter Brett
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

# $Header: /cvsroot/quark/runtime/quarkpy/tagging.py,v 1.8 2008/02/22 09:52:23 danielpharos Exp $

"""Version 2 of QuArK tagging support, moved to the quarkpy module as
it isn't just used by plugins any more.

Now dictionary-based, supporting any number of categories.

This is to deal with the problem of plugins being able to stomp all over
each others' tags, potentially causing problems.

This also solves the problem of how to tag many different types of object.
"""

__all__ = ['cleartags', 'untag', 'istagged', 'tag',
           'uniquetag', 'gettaglist', 'getuniquetag',
           'tagdrawfunc']

import qbaseeditor

# -- Tagging ------------------------------------------------------- #
class Tagging:
  """A place to stick tagging stuff.

  Plugins should never manipulate objects of this class directly.
  """
  def __init__(self):
    self.taglists = {}

"""Stores all Tagging objects for all editors.

The ONLY code that may access this dictionary is the _gettagging()
function below.
"""
_tagsets = {}

def _diag():
  for k in _tagsets.keys():
    print " == %s ==\n == %s ==\n" % (k, _tagsets[k])
    for j in _tagsets[k].taglists.keys():
      print "    -- %s --\n%s" % (j, _tagsets[k].taglists[j])

# -- Private utility functions ------------------------------------- #
#   ===========================
def _gettagging(editor):
  """   _gettagging(editor)
  
Get the Tagging object associated with editor.

Should never be called by any methods other than the ones in
this module.

The tagging object should never be accessed except via this function.
"""
  try:
    t = _tagsets[editor]
  except (KeyError):
    t = Tagging()
    _tagsets[editor] = t
  return t


def _gettaglist(editor, key):
  """   _gettaglist(editor, key):

Gets the actual tag list associated with key.

Should never be called by any methods other than the ones in
this module.
"""
  try:
    t = _gettagging(editor).taglists[key]
  except (KeyError):
    t = []
    _gettagging(editor).taglists[key] = t
  return t


# -- Exported functions -------------------------------------------- #
#   ====================      
def cleartags(editor, *keys):
  """   cleartags(editor, key[, key2, ..., keyN])

Clear all tags in the specified categories.
"""
  for k in keys:
    # We do this via untag() so that callback functions are called

    # Get a copy of the list of tagged items so callback functions
    # don't modify the actual list (that would be bad)
    objs = gettaglist(editor, k)
    untag(editor, k, *objs)


def untag(editor, key, *objs):
  """   untag(editor, key, obj[, obj2, ..., objN])
  
If any of the specified objects are tagged in the specified category,
untag them.
"""
  t = _gettaglist(editor, key)
  
  # Find out which objects are already tagged
  objstountag = []
  for o in objs:
    if o in t:
      objstountag.append(o)

  # Call callback functions
  _applytagchangefuncs(editor, key, [], objstountag)

  # Do removal
  for o in objstountag:
    t.remove(o)

  editor.invalidateviews()


def istagged(editor, key, *obj):
  """   istagged(editor, key, obj[, obj2, ..., objN])

If all specified objects are tagged in the specified category, return
1.  Otherwise, return 0.
"""
  t = _gettaglist(editor, key)
  for o in obj:
    if not o in t:
      return 0
  return 1


def tag(editor, key, *objs):
  """   tag(editor, key, obj[, obj2, ..., objN])
  
Tag objects in the tag category specified by key.
"""
  t = _gettaglist(editor, key)

  # Find out which objects aren't already tagged
  objstotag = []
  for o in objs:
    if not o in t:
      objstotag.append(o)

  # Call callback functions
  _applytagchangefuncs(editor, key, objstotag, [])

  # Do addition
  for o in objstotag:
    t.append(o)
      
  editor.invalidateviews()


def uniquetag(editor, key, obj):
  """   uniquetag(editor, key, obj)

Tag an object, and remove all other tags in the same category.
"""
  cleartags(editor, key)
  tag(editor, key, obj)


def gettaglist(editor, *keys):
  """   gettaglist(editor, key[, key2, ..., keyN])

Get all tagged objects in the specified tag categories.

Modifications to the returned list will not affect which items are
tagged.
"""
  objlist = []
  for k in keys:
    objlist += _gettaglist(editor, k)
  return objlist


def getuniquetag(editor, key):
  """   getuniquetag(editor, key)

Get the most recently tagged object in the tag category specified
by key.
"""
  t = _gettaglist(editor, key)
  if t:
    return t[-1]
  return None


# -- Tag change callback functions --------------------------------- #
#   ===============================

# Stores functions called when the items are tagged or untagged
#
# The ONLY code that may access this dictionary are the tagchangefunc()
# and _applytagchangefuncs() functions below
_changecallbacks = {}


def tagchangefunc(function, *keys):
  """   tagchangefunc(function, *key...)

Set a function called when a tag category/categories changes
(i.e. items are tagged or untagged).

Functions must be of the form

  f(editor, key, tagged, untagged)

where: editor is the editor where tags have changed
       key is the key of the tag category being changed
       tagged is a list of items being added to the category
       untagged is a list of items being removed from the category

Functions *must not* add or remove tags.

The callback function is called before making changes to what's tagged
or not tagged.  This means that a callback function can modify the
tagged and untagged lists if necessary, or raise exceptions to prevent
changes to tags.

Callback functions are used for _all_ editors.
"""
  for k in keys:
    if not k in _changecallbacks.keys():
      _changecallbacks[k] = []
    l = _changecallbacks[k]
    l.append(function)


def _applytagchangefuncs(editor, key, tagged, untagged):
  """   _applytagchangefuncs(editor, key, tagged, untagged)

Call any defined change callback functions.

Should never be called by any methods other than the ones in
this module.
"""
  if key in _changecallbacks.keys():
    for f in _changecallbacks[key]:
      f(editor, key, tagged, untagged)


# -- Map drawing routines ------------------------------------------ #
#   ======================

# Stores callbacks for drawing tagged objects
# 
# The ONLY code that may access this dictionary are the tagdrawfunc()
# and _tagfinishdrawing functions below.
_drawcallbacks = {}


def tagdrawfunc(function, *keys):
  """   tagdrawfunc(function, *key...)

Set the function to be used to draw tagged items in
a particular tag category or categories.

Functions must be of the form

  f(editor, view, canvas, obj)

where: editor is the editor being redrawn
       view is the view to be drawn on
       obj is the tagged object to draw.

Callback functions are used for _all_ editors.
"""
  for k in keys:
    _drawcallbacks[k] = function


def _tagfinishdrawing(editor, view, oldmore=qbaseeditor.BaseEditor.finishdrawing):
  """Finishdrawing routine for handling tagged objects.

Uses callback functions set using tagdrawfunc().
"""
  
  oldmore(editor, view)
  cv = view.canvas()
  
  # Make the pen the correct colour, so callback functions don't
  # need to
  oldcolour = cv.pencolor
  cv.pencolor = qbaseeditor.MapColor("Tag")
  
  for k in _drawcallbacks.keys():
    f = _drawcallbacks[k]
    if f is None:
      continue
    
    for obj in _gettaglist(editor, k): # _gettaglist is faster 
      f(editor, view, cv, obj)
      
  # Restore the pen colour
  cv.pencolor = oldcolour
  
qbaseeditor.BaseEditor.finishdrawing = _tagfinishdrawing

#$Log: tagging.py,v $
#Revision 1.8  2008/02/22 09:52:23  danielpharos
#Move all finishdrawing code to the correct editor, and some small cleanups.
#
#Revision 1.7  2005/10/15 00:47:57  cdunde
#To reinstate headers and history
#
#Revision 1.3  2005/09/19 00:23:45  peter-b
#Fix more silly tagging errors
#
#Revision 1.2  2005/09/18 23:55:33  peter-b
#Make tagfinishdrawing() set and restore the pen colour
#
#Revision 1.1  2005/09/18 23:06:16  peter-b
#New uber-powerful tagging API
#
#
