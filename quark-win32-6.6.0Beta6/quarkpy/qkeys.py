"""   QuArK  -  Quake Army Knife

Keyboard constants and utilities
"""
#
# Copyright (C) 1996-99 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/quarkpy/qkeys.py,v 1.5 2005/10/15 00:47:57 cdunde Exp $


# Virtual Keys, Standard Set
# P.S. don't ask me (Armin) what some of these keys are !
# I don't know... The list below is just taken from the Win32 doc.
LBUTTON = '\001'    # mouse
RBUTTON = '\002'    # mouse
CANCEL = '\003'
MBUTTON = '\004'    # mouse
BACK = '\010'
TAB = '\011'
CLEAR = '\014'
RETURN = '\015'
SHIFT = '\020'
CONTROL = '\021'
MENU = '\022'       # this is ALT
PAUSE = '\023'
CAPITAL = '\024'
ESCAPE = '\033'
SPACE = ' '
PRIOR = '!'
NEXT = '"'
END = '#'
HOME = '$'
LEFT = '%'
UP = '&'
RIGHT = "'"
DOWN = '('
SELECT = ')'
PRINT = '*'
EXECUTE = '+'
SNAPSHOT = ','
INSERT = '-'
DELETE = '.'
HELP = '/'
# VK_0 thru VK_9 are the same as ASCII '0' thru '9'
# VK_A thru VK_Z are the same as ASCII 'A' thru 'Z'
LWIN = '['
RWIN = '\\'
APPS = ']'
NUMPAD0 = '`'
NUMPAD1 = 'a'
NUMPAD2 = 'b'
NUMPAD3 = 'c'
NUMPAD4 = 'd'
NUMPAD5 = 'e'
NUMPAD6 = 'f'
NUMPAD7 = 'g'
NUMPAD8 = 'h'
NUMPAD9 = 'i'
MULTIPLY = 'j'
ADD = 'k'
SEPARATOR = 'l'
SUBTRACT = 'm'
DECIMAL = 'n'
DIVIDE = 'o'
F1 = 'p'
F2 = 'q'
F3 = 'r'
F4 = 's'
F5 = 't'
F6 = 'u'
F7 = 'v'
F8 = 'w'
F9 = 'x'
F10 = 'y'
F11 = 'z'
F12 = '{'
F13 = '|'
F14 = '}'
F15 = '~'
F16 = '\177'
F17 = '\200'
F18 = '\201'
F19 = '\202'
F20 = '\203'
F21 = '\204'
F22 = '\205'
F23 = '\206'
F24 = '\207'
NUMLOCK = '\220'
SCROLL = '\221'
# LSHIFT = '\240'
# RSHIFT = '\241'      # left and right keys are not distinguished
# LCONTROL = '\242'
# RCONTROL = '\243'
# LMENU = '\244'       # left ALT
# RMENU = '\245'       # right ALT
PROCESSKEY = '\345'
ATTN = '\366'
CRSEL = '\367'
EXSEL = '\370'
EREOF = '\371'
PLAY = '\372'
ZOOM = '\373'
NONAME = '\374'
PA1 = '\375'
OEM_CLEAR = '\376'


# compute keyname dictionnary

def keynames():
    global _keynames
    try:
        return _keynames
    except NameError:
        _keynames = {}
        for item, value in globals().items():
            if type(value)==type('') and len(value)==1:
                _keynames[value] = item
        return _keynames
        
# ----------- REVISION HISTORY ------------
#
#
#$Log: qkeys.py,v $
#Revision 1.5  2005/10/15 00:47:57  cdunde
#To reinstate headers and history
#
#Revision 1.2  2000/06/02 16:00:22  alexander
#added cvs headers
#
#
#