"""   QuArK  -  Quake Army Knife

Python macros available for direct call by QuArK
"""
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/plugins/entfgd2qrk.py,v 1.17 2009/02/11 15:39:07 danielpharos Exp $

Info = {
   "plug-in":       "entfgd2qrk plugin",
   "desc":          "Python macros available for direct call by QuArK",
   "date":          "2001/04/14",
   "author":        "decker",
   "author e-mail": "decker@planetquake.com",
   "quark":         "Version 6.3"
}


#
#tbd:
#     readonly
#     halfgridsnap
#     forms for specific data types
#


import time, sys

class Key:
    def __init__(self):
        self.m_keyname = None
        self.m_desc = ""
        self.m_defaultvalue = None
        self.m_kind =None

    def SetKeyname(self, keyname):
        self.m_keyname = keyname

    def SetDesc(self, desc):
        self.m_desc = desc

    def AddDesc(self, desc):
        self.m_desc += desc

    def SetDefaultValue(self, defvalue):
        self.m_defaultvalue = defvalue

    def GetDefaultValue(self):
        return self.m_defaultvalue

    def GenerateFolder(self, indent):
        if (self.m_defaultvalue is None) or (self.m_defaultvalue == ""):
            return None
        indent[self.m_keyname] = str(self.m_defaultvalue)
        return None

    def GenerateForm(self, indent):
        return "This is pure virtual"

    def AddKeyFlag(self, value, desc, selected):
        return "This is pure virtual"

    def AddKeyChoice(self, value, desc):
        return "This is pure virtual"

class KeyString(Key):
    def __init__(self):
        Key.__init__(self)

    def GenerateForm(self, indent):
        s = quarkx.newobj(self.m_keyname + ":")
        s["txt"] = "&"
        s["hint"] = self.m_desc
        indent.appenditem(s)
        return s

class KeyInput(Key):
    def __init__(self):
        Key.__init__(self)
        self.m_kind='input'
    	print 'create input',self.m_keyname

    def GenerateForm(self, indent):
    	print 'generate input',self.m_keyname
        s = quarkx.newobj(self.m_kind+'_'+self.m_keyname + ":")
        s["txt"] = "&"
        s["inp"] = self.m_keyname
        s["hint"] = self.m_desc
        indent.appenditem(s)
        return s

class KeyOutput(Key):
    def __init__(self):
        Key.__init__(self)
        self.m_kind='output'
    	print 'create output',self.m_keyname

    def GenerateForm(self, indent):
    	print 'generate output',self.m_keyname
        s = quarkx.newobj(self.m_kind+'_'+self.m_keyname + ":")
        s["txt"] = "&"
        s["outp"] = self.m_keyname
        s["hint"] = self.m_desc
        indent.appenditem(s)
        return s

class KeyNumeric(Key):
    def __init__(self):
        Key.__init__(self)

    def GenerateForm(self, indent):
        s = quarkx.newobj(self.m_keyname + ":")
        s["txt"] = "&"
        s["hint"] = self.m_desc
        indent.appenditem(s)
        return None

class KeyBool(Key):
    def __init__(self):
        Key.__init__(self)

    def GenerateForm(self, indent):
        s = quarkx.newobj(self.m_keyname + ":")
        s["txt"] = "&"
        s["hint"] = self.m_desc
        indent.appenditem(s)
        return None

class KeyStudio(Key):
    def __init__(self):
        Key.__init__(self)

    def GenerateForm(self, indent):
        s = quarkx.newobj(self.m_keyname + ":")
        s["txt"] = "&"
        s["hint"] = self.m_desc
        s["typ"] = "B"
        s["Cap"] = "models..."
        s["form"] = "t_models_hl2_form:form"
        indent.appenditem(s)
        return None

class KeyTexture(Key):
    def __init__(self):
        Key.__init__(self)

    def GenerateForm(self, indent):
        s = quarkx.newobj(self.m_keyname + ":")
        s["txt"] = "&"
        s["hint"] = self.m_desc
        s["typ"] = "ET"
        s["Cap"] = "texture..."
        indent.appenditem(s)
        return None


class KeyFlags(Key):
    def __init__(self):
        Key.__init__(self)
        self.m_flags = []

    def AddKeyFlag(self, value, desc, selected):
        self.m_flags = self.m_flags + [(value, desc)]
        if (int(selected) > 0):
            try:
                oldvalue = int(self.GetDefaultValue())
            except:
                oldvalue = 0
            self.SetDefaultValue(oldvalue + int(value))

    def GenerateForm(self, indent):
        s = ""
        nl = "" # no first newline
        for value, desc in self.m_flags:
          s = quarkx.newobj(self.m_keyname + ":")
          s["txt"] = "&"
          s["hint"] = ""
          s["typ"] = "X"+value
          s["cap"] = desc
          indent.appenditem(s)
        return None

class KeyChoices(Key):
    def __init__(self):
        Key.__init__(self)
        self.m_choices = []

    def AddKeyChoice(self, value, desc):
        self.m_choices = self.m_choices + [(value, desc)]

    def GenerateForm(self, indent):
        s = quarkx.newobj(self.m_keyname + ":")
        s["txt"] = "&"
        s["hint"] = self.m_desc
        s["typ"] = "C"
        indent.appenditem(s)
        it = ""
        vl = ""
        c = 0
        for value, desc in self.m_choices:
          it = it + desc
          vl = vl + value
          c = c + 1
          if (c <> len(self.m_choices)):
            it = it + "\r"
            vl = vl + "\r"
        s["items"] = it
        s["values"] = vl
        return None

## --------

INHERITPREFIX = "t_"

class Entity:
    def __init__(self):
        self.m_classname = None
        self.m_desc = ""
        self.m_keys = []
        self.m_inherit = []
        self.m_size = None
        self.m_color = None

    def Type(self):
        raise "This is pure virtual"

    def SetClassname(self, classname):
        self.m_classname = classname

    def SetDesc(self, desc):
        self.m_desc = desc

    def AddDesc(self, desc):
        self.m_desc += desc

    def SetSize(self, sizeargs):
        if (len(sizeargs) == 6):
            self.m_size = (float(sizeargs[0]), float(sizeargs[1]), float(sizeargs[2]),
                           float(sizeargs[3]), float(sizeargs[4]), float(sizeargs[5]))

    def InheritsFrom(self, inherit):
        self.m_inherit = self.m_inherit + [INHERITPREFIX + inherit]

    def AddKey(self, key):
        self.m_keys = self.m_keys + [key]

    def TypeForm(self):
        return ":form"

    def TypeIncl(self):
        return ":incl"

    def GetFolderStuff(self, s):
        return ""

    def GenerateFolder(self, indent):
        def SortedAppendItem(obj, subitem):
            i = 0
            for s in obj.subitems:
                if (s.shortname.lower() > subitem.shortname.lower()):
                    break
                i = i + 1
            obj.insertitem(i, subitem)

        s = quarkx.newobj(self.m_classname + self.Type())
        folder = indent
        p = s.name.find("_")
        if (p == -1):
            folder = indent.findname("other entities.qtxfolder")
            if (folder is None):
                folder = quarkx.newobj("other entities.qtxfolder")
                SortedAppendItem(indent, folder)
        else:
            folder = indent.findname(s.name[:p+1]+"* entities.qtxfolder")
            if (folder is None):
                folder = quarkx.newobj(s.name[:p+1]+"* entities.qtxfolder")
                SortedAppendItem(indent, folder)
        SortedAppendItem(folder, s)
        self.GetFolderStuff(s)
        s[";desc"] = self.m_desc
        founddefaults = 0
        for key in self.m_keys:
            k = key.GenerateFolder(s)

    def GenerateForm(self, indent): # Changed 4/30/2008 - creates :incl with :form data so mods can build on top of all entities
        if (self.m_classname.find("t_") == 0):                                    #Modified 4/30/2008 - If t_ exists dont put another
            s = quarkx.newobj(self.m_classname + self.TypeIncl())                 #                     And put :incl instead of :form
        else:                                                                     #Modified 4/30/2008 - Add t_ if it doesn't exist
            s = quarkx.newobj(INHERITPREFIX + self.m_classname + self.TypeIncl()) #                     And put :incl instead of :form
        if (self.m_size is not None):
            s["bbox"] = self.m_size
        for key in self.m_keys:
            key.GenerateForm(s)
        # Place "<keyword>=!"-statements at the _end_ of ":form" definitions, because of a problem which Decker found but can't solve.
        for inh in self.m_inherit:
            s.specificadd(inh+"=!")
        indent.appenditem(s)

    def GenerateRealForm(self, indent):                            # Function added 4/30/2008
        if (self.m_classname.find("t_") is not 0):                 #Adds the new :form -   entityname: =
            s = quarkx.newobj(self.m_classname + self.TypeForm())  #(just link to :incl)   {
            s[INHERITPREFIX + self.m_classname] = "!"              #                         t_entityname = !
            indent.appenditem(s)                                   #                       }

class BrushEntity(Entity):
    def __init__(self):
        Entity.__init__(self)

    def Type(self):
        return ":b"

    def GetFolderStuff(self, s):
        if (self.m_classname.lower() == "worldspawn"):
            return
#        s["angles"] = "0 0 0"
        s[";incl"] = "defpoly"

class PointEntity(Entity):
    def __init__(self):
        Entity.__init__(self)

    def Type(self):
        return ":e"

    def GetFolderStuff(self, s):
#        s["angles"] = "0 0 0"
        s["origin"] = "0 0 0"

class InheritEntity(Entity):
    def __init__(self):
        Entity.__init__(self)

    def SetClassname(self, classname):
        self.m_classname = INHERITPREFIX + classname

    def GenerateFolder(self, indent):
        return

    def Type(self):
        return

    def TypeForm(self):
        return ":"

## --------

theEntities = []
theEntity = None
theKey = None
currentclassname = None
currentkeyname = None
currentkeytype = None
currentinherit = None
currentinheritargs = None
currentkeyflag = None
currentkeychoice = None

def CreateClass(token):
    global theEntity, theEntities
    CloseClass("--CloseByCreateClass--")
    # Create entity-type
    if (token.lower() == "solidclass"):
        theEntity = BrushEntity()
    elif (token.lower() == "pointclass"):
        theEntity = PointEntity()
    elif (token.lower() == "baseclass"):
        theEntity = InheritEntity()
    elif (token.lower() == "keyframeclass"):
        theEntity = PointEntity()
    elif (token.lower() == "moveclass"):
        theEntity = PointEntity()
    elif (token.lower() == "pointclass"):
        theEntity = PointEntity()
    elif (token.lower() == "filterclass"):
        theEntity = PointEntity()
    elif (token.lower() == "npcclass"):
        theEntity = PointEntity()
    else:
        raise "Unknown @-token:", token

def CloseClass(token):
    global theEntity, theEntities
    # Add to large list of entities
    if (theEntity is not None):
        theEntities = theEntities + [theEntity]

def BeginInherit(token):
    global currentinherit, currentinheritargs
    EndInherit("--EndByBeginInherit--")
    currentinherit = token.lower()
    currentinheritargs = []

def AddInherit(token):
    global currentinherit, currentinheritargs
    currentinheritargs = currentinheritargs + [token]

def EndInherit(token):
    global currentinherit, currentinheritargs, theEntity
    if (currentinherit is None):
        return
    if (currentinherit == "base"):
        for arg in currentinheritargs:
            theEntity.InheritsFrom(arg)
    elif (currentinherit == "size"):
        theEntity.SetSize(currentinheritargs)
    else:
        pass
    currentinherit = None

def BeginClassname(token):
    global currentclassname, theEntity
    EndClassname("--EndByBeginClassname--")
    currentclassname = token
    theEntity.SetClassname(token)

def AddClassnameDesc(token):
    global theEntity
    theEntity.AddDesc(token)

def EndClassname(token):
    global currentclassname
    if (currentclassname is None):
        return
    EndKey("--EndByEndClassname--")
    currentclassname = None

def BeginKey(token):
    global currentkeyname
    EndKey("--EndByBeginKey--")
    currentkeyname = token

def SetInput(token):
    global currentkeytype
    EndKey("--EndByBeginKey--")
    currentkeytype = 'input'

def SetOutput(token):
    global currentkeytype
    EndKey("--EndByBeginKey--")
    currentkeytype = 'output'

def AddKeyType(token):
    global currentkeyname, theKey
    # Determine what type this key is, so the correct object can be created
    token = token.lower()
    if (token == "integer" or token =='float' or token == 'node_dest'):
        theKey = KeyNumeric()
    elif (token == "string" \
       or token == "target_source" \
       or token == "target_destination" \
       or token == "color1" \
       or token == "color255" \
       or token == "sound" \
       or token == "sprite" \
       or token == "angle" \
       or token == "origin" \
       or token == "filterclass" \
       or token == "npcclass" \
       or token == "target_name_or_class" \
       or token == "pointentityclass" \
       or token == "scene"):
#       or token == "decal"):
        theKey = KeyString()
    elif (token == "flags"):
        theKey = KeyFlags()
    elif (token == "choices"):
        theKey = KeyChoices()
    elif (token == "void"):
        theKey = KeyString()       #tbd 
    elif (token == "vector"):
        theKey = KeyString()       #tbd 
    elif (token == "vecline"):
        theKey = KeyString()       #tbd 
    elif (token == "axis"):
        theKey = KeyString()       #tbd 
    elif (token == "sidelist"):
        theKey = KeyString()       #tbd 
    elif (token == "material"):
        theKey = KeyTexture()       #tbd 
    elif (token == "decal"):
        theKey = KeyTexture()       #tbd 
    elif (token == "bool"):
        theKey = KeyBool()       #tbd 
    elif (token == "studio"):
        theKey = KeyStudio()
    else:
        raise "Unknown KeyType-token:", token
    theKey.SetKeyname(currentkeyname)

def AddKeyDesc(token):
    global theKey
    theKey.AddDesc(token)

def AddKeyDefa(token):
    global theKey
    theKey.SetDefaultValue(token)

def AddKeyFlagNum(token):
    global currentkeyflag
    EndKeyFlag("--EndByAddKeyFlagNum--")
    currentkeyflag = token

def AddKeyFlagStr(token):
    global currentkeyflag
    EndKeyFlag("--EndByAddKeyFlagNum--")
    currentkeyflag = token

def AddKeyFlagDesc(token):
    global currentkeyflag
    value = currentkeyflag
    currentkeyflag = (value, token)

def AddKeyFlagDefa(token):
    global currentkeyflag
    value, desc = currentkeyflag
    currentkeyflag = (value, desc, token)

def EndKeyFlag(token):
    global currentkeyflag, theKey
    if (currentkeyflag is None):
        return
    value, desc, selected = currentkeyflag
    theKey.AddKeyFlag(value, desc, selected)
    currentkeyflag = None

def AddKeyChoiceNum(token):
    global currentkeychoice
    EndKeyChoice("--EndByAddKeyChoiceNum--")
    currentkeychoice = token

def AddKeyChoiceStr(token):
    global currentkeychoice
    EndKeyChoice("--EndByAddKeyChoiceStr--")
    currentkeychoice = token

def AddKeyChoiceDesc(token):
    global currentkeychoice
    value = currentkeychoice
    currentkeychoice = (value, token)

def EndKeyChoice(token):
    global currentkeychoice, theKey
    if (currentkeychoice is None):
        return
    value, desc = currentkeychoice
    theKey.AddKeyChoice(value, desc)
    currentkeychoice = None

def EndKey(token):
    global currentkeyname, theEntity, theKey,currentkeytype
    if (currentkeyname is None):
        return
    if (theKey is None or theEntity is None):
        raise "Failure in EndKey()"
    if (currentkeytype != None):
    	print currentkeytype,currentkeyname
    	theKey.m_keyname = currentkeytype+'#'+theKey.m_keyname
    theEntity.AddKey(theKey)
    currentkeyname = None
    currentkeytype = None

def EndKeyFlags(token):
    EndKeyFlag("--EndByEndKeyFlags--")
    EndKey(token)

def EndKeyChoices(token):
    EndKeyChoice("--EndByEndKeyChoices--")
    EndKey(token)

## ------------

def readentirefile(file):
    f = open(file, "r")
    filecontents = ""
    while 1:
        line = f.readline()
        if not line:
            break
        line = line.strip()
        line = line.split("//")[0] # Remove end-of-line comments
        line = line.split("@include")[0] # Added 4/30/2008 - Remove @include statements
        line = line.split("@mapsize")[0] # Added 4/30/2008 - Remove @mapsize statements
        if line:
            filecontents = filecontents + line + "\n"
    f.close()
    return filecontents
TYPE_UNKNOWN    = 0
TYPE_NUMERIC    = 1
TYPE_STRING     = 2
TYPE_SYMBOL     = 3
TYPE_HALFGRIDSNAP       = 4     # 'halfgridsnap' Added 4/30/2008 to fix 'halfgridsnap' error
TYPE_READONLY           = 5     # 'readonly' Added 4/30/2008 to fix 'readonly' error
TYPE_SPLITTER_AT        = 10    # '@'
TYPE_SPLITTER_COLON     = 11    # ':'
TYPE_SPLITTER_EQUAL     = 12    # '='
TYPE_SPLITTER_SQUARE_B  = 13    # '['
TYPE_SPLITTER_SQUARE_E  = 14    # ']'
TYPE_SPLITTER_PRNTSHS_B = 15    # '('
TYPE_SPLITTER_PRNTSHS_E = 16    # ')'
TYPE_SPLITTER_COMMA     = 17    # ','
TYPE_INPUT              = 18    # 'input'
TYPE_OUTPUT             = 19    # 'output'
TYPE_SPLITTER_PLUS      = 20    # '+'

toktypes={
0  :'TYPE_UNKNOWN',        
1  :'TYPE_NUMERIC',        
2  :'TYPE_STRING',        
3  :'TYPE_SYMBOL',
#Added 4/30/2008 to fix 'halfgridsnap' error ,
4  :'TYPE_HALFGRIDSNAP',
#Added 4/30/2008 to fix 'readonly' error ,
5  :'TYPE_READONLY',
10 :'TYPE_SPLITTER_AT',
11 :'TYPE_SPLITTER_COLON',
12 :'TYPE_SPLITTER_EQUAL',
13 :'TYPE_SPLITTER_SQUARE_B',
14 :'TYPE_SPLITTER_SQUARE_E',
15 :'TYPE_SPLITTER_PRNTSHS_B',
16 :'TYPE_SPLITTER_PRNTSHS_E',
17 :'TYPE_SPLITTER_COMMA',
18 :'TYPE_INPUT',
19 :'TYPE_OUTPUT',
20 :'TYPE_SPLITTER_PLUS'}


CHARS_NUMERIC  = "-0123456789."
CHARS_STRING   = "\""
CHARS_SPLITTER = "@:=[](),+"

def getnexttoken(srcstring):
    def nextnonwhitespace(srcstring):
        i = 0
        while (srcstring[i] in " \t\n\r"):
            i = i + 1
        return srcstring[i:]

    def gettoken(srcstring, delims=None):
        token = ""
        i = 0
        if delims is None:
            delims = " \t\n\r" + CHARS_SPLITTER
        if not (srcstring[i] in delims):
            token = token + srcstring[i]
            i = i + 1
        while not (srcstring[i] in delims):
            token = token + srcstring[i]
            i = i + 1
        return token, srcstring[i:]

    token_is = TYPE_UNKNOWN
    srcstring = nextnonwhitespace(srcstring)
    if (not srcstring):
        return None, TYPE_UNKNOWN, srcstring

    if (srcstring[0] in CHARS_NUMERIC):
        token_is = TYPE_NUMERIC
        token, srcstring = gettoken(srcstring)
    elif (srcstring[0] in CHARS_STRING):
        token_is = TYPE_STRING
        token, srcstring = gettoken(srcstring[1:], CHARS_STRING)
        srcstring = srcstring[1:] # Jump over the last " character
    elif (srcstring[0] in CHARS_SPLITTER):
        token = srcstring[0]
        srcstring = srcstring[1:] # Jump over the splitter character
        if (token == "@"):
            token_is = TYPE_SPLITTER_AT
        elif (token == ":"):
            token_is = TYPE_SPLITTER_COLON
        elif (token == "="):
            token_is = TYPE_SPLITTER_EQUAL
        elif (token == "["):
            token_is = TYPE_SPLITTER_SQUARE_B
        elif (token == "]"):
            token_is = TYPE_SPLITTER_SQUARE_E
        elif (token == "("):
            token_is = TYPE_SPLITTER_PRNTSHS_B
        elif (token == ")"):
            token_is = TYPE_SPLITTER_PRNTSHS_E
        elif (token == ","):
            token_is = TYPE_SPLITTER_COMMA
        elif (token == "+"):
            token_is = TYPE_SPLITTER_PLUS
    else:
        token, srcstring = gettoken(srcstring)
        if (token == 'input'):
          token_is = TYPE_INPUT
        elif (token == 'output'):
          token_is = TYPE_OUTPUT
        elif (token == 'halfgridsnap'): # Added 4/30/2008
          token_is = TYPE_HALFGRIDSNAP  # To fix 'halfgridsnap' error
        elif (token == 'readonly'): # Added 4/30/2008
          token_is = TYPE_READONLY  # To fix 'readonly' error
        else:
          token_is = TYPE_SYMBOL
    return token, token_is, srcstring


statediagram =                                                                                  \
{                                                                                               \
# Current state            Token-type to go to ->    Next state             Function to call with token \
 'STATE_UNKNOWN'        :[(TYPE_SPLITTER_AT        ,'STATE_CLASSBEGIN'     ,None)             ] \
                                                                                                \
,'STATE_CLASSBEGIN'     :[(TYPE_SYMBOL             ,'STATE_CLASSINHERIT'   ,CreateClass)      ] \
# Added TYPE_HALFGRIDSNAP here 4/30/2008 to fix 'halfgridsnap' error                            \
,'STATE_CLASSINHERIT'   :[(TYPE_HALFGRIDSNAP       ,'STATE_CLASSINHERIT'   ,None)               \
                         ,(TYPE_SYMBOL             ,'STATE_INHERITBEGIN'   ,BeginInherit)       \
                         ,(TYPE_SPLITTER_EQUAL     ,'STATE_CLASSNAME'      ,None)             ] \
                                                                                                \
,'STATE_INHERITBEGIN'   :[(TYPE_SPLITTER_PRNTSHS_B ,'STATE_INHERITMEDIUM'  ,None)             ] \
                                                                                                \
,'STATE_INHERITMEDIUM'  :[(TYPE_SYMBOL             ,'STATE_INHERITMEDIUM'  ,AddInherit)         \
                         ,(TYPE_NUMERIC            ,'STATE_INHERITMEDIUM'  ,AddInherit)         \
                         ,(TYPE_STRING             ,'STATE_INHERITMEDIUM'  ,AddInherit)         \
                         ,(TYPE_SPLITTER_COMMA     ,'STATE_INHERITMEDIUM'  ,None)               \
                         ,(TYPE_SPLITTER_PRNTSHS_E ,'STATE_CLASSINHERIT'   ,EndInherit)       ] \
                                                                                                \
,'STATE_CLASSNAME'      :[(TYPE_SYMBOL             ,'STATE_CLASSNAME2'     ,BeginClassname)   ] \
                                                                                                \
,'STATE_CLASSNAME2'     :[(TYPE_SPLITTER_COLON     ,'STATE_CLASSNAME3'     ,None)               \
                         ,(TYPE_SPLITTER_SQUARE_B  ,'STATE_KEYSBEGIN'      ,None)             ] \
                                                                                                \
,'STATE_CLASSNAME3'     :[(TYPE_STRING             ,'STATE_CLASSNAME3'     ,AddClassnameDesc)   \
                         ,(TYPE_SPLITTER_PLUS      ,'STATE_CLASSNAME3'     ,None)               \
                         ,(TYPE_SPLITTER_SQUARE_B  ,'STATE_KEYSBEGIN'      ,None)             ] \
                                                                                                \
                                                                                                \
,'STATE_KEYSBEGIN'      :[(TYPE_SPLITTER_SQUARE_E  ,'STATE_UNKNOWN'        ,EndClassname)       \
                         ,(TYPE_SYMBOL             ,'STATE_KEYBEGIN'       ,BeginKey)           \
                         ,(TYPE_INPUT              ,'STATE_INPUTBEGIN'     ,SetInput)           \
                         ,(TYPE_OUTPUT             ,'STATE_OUTPUTBEGIN'    ,SetOutput)        ] \
                                                                                                \
,'STATE_INPUTBEGIN'     :[(TYPE_SYMBOL             ,'STATE_KEYBEGIN'       ,BeginKey)         ] \
                                                                                                \
,'STATE_OUTPUTBEGIN'    :[(TYPE_SYMBOL             ,'STATE_KEYBEGIN'       ,BeginKey)         ] \
                                                                                                \
,'STATE_KEYBEGIN'       :[(TYPE_SPLITTER_PRNTSHS_B ,'STATE_KEYTYPE'        ,None)             ] \
                                                                                                \
,'STATE_KEYTYPE'        :[(TYPE_SYMBOL             ,'STATE_KEYTYPE2'       ,AddKeyType)       ] \
                                                                                                \
,'STATE_KEYTYPE2'       :[(TYPE_SPLITTER_PRNTSHS_E ,'STATE_KEYTYPE3'       ,None)             ] \
# Added TYPE_READONLY here 4/30/2008 to fix 'readonly' error                                    \
,'STATE_KEYTYPE3'       :[(TYPE_SPLITTER_EQUAL     ,'STATE_VALUEFLAGS'     ,None)               \
                         ,(TYPE_READONLY           ,'STATE_KEYTYPE3'       ,None)               \
                         ,(TYPE_SYMBOL             ,'STATE_KEYBEGIN'       ,BeginKey)           \
                         ,(TYPE_SPLITTER_COLON     ,'STATE_VALUE'          ,None)               \
                         ,(TYPE_SPLITTER_SQUARE_E  ,'STATE_UNKNOWN'        ,EndClassname)       \
                         ,(TYPE_INPUT              ,'STATE_INPUTBEGIN'     ,BeginKey)           \
                         ,(TYPE_OUTPUT             ,'STATE_OUTPUTBEGIN'    ,BeginKey)         ] \
                                                                                                \
,'STATE_VALUEFLAGS'     :[(TYPE_SPLITTER_SQUARE_B  ,'STATE_VALUEFLAGS2'    ,None)             ] \
                                                                                                \
,'STATE_VALUEFLAGS2'    :[(TYPE_SPLITTER_SQUARE_E  ,'STATE_KEYSBEGIN'      ,EndKeyFlags)        \
                         ,(TYPE_NUMERIC            ,'STATE_VALUEFLAG'      ,AddKeyFlagNum)    ] \
                                                                                                \
,'STATE_VALUEFLAG'      :[(TYPE_SPLITTER_COLON     ,'STATE_VALUEFLAG2'     ,None)             ] \
                                                                                                \
,'STATE_VALUEFLAG2'     :[(TYPE_STRING             ,'STATE_VALUEFLAG3'     ,AddKeyFlagDesc)   ] \
                                                                                                \
,'STATE_VALUEFLAG3'     :[(TYPE_SPLITTER_COLON     ,'STATE_VALUEFLAG4'     ,None)             ] \
                                                                                                \
,'STATE_VALUEFLAG4'     :[(TYPE_NUMERIC            ,'STATE_VALUEFLAGS2'    ,AddKeyFlagDefa)   ] \
                                                                                                \
,'STATE_VALUE'          :[(TYPE_STRING             ,'STATE_VALUE'          ,AddKeyDesc)         \
                         ,(TYPE_SPLITTER_PLUS      ,'STATE_VALUE'          ,None)               \
                         ,(TYPE_SYMBOL             ,'STATE_KEYBEGIN'       ,BeginKey)           \
                         ,(TYPE_SPLITTER_SQUARE_E  ,'STATE_UNKNOWN'        ,EndClassname)       \
                         ,(TYPE_SPLITTER_COLON     ,'STATE_VALUE3'         ,None)               \
                         ,(TYPE_SPLITTER_EQUAL     ,'STATE_CHOICES'        ,None)               \
                         ,(TYPE_INPUT              ,'STATE_INPUTBEGIN'     ,SetInput)           \
                         ,(TYPE_OUTPUT             ,'STATE_OUTPUTBEGIN'    ,SetOutput)        ] \
                                                                                                \
,'STATE_VALUE3'         :[(TYPE_NUMERIC            ,'STATE_VALUE4'         ,AddKeyDefa)         \
                         ,(TYPE_STRING             ,'STATE_VALUE4'         ,AddKeyDefa)         \
                         ,(TYPE_SPLITTER_COLON     ,'STATE_VALUE5'         ,None)             ] \
                                                                                                \
,'STATE_VALUE4'         :[(TYPE_SYMBOL             ,'STATE_KEYBEGIN'       ,BeginKey)           \
                         ,(TYPE_SPLITTER_SQUARE_E  ,'STATE_UNKNOWN'        ,EndClassname)       \
                         ,(TYPE_SPLITTER_COLON     ,'STATE_VALUE5'         ,None)               \
                         ,(TYPE_SPLITTER_EQUAL     ,'STATE_CHOICES'        ,None)               \
                         ,(TYPE_INPUT              ,'STATE_INPUTBEGIN'     ,SetInput)           \
                         ,(TYPE_OUTPUT             ,'STATE_OUTPUTBEGIN'    ,SetOutput)        ] \
                                                                                                \
,'STATE_VALUE5'         :[(TYPE_STRING             ,'STATE_VALUE5'         ,None)               \
                         ,(TYPE_SPLITTER_PLUS      ,'STATE_VALUE5'         ,None)               \
                         ,(TYPE_SYMBOL             ,'STATE_KEYBEGIN'       ,BeginKey)           \
                         ,(TYPE_SPLITTER_SQUARE_E  ,'STATE_UNKNOWN'        ,EndClassname)       \
                         ,(TYPE_SPLITTER_EQUAL     ,'STATE_CHOICES'        ,None)               \
                         ,(TYPE_INPUT              ,'STATE_INPUTBEGIN'     ,SetInput)           \
                         ,(TYPE_OUTPUT             ,'STATE_OUTPUTBEGIN'    ,SetOutput)        ] \
                                                                                                \
,'STATE_CHOICES'        :[(TYPE_SPLITTER_SQUARE_B  ,'STATE_CHOICES2'       ,None)             ] \
,'STATE_CHOICES2'       :[(TYPE_SPLITTER_SQUARE_E  ,'STATE_KEYSBEGIN'      ,EndKeyChoices)      \
                         ,(TYPE_STRING             ,'STATE_CHOICES3'       ,AddKeyChoiceStr)    \
                         ,(TYPE_NUMERIC            ,'STATE_CHOICES3'       ,AddKeyChoiceNum)  ] \
                                                                                                \
,'STATE_CHOICES3'       :[(TYPE_SPLITTER_COLON     ,'STATE_CHOICES4'       ,None)             ] \
                                                                                                \
,'STATE_CHOICES4'       :[(TYPE_STRING             ,'STATE_CHOICES2'       ,AddKeyChoiceDesc) ] \
}

import quarkpy.qutils
import quarkx

def makeqrk(root, filename, gamename, nomessage=0):
    global theEntities, theEntity, theKey, currentclassname, currentkeyname, currentkeytype, currentinherit, currentinheritargs, currentkeyflag, currentkeychoice

    count = 0
    for item in root.subitems:
        if count == 0:
            count = 1
            continue
        root.removeitem(item)

    if nomessage == 0:
        quarkx.msgbox("Please note, this is not always 100% accurate may duplicate\nexisting entities and possibly miss some out.\n\nYou may need to handedit the .qrk file. For help with this,\nfeel free to ask questions on the QuArK forum.", quarkpy.qutils.MT_INFORMATION, quarkpy.qutils.MB_OK)
    srcstring = readentirefile(filename)
    state = 'STATE_UNKNOWN'
    while (len(srcstring) > 1):
        token, token_is, srcstring = getnexttoken(srcstring)
        print "\ntoken:",token
        print "token_is:",toktypes[token_is]
        print "nextstring:",srcstring[:64]
        # Figure out, if the token_is type is expected or not
        expectedtypes = []
        newstate = None
        defaultstate=None
        typestates = statediagram[state]
        for type, nextstate, func in typestates:
            if (type == token_is):
                # We found the correct token type, now remember what new state we're going into
                newstate = nextstate
                break
            expectedtypes = expectedtypes + [type]
        if newstate is None:
       #     print "Parse error: Got type", toktypes[token_is], "but expected type(s);", [toktypes[i] for i in expectedtypes]
       #     print "Debug: Last classname was =", currentclassname
       #     print "Debug:", srcstring[:64]
       #     raise "Parse error!"
            if func == "None":
                func_str = "None"
            else:
                func_str = str(func)
            quarkx.beep()
            quarkx.msgbox("PARSE ERROR !\nNon-supported Entity Definition file(s) format.\n\nGot type " + str(toktypes[token_is]) + "\nbut expected type(s): " + str([toktypes[i] for i in expectedtypes]) + "\n\nDebug: Last classname was = " + str(currentclassname) + "\nDebug: " + str(srcstring[:64]) + "\nDebug - Associated function: " + func_str + "\n\nContact QuArK development team with copy of Entity file(s).", quarkpy.qutils.MT_ERROR, quarkpy.qutils.MB_ABORT)
            return None
        if (func is not None):
            # This state have a function attached to it. Call it giving it the found token.
            func(token)
        # Change to new state
        state = newstate
    CloseClass("--EndByEOF--")
    indent = 2
    r_tbx = quarkx.newobj("Toolbox Folders.qtx")
    r_tbx["Toolbox"] = "New map items..."
    r_tbx.flags = r_tbx.flags | quarkpy.qutils.OF_TVSUBITEM
    root.appenditem(r_tbx)

    e_tbx = quarkx.newobj("Entities for "+gamename.split("\\")[-1]+".qtxfolder")
    e_tbx[";desc"] = "Created from "+filename.split("\\")[-1]
    r_tbx.appenditem(e_tbx)

    r_tbx["Root"] = e_tbx.name

    for ent in theEntities:
        ent.GenerateFolder(e_tbx)

    f_tbx = quarkx.newobj("Entity Forms.fctx")
    f_tbx.flags = f_tbx.flags | quarkpy.qutils.OF_TVSUBITEM
    root.appenditem(f_tbx)
  
    for ent in theEntities:
        ent.GenerateForm(f_tbx)
        ent.GenerateRealForm(f_tbx) # Added 4/30/2008 - creates :form with link to associated :incl

    root.refreshtv()

    if nomessage == 0:
        quarkx.msgbox("The .FGD file have now almost been converted to QuArK format.\n\nWhat remains is to save it as a 'Structured text for hand-editing (*.qrk)' file, then using a text-editor do a Search-Replace of   \"!\"   with   !\nE.g. replacing a double-quoted exclamation mark, with just a exclamation mark.\n\nIf you encounter any problems using this 'Convert from Worldcraft .FGD file' utility, please post a mail in the QuArK-forum.", quarkpy.qutils.MT_INFORMATION, quarkpy.qutils.MB_OK)

    # To reset all the globals to avoid duplications if the file is called to be remade without closing QuArK.
    theEntities = []
    theEntity = None
    theKey = None
    currentclassname = None
    currentkeyname = None
    currentkeytype = None
    currentinherit = None
    currentinheritargs = None
    currentkeyflag = None
    currentkeychoice = None

    return root

import quarkpy.qentbase
quarkpy.qentbase.RegisterEntityConverter("Worldcraft .fgd file", "Worldcraft .fgd file", "*.fgd", makeqrk)

# ----------- REVISION HISTORY ------------
#$Log: entfgd2qrk.py,v $
#Revision 1.17  2009/02/11 15:39:07  danielpharos
#Updated link to forum.
#
#Revision 1.16  2008/05/04 07:30:41  cdunde
#Changes by Adam Quest (aka Who Gives A Dam)
#Replaced GenerateFolder in Class Entity with
#  one from entdef2qrk.py v1.11 in order to
#  output toolbox alphabetically
#Minor modifications to makeqrk function to
#  make it more resemble entdef2qrk.py v1.11's
#
#Revision 1.15  2008/05/01 16:01:22  cdunde
#Changes by 'Who Gives A Dam'
#Look for comments dated 4/30/2008 in code.
#Fixed 'readonly' and 'halfgridsnap' parsing
#  didn't enable ER entry field functionality
#  nor 'halfgridsnap' functionality
#Now capable of removing @include and @mapsize
#All entries in fgd now have an :incl statement
#  and entities all have a :form that just links
#  to the :incl so all future mods can base
#  entities off other already defined entities
#
#Revision 1.14  2005/11/10 18:03:04  cdunde
#Activate history log
#
#Revision 1.13  2005/10/15 00:49:51  cdunde
#To reinstate headers and history
#
#Revision 1.11  2004/12/23 10:11:10  alexander
#removed bloody duplicated rcs headers again
#
#Revision 1.10  2004/12/19 09:59:48  alexander
#no default angle specifics
#generate model form button for studio specifics
#generate texture form button for texture and decal specifics
#support for input and output type specifics (input#specificname)
#
#Revision 1.9  2004/12/08 21:10:55  alexander
#can parse hl2 and hl2 mp hammer files now
#
#Revision 1.8  2004/12/07 17:59:52  alexander
#parse almost all of hammers fgd file except
#- readonly
#- halfgridsnap
#- include directives
#
#Revision 1.7  2004/12/01 21:48:29  alexander
#preliminary hammer files parsed
#
#Revision 1.6  2003/12/17 13:58:59  peter-b
#- Rewrote defines for setting Python version
#- Removed back-compatibility with Python 1.5
#- Removed reliance on external string library from Python scripts
#
#Revision 1.5  2002/02/05 18:32:58  decker_dk
#Corrected a problem with debug() calls
#
#Revision 1.4  2001/12/02 09:57:45  decker_dk
#Removing 'os' from the import list, and some other minor fixes.
#
#Revision 1.3  2001/10/21 08:34:42  decker_dk
#Print out debug-information, in case of parse-error.
#
#Revision 1.2  2001/08/13 17:45:30  decker_dk
#Problem with "<keyword>=!" placements in ":form" definitions. Hard to solve correctly, as its deep within QuArK's Delphi-code!
#
#Revision 1.1  2001/06/13 23:02:50  aiv
#Moved 'Convert From' stuff to python code (plugin type)
#
#Revision 1.4  2001/06/11 17:42:38  decker_dk
#Fixed the BBOX problem, where it would think the value were a string (double-quotes), and not 6 numbers (single-quotes).
#Also added a messagebox which states what should be manually done afterwards.
#
#Revision 1.3  2001/04/14 19:30:58  decker_dk
#Handle 'color1' FGD-types too.
#
#
