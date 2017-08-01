"""   QuArK  -  Quake Army Knife

 ConvertToolGet_tokens.py - token parsing library (sort of)
            - Rowdy Nov. 28, 2004 - added by cdunde March 30, 2008
"""

#
#$Header: /cvsroot/quark/runtime/plugins/ConvertToolGet_tokens.py,v 1.4 2008/04/19 00:48:56 cdunde Exp $
#

NUMBERS = '0123456789-.'
ALPHAS  = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_'

# "tokenType" nbr,       what it is
T_EOF        = 1
T_NUMBER     = 2
T_COMMENT    = 3
T_COMMENT    = 4
T_QSTRING    = 5  # specific and argument
T_IDENTIFIER = 6
T_SPECIAL    = 7

srcLine = ''
srcPos = 0

def unGetChar(ch):
    global srcLine, srcPos
    if srcPos > 0:
        srcPos -= 1
    else:
        srcLine = ch + srcLine

def getChar(infile):
    global srcLine, srcPos
    if srcPos >= len(srcLine):
        srcLine = infile.readline()
        if srcLine == "":
            return chr(4) # eof
        srcPos = 0
    result = srcLine[srcPos]
    if result == '\r':
        result = '\n'
    srcPos += 1
    return result

def getToken(infile, shaders):
    if shaders == 0:
        nbrlist = '0123456789-.'
        alphalist = '_/.'
    else:
        nbrlist = '0123456789.'
        alphalist = '_/.-'
    result = ''
    ch = getChar(infile)
    while ch.isspace():
        ch = getChar(infile)
    if ch == chr(4):
        return T_EOF, None
    # is it a number, ident, quoted string or special?
    if ch in nbrlist:
        result = ch
        ch = getChar(infile)
        while ch in '0123456789.':
            result += ch
            ch = getChar(infile)
        unGetChar(ch)
        return T_NUMBER, result
    if ch == '/':
        # comment???
        ch = getChar(infile)
        if ch == '/':
            # single line comment - read until eoln
            result = '/'
            while (ch != chr(4)) and (ch != '\n'):
                result += ch
                ch = getChar(infile)
            # we don't need to do this: unGetChar(ch)
            return T_COMMENT, result
        if ch == '*':
            # multiline comment - read until end of multiline comment
            result = '/'
            lastCh = '/'
            while (ch != chr(4)) and ((ch != '/') or (lastCh != '*')):
                lastCh = ch
                result += ch
                ch = getChar(infile)
            result += ch
            # we don't want to do this here: unGetChar(ch)
            return T_COMMENT, result
        # not a comment, push the last char back and let's keep comparing
        unGetChar(ch)
    if ch == '"':
        # quoted string - read until the next quote
        result = '"'
        ch = getChar(infile)
        while (ch != chr(4)) and (ch != '"'):
            result += ch
            ch = getChar(infile)
        result += ch
        # we don't want to do this here: unGetChar(ch)
        return T_QSTRING, result
    if ch.isalpha() or (ch == '_'):
        # identifier (probably, or something fairly close to it)
        # might also be a (UNIX) pathname
        result = ch
        ch = getChar(infile)
        while (ch != chr(4)) and (ch.isalnum() or (ch in alphalist)):
            result += ch
            ch = getChar(infile)
        unGetChar(ch)
        return T_IDENTIFIER, result
    # dunno what we've got, treat it as special
    return T_SPECIAL, ch

def getTokens(inname, shaders=0):
    infile = open(inname)
    result = []
    while 1:
        tokenType, tokenValue = getToken(infile, shaders)
        result.append((tokenType, tokenValue))
        if tokenType == T_EOF:
            break
    infile.close()
    return result

if __name__ == "__main__":
    print
    print "You are not supposed to run this, usage is:"
    print ""
    print ">>> from get_tokens import *"
    print '>>> tokens = getTokens(gamefileslocation + "\\" + filesfoldername + "\\" + name)'
    print ""
    print ">>> See plugins AddsShadersList.py for example of its usage."

#
#$Log: ConvertToolGet_tokens.py,v $
#Revision 1.4  2008/04/19 00:48:56  cdunde
#Made changes to sort material lists, cleanup dead ones and improved missing ones.
#
#Revision 1.3  2008/04/11 22:27:09  cdunde
#Update
#
#Revision 1.2  2008/04/04 23:20:08  cdunde
#Needed correction.
#
#Revision 1.1  2008/04/04 20:19:28  cdunde
#Added a new Conversion Tools for making game support QuArK .qrk files.
#
#

