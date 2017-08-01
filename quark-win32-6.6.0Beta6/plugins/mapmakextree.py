"""   QuArK  -  Quake Army Knife Bezier shape makers


"""
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#


#$Header: /cvsroot/quark/runtime/plugins/mapmakextree.py,v 1.3 2005/11/10 17:43:55 cdunde Exp $

Info = {
  "plug-in":       "Make a simple tree",
  "desc":          "Make an tree from several intersecting brushes",
  "date":          "2003.04.20",
  "author":        "Marco 'NerdIII' Leise",
  "author e-mail": "Marco.Leise@gmx.de",
  "quark":         "Version 6.x"
}

from math import sin
from math import cos
from math import pi
import quarkx
import maptagside
import quarkpy.qmacro
import quarkpy.qtoolbar
from quarkpy.maputils import *

#base class for all games
class MakeXTreeDlg(quarkpy.qmacro.dialogbox):
  size = (300, 180)
  dfsep = 0.4     # separation at 40% between labels and edit boxes
  dlgflags = FWF_KEEPFOCUS + FWF_NORESIZE
  dlgdef = """
    {
      Style = "13"
      Caption = "simple tree maker 1.1"
      tex: = {
        Txt = "Tree texture:"
        Typ = "ET"
        SelectMe = "1"
        Hint = "Use transparent textures for trees"
      }
      planes: = {
        Txt = "Number of 'wings'"
        Typ = "EF1"
        Min = '3'
        Max = '32'
      }
      scale: = {
        Txt = "Scale tree by"
        Typ = "EF1"
        Min = '0.1'
        Hint = "This will add a size factor to the usual texturesize of the tree."
      }
    """

  def __init__(self, form, editor):
    self.editor = editor
    src = quarkx.newobj(":")

    # Based on the textures in the selections, initialize the from and to textures
    texlist = quarkx.texturesof(editor.layout.explorer.sellist)
    if len(texlist) == 1:
      src["tex"] = texlist[0]
    else:
      src["tex"] = quarkx.setupsubset()["DefaultTexture"]
    src["planes"]      = 4,
    src["scale"]       = 1,
    src["alternate"]     = "X"
    src["useblue"]     = ""

    # Create the dialog form and the buttons
    quarkpy.qmacro.dialogbox.__init__(self, form, src,
      close = quarkpy.qtoolbar.button(
        self.close,
        "close this box",
        ico_editor, 0,
        "Close"),
      MakeXTree = quarkpy.qtoolbar.button(
        self.MakeXTree,
        "make tree",
        ico_editor, 3,
        "Make Tree"))

  def AcceptDialog(self):
    # Commit any pending changes in the dialog box
    quarkx.globalaccept()
    # Gather information about what is to be created
    self.tex     = self.src["tex"]
    self.planes  = int((self.src["planes"])[0])
    self.scale   = (self.src["scale"])[0]
    self.blue    = self.src["useblue"] is not None
    self.alternate = self.src["alternate"] is not None
    texobj = quarkx.loadtexture (self.tex, self.editor.TexSource)
    if texobj is not None:
      try:
        texobj = texobj.disktexture
      except quarkx.error:
        texobj = None
    if texobj is not None:
      self.tsize = texobj ["size"]
    else:
      self.tsize = (128.0,128.0)
    self.twidth  = self.tsize[0]*self.scale
    self.theight = self.tsize[1]*self.scale
    self.treename = "huge tree"
    if self.theight <= 192: self.treename = "tree"
    if self.theight <= 64: self.treename = "bush"
    if self.theight <= 32: self.treename = "grass"

class MakeHLXTreeDlg(MakeXTreeDlg):
  dlgdef = MakeXTreeDlg.dlgdef + """
        alternate: = {
          Typ = "X"
          Txt = "Switch texture"
          Cap = "orientation on every wing"
          Hint = "On gives more variety from the chosen texture but should not be used on trees with bent trunks."
        }
        useblue: = {
          Typ = "X"
          Txt = "No null texture"
          Cap = "Only use the '{BLUE' texture instead"
          Hint = "Only use {BLUE if your set of build tools is too old. Using the null texture will increase performance."
        }
        sep: = { Typ ="S" Txt=""}
        MakeXTree:py = {Txt="" }
        close:py = {Txt="" }
      }
    """

  def MakeXTree(self, btn):
    self.AcceptDialog()
    if self.blue:
      nulltex = "{BLUE"
    else:
      nulltex = "NULL"
    # Create the tree
    g = quarkx.newobj(self.treename+":g");
    aface = quarkx.newobj("null:f")
    aface["v"] = (-self.twidth/2,-self.twidth/2,self.theight, self.twidth/2,-self.twidth/2,self.theight, -self.twidth/2,self.twidth/2,self.theight)
    aface["tex"] = nulltex
    g.appenditem(aface)
    aface = quarkx.newobj("null:f")
    aface["v"] = (-self.twidth/2,-self.twidth/2,0, -self.twidth/2,self.twidth/2,0, self.twidth/2,-self.twidth/2,0)
    aface["tex"] = nulltex
    g.appenditem(aface)
       
    ang=pi*2/self.planes
    addang=pi/self.planes/2
    addlen=sin(addang)/cos(addang)*self.twidth/2
    for j in range(2):
      e = quarkx.newobj("func_illusionary:b");
      e["rendermode"] = "4"
      e["renderamt"] = "127"
      g.appenditem(e)
      for i in range(self.planes):
        p = quarkx.newobj("tree-side:p");
        aface = quarkx.newobj("tree:f")
        sx1=cos(ang*i)*self.twidth/2
        sy1=sin(ang*i)*self.twidth/2
        if j==0:
          aface["v"] = (0,0,0, sx1,sy1,0, 0,0,self.theight)
        else:
          aface["v"] = (0,0,0, 0,0,self.theight, sx1,sy1,0)
        aface["tex"] = self.tex
        if (i>=self.planes/2) ^ ((self.alternate) & (i % 2==1)) ^ j==1:
          sign= 1
        else:
          sign=-1
        aface["tv"] = (-self.twidth/2,0,
                        sign*self.twidth / (self.tsize[0] / 128)-self.twidth/2,0,
                       -self.twidth/2, -self.theight / (self.tsize[1] / 128) - 0.5)
        p.appenditem(aface)
        aface = quarkx.newobj("null:f")
        if j==0:
          sx2=sx1-sin(ang*i)*addlen
          sy2=sy1+cos(ang*i)*addlen
          aface["v"] = (0,0,0, 0,0,self.theight, sx2,sy2,0)
        else:
          sx2=sx1+sin(ang*i)*addlen
          sy2=sy1-cos(ang*i)*addlen
          aface["v"] = (0,0,0, sx2,sy2,0, 0,0,self.theight)
        aface["tex"] = nulltex
        p.appenditem(aface)
        aface = quarkx.newobj("null:f")
        if j==0:
          aface["v"] = (sx1,sy1,0, sx2,sy2,0, sx2,sy2,self.theight)
        else:
          aface["v"] = (sx1,sy1,0, sx2,sy2,self.theight, sx2,sy2,0)
        aface["tex"] = nulltex
        p.appenditem(aface)
        e.appenditem(p)
    # Drop the items
    quarkpy.mapbtns.dropitemsnow(self.editor, [g], "make x-tree")
    
class MakeSinXTreeDlg(MakeXTreeDlg):
  dlgdef = MakeXTreeDlg.dlgdef + """
        alternate: = {
          Typ = "X"
          Txt = "Switch texture"
          Cap = "orientation on every wing"
          Hint = "On gives more variety from the chosen texture but should not be used on trees with bent trunks."
        }
        sep: = { Typ ="S" Txt=""}
        MakeXTree:py = {Txt="" }
        close:py = {Txt="" }
      }
    """

  def MakeFace(self,type):
    if type == 1:
      aface = quarkx.newobj("tree:f")
      aface["tex"] = self.tex
    else:
      aface = quarkx.newobj("null:f")
      aface["tex"] = self.nulltex
    aface["Contents"] = "402653248"
    aface["Flags"] = "2"
    return aface

  def MakeXTree(self, btn):
    self.AcceptDialog()
    self.nulltex = "generic/misc/skip"
    # Create the tree
    g = quarkx.newobj(self.treename+":g");
    aface = self.MakeFace(0)
    aface["v"] = (-self.twidth/2,-self.twidth/2,self.theight, self.twidth/2,-self.twidth/2,self.theight, -self.twidth/2,self.twidth/2,self.theight)
    g.appenditem(aface)
    aface = self.MakeFace(0)
    aface["v"] = (-self.twidth/2,-self.twidth/2,0, -self.twidth/2,self.twidth/2,0, self.twidth/2,-self.twidth/2,0)
    g.appenditem(aface)
    
    ang=pi*2/self.planes
    addang=pi/self.planes/2
    addlen=sin(addang)/cos(addang)*self.twidth/2
    for j in range(2):
      e = quarkx.newobj("func_illusionary:b");
      g.appenditem(e)
      for i in range(self.planes):
        p = quarkx.newobj("tree-side:p");
        aface = self.MakeFace(1)
        sx1=cos(ang*i)*self.twidth/2
        sy1=sin(ang*i)*self.twidth/2
        if j==0:
          aface["v"] = (0,0,0, sx1,sy1,0, 0,0,self.theight)
        else:
          aface["v"] = (0,0,0, 0,0,self.theight, sx1,sy1,0)
        if (i>=self.planes/2) ^ ((self.alternate) & (i % 2==1)) ^ j==1:
          sign= 1
        else:
          sign=-1
        aface["tv"] = (-self.twidth/2,0,
                        sign*self.twidth / (self.tsize[0] / 128)-self.twidth/2,0,
                       -self.twidth/2, -self.theight / (self.tsize[1] / 128) - 0.5)
        p.appenditem(aface)
        aface = self.MakeFace(0)
        if j==0:
          sx2=sx1-sin(ang*i)*addlen
          sy2=sy1+cos(ang*i)*addlen
          aface["v"] = (0,0,0, 0,0,self.theight, sx2,sy2,0)
        else:
          sx2=sx1+sin(ang*i)*addlen
          sy2=sy1-cos(ang*i)*addlen
          aface["v"] = (0,0,0, sx2,sy2,0, 0,0,self.theight)
        p.appenditem(aface)
        aface = self.MakeFace(0)
        if j==0:
          aface["v"] = (sx1,sy1,0, sx2,sy2,0, sx2,sy2,self.theight)
        else:
          aface["v"] = (sx1,sy1,0, sx2,sy2,self.theight, sx2,sy2,0)
        p.appenditem(aface)
        e.appenditem(p)
    # Drop the items
    quarkpy.mapbtns.dropitemsnow(self.editor, [g], "make x-tree")

class MakeQ2XTreeDlg(MakeXTreeDlg):
  size = (300, 150)
  dlgdef = MakeXTreeDlg.dlgdef + """
        sep: = { Typ ="S" Txt=""}
        MakeXTree:py = {Txt="" }
        close:py = {Txt="" }
      }
    """

  def MakeFace(self):
    aface = quarkx.newobj("tree:f")
    aface["Contents"] = "402653248"
    aface["Flags"] = "48"
    aface["tex"] = self.tex
    return aface

  def MakeXTree(self, btn):
    self.AcceptDialog()
    if not quarkpy.b2utils.iseven(self.planes):
      quarkx.msgbox("Sorry, but in Quake2 you must enter even numbers for 'wings'.",MT_INFORMATION, MB_OK)
      return
    # Create the tree
    g = quarkx.newobj(self.treename+":g");
    ang=pi*2/self.planes
    n=1
    aface = self.MakeFace()
    aface["v"] = (-self.twidth/2,-self.twidth/2,0,
                  -self.twidth/2, self.twidth/2,0,
                   self.twidth/2,-self.twidth/2,0)
    g.appenditem(aface)
    for k in range(self.planes / 2):
      p = quarkx.newobj("poly:p");
      x1 = self.twidth/2 * cos(k*ang)
      y1 = self.twidth/2 * sin(k*ang)
      x2 = n * sin(k*ang)
      y2 = n * cos(k*ang)
      for i in [-1,1]:
        #Create a help plane for texture mapping
        proj = self.MakeFace()
        proj["v"] = (i*-x1,i*-y1,0,
                     i* x1,i* y1,0,
                     i*-x1,i*-y1,self.theight)
        proj["tv"] = (-self.twidth/2,0,
                       -self.twidth / (self.tsize[0] / 128)-self.twidth/2,0,
                       -self.twidth/2, -self.theight / (self.tsize[1] / 128) - 0.5)
        proj["tv"] = (-self.twidth,0,
                      -self.twidth / (self.tsize[0] / 128)-self.twidth,0,
                      -self.twidth, -self.theight / (self.tsize[1] / 128) - 0.5)
        #Create the real brush
        aface = self.MakeFace()
        aface["v"] = (i*x2,i*-y2,0,
                      i*x1,i* y1,0,
                      i*x2,i*-y2,self.theight)
        pface = maptagside.projecttexfrom(proj, aface)
        p.appenditem(pface)
        aface = self.MakeFace()
        aface["v"] = (i*-x2,i*y2,0,
                      i*-x2,i*y2,self.theight,
                      i* x1,i*y1,0)
        pface = maptagside.projecttexfrom(proj, aface)
        p.appenditem(pface)
        aface = self.MakeFace()
        aface["v"] = (i*-x2,i* y2,0,
                      i*-x1,i*-y1,self.theight,
                      i* x1,i* y1,self.theight)
        pface = maptagside.projecttexfrom(proj, aface)
        p.appenditem(pface)
      g.appenditem(p)
    quarkpy.mapbtns.dropitemsnow(self.editor, [g], "make x-tree")


# Menu click...
def MakeXTreeClick(m):
  editor = mapeditor()
  if editor is None:
    return
  game = quarkx.setupsubset().shortname
  if game == 'Half-Life':
    MakeHLXTreeDlg(quarkx.clickform, editor)
  else:
    if game == 'Quake 2':
      MakeQ2XTreeDlg(quarkx.clickform, editor)
    else:
      if game == 'Sin':
        MakeSinXTreeDlg(quarkx.clickform, editor)
        quarkx.msgbox("When I coded the plug-in I did not have Sin. I still need someone to test it, or tell me if I did something wrong. I would be glad if you could send me a mail to Marco.Leise@gmx.de!",MT_INFORMATION, MB_OK)
      else:
        if game in ['Quake 1','Heretic II', 'Hexen II']:
          quarkx.msgbox("This plugin works with masked textures. "+game+" does not support this kind of transparency.",MT_INFORMATION, MB_OK)
        else:
          quarkx.msgbox(game+" is currently not supported, sorry. Please post a mail to Marco.Leise@gmx.de and I'll see what I can do.",MT_INFORMATION, MB_OK)

# in case the developer (that would be me) reloaded the plugin, delete the previous button procedure
for m in quarkpy.mapcommands.items:
  if m <> None:
    if m.text == "Make &X-Tree":
      quarkpy.mapcommands.items.remove(m)      
# Register the plug-in
quarkpy.mapcommands.items.append(quarkpy.qmenu.item("Make &X-Tree", MakeXTreeClick))

# ----------- REVISION HISTORY ------------
#
# $Log: mapmakextree.py,v $
# Revision 1.3  2005/11/10 17:43:55  cdunde
# To add header and start history log
#
# Revision 1.2  2005/11/10 17:25:38  cdunde
# To add header and start history log
#
#