"""   QuArK  -  Quake Army Knife

Amending functions of QuArK Map editor's "Addons" menu
"""
#
# Copyright (C) 1996-99 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

#$Header: /cvsroot/quark/runtime/plugins/map1addonsamendmenu.py,v 1.7 2010/02/21 15:42:49 danielpharos Exp $

Info = {
   "plug-in":       "Map1 Addons Amend Menu",
   "desc":          "This implements the Addons menu and Categories for adding and removing 3rd party programs.",
   "date":          "June 7 2003",
   "author":        "cdunde, Decker and others",
   "author e-mail": "cdunde1@attbi.com",
   "quark":         "Version 6.4" }


from quarkpy.maputils import *
import quarkpy.qmacro

# ****************** Add Menu Items Dialog ******************


class AddonsDlg (quarkpy.qmacro .dialogbox):
    #
    # dialog layout
    #

    endcolor = AQUA
    size = (300,155)
    dfsep = 0.35
    flags = FWF_KEEPFOCUS
    
    dlgdef = """
        {
        Style = "9"
        Caption = "Add Item Dialog"

        catagory: =
        {
        Typ = "C" Txt = "select catagory:"
            items =
                "Shape programs" $0D
                "Terrain programs" $0D
                "Other programs" $0D
            values =
                "1" $0D
                "2" $0D
                "3" $0D
        Hint = "Select a catagory of the Addons menu"$0D
               "to place the program menu item in."
        }

        program: =
        {
        Txt = "select program:"
        Typ = "EP"
        DefExt = "exe"
        BasePath = "C:"
        Hint = "Type in the full path and name of the program"$0D
               "you wish to add to this menu as a menu item"$0D
               "or just use the file browser ... to the right."$0D
        }

        mapfile: =
        {
        Txt = "select mapfile:"
        Typ = "EP"
        DefExt = "map"
        BasePath = "$Game\\tmpQuArK\maps"
        Hint = "Type in the full path and name of an optional"$0D
               "mapfile you wish to use for the programs output"$0D
               "or just use the file browser ... to the right."$0D
        }

        sep: = { Typ="S" Txt=" " }

        close:py = {Txt="" }
        cancel:py = {Txt="" }

    }
    """

    #
    # __init__ initialize the object
    #

    def __init__(self, form, editor, action):

    #
    # General initialization of some local values
    #

        self.editor = editor
        src = quarkx.newobj(":")
        self.src = src
        self.action = action
        self.form = form
        self.src["program"] = None
        self.src["mapfile"] = quarkx.outputfile(quarkx.getmapdir()+"\\1SaveImport.map")

    #
    # Create the dialog form and the buttons
    #

        quarkpy.qmacro.dialogbox.__init__(self, form, src,
        close = quarkpy.qtoolbar.button(
            self.close,
            "Add the selected program",
            ico_editor, 3,
            "Reload"),
        cancel = quarkpy.qtoolbar.button(
            self.cancel,
            "Cancel & close window",
            ico_editor, 0,
            "Cancel"))

    def onclose(self, dlg):
        if self.src is None:
            qmacro.dialogbox.onclose(self, dlg)
            return
        quarkx.globalaccept()
        self.action(self)
        qmacro.dialogbox.onclose(self, dlg)

    def cancel(self, dlg):
        self.src = None 
        qmacro.dialogbox.close(self, dlg)


#        ********** Addons FUNCTION Starts Here **********


def CreateMenuItems(self):

    catagory = self.src["catagory"]
    if catagory == "1":
        catagory = "ShapesMenu"
    if catagory == "2":
        catagory = "TerrainMenu"
    if catagory == "3":
        catagory = "OtherMenu"
    program = self.src["program"]
    words = program.split("\\")
    cmdline = words [-1]
    path_to_program = words [ 0 : -1 ]
    currentdir = "\\".join(path_to_program)
    words = cmdline.split(".")
    name =  words[0]
    name = name.replace(" ", "")
    mapfile = self.src["mapfile"]
    objfile = mapfile.replace("\\", "/")
    proglocate = program.replace("\\", "/")


    outfile = open(quarkx.exepath + "plugins\map1AddonsMenuEdit.py", "w")

    outfile.write("Info = {\n\n   'plug-in':       'Addons Menu Edit',")

    outfile.write("\n\n   'desc':          'This file stores the Addons Main menu, Category sub-menu items. It is created by the plugins map1addonsamendmenu.py file.',")

    outfile.write("\n\n   'date':          'June 7 2003',")

    outfile.write("\n\n   'author':        'cdunde, Decker and others',")

    outfile.write("\n\n   'author e-mail': 'cdunde1@attbi.com',")

    outfile.write("\n\n   'quark':         'Version 6.4' }\n\n")

    outfile.write("# Deleting this file well remove all items\n# added to the Addons Menu Categories.\n\n")

    outfile.write("from quarkpy.maputils import *\nimport quarkpy.mapeditor\nimport quarkpy.qmenu\nimport map1addonsmenu\n\n")

    outfile.write("# ================DO NOT DELETE ABOVE THIS LINE =================\n\n")

# New test line
    outfile.write("#===========================================\n\n")

    outfile.write("plugins.map1addonsmenu."+catagory+".items.append(qmenu.sep)\n\n")

    outfile.write("# ------------ Delete This Item ------------\n\n")

    outfile.write("# Menu Catagory: "+catagory+"\n")

    outfile.write("# Menu Title: Run "+name+"\n\n")

    outfile.write("def Run_"+name+"(self):\n    pass\n    cmdline = '"+cmdline+"'\n    currentdir = '"+currentdir+"'\n    quarkx.runprogram(cmdline, currentdir)\n\n")

    outfile.write("plugins.map1addonsmenu."+catagory+".items.append(quarkpy.qmenu.item('Run "+name+"', Run_"+name+",'|This programs location is:\\n\\n"+proglocate+"'))\n\n")

    outfile.write("# ------------ End Item Cutting ------------\n\n")

    outfile.write("# ------------ Delete This Item ------------\n\n")

    outfile.write("# Menu Catagory: "+catagory+"\n")

    outfile.write("# Menu Title: Import "+name+" map\n\n")

    outfile.write("def Load_"+name+"_Map(editor):\n    pass\n    editor = mapeditor()\n    info = quarkx.openfileobj('"+objfile+"')\n    mygroup = quarkx.newobj('group:g')\n")

    outfile.write("    mygroup.copyalldata(info.subitem(0))\n    quarkpy.mapbtns.dropitemsnow(editor, [mygroup], 'draw map')\n\n")

    outfile.write("plugins.map1addonsmenu."+catagory+".items.append(quarkpy.qmenu.item('Import "+name+" map', Load_"+name+"_Map,'|This maps location is:\\n\\n"+objfile+"'))\n\n")

    outfile.write("# ------------ End Item Cutting ------------\n\n")

    outfile.write("#===========================================\n\n")

    outfile.write("# End Of File\n")

    outfile.close()

#        ********** Addons FUNCTION Ends Here **********

def AddItemClick(m):
    def action(self):

        if self.src["catagory"] is None:
            quarkx.msgbox("You have not selected a catagory, nothing done", MT_ERROR, MB_OK)
            return
        if self.src["program"] is None:
            quarkx.msgbox("You have not entered a program, nothing done", MT_ERROR, MB_OK)
            return
        if self.src["mapfile"] is None:
            quarkx.msgbox("You have not entered a mapfile, nothing done", MT_ERROR, MB_OK)
            return
        pass
        catagory = self.src["catagory"]
        program = self.src["program"]
        words = program.split("\\")
        cmdline = words [-1]
        path_to_program = words [ 0 : -1 ]
        currentdir = "\\".join(path_to_program)
        words = cmdline.split(".")
        name =  words [0]
        name = name.replace(" ", "")
        proglocate = program.replace("\\", "/")

        files = (quarkx.exepath + "plugins\map1AddonsMenuEdit.py")

        if len(files) != 0:
            text = ""

            try:
                f = open(quarkx.exepath + "plugins\map1AddonsMenuEdit.py")
            except (IOError):


# *********** If first time used then it runs this script **********

                CreateMenuItems(self)

                quarkx.msgbox("The menu item has been added and stored\nin the newly created Addons Menu Edit file:\n"+("\r\n" + quarkx.exepath + "plugins\map1AddonsMenuEdit.py")+"\n\nYou need to restart QuArK to undate the menu", MT_INFORMATION, MB_OK)

                return None

# ******** If map1AddonsMenuEdit.py file exists but no items ********

            NbrOfBoxes = 0

            while 1:
                line = f.readline()
                if line == '': # completely empty line means end-of-file
                    break

                words = line.split('\r\n')
                for word in words:

                    if word == "# ------------ Delete This Item ------------\n":
                        NbrOfBoxes = NbrOfBoxes + 1

            if NbrOfBoxes == 0:
                f.close()
                CreateMenuItems(self)

                quarkx.msgbox("The item has been added to the Addons Menu Edit file: "+("\r\n" + quarkx.exepath + "plugins\map1AddonsMenuEdit.py")+"\n\nYou need to restart QuArK to undate the menu", MT_INFORMATION, MB_OK)

                return

# ********** If map1AddonsMenuEdit.py file already exists with items **********

# ********* This part sets parameters and  starts copying the old file data *******

            NewItem = ""
            itemadded = 0
            flag = 0
            if catagory == "1":
                catagory = "ShapesMenu"
            if catagory == "2":
                catagory = "TerrainMenu"
            if catagory == "3":
                catagory = "OtherMenu"
            mapfile = self.src["mapfile"]
            objfile = mapfile.replace("\\", "/")

            f = open(quarkx.exepath + "plugins\map1AddonsMenuEdit.py")

            while 1:
                line = f.readline()
                if line == '': # completely empty line means end-of-file
                    break

                words = line.split('\r\n')
                for word in words:

                    if word == "plugins.map1addonsmenu." + catagory + ".items.append(qmenu.sep)\n":
                        itemadded = 1
                        flag = 1

                    if itemadded == 1:
                        me = 1
                    else:
                        if catagory == "ShapesMenu":
                            if word == "plugins.map1addonsmenu.TerrainMenu.items.append(qmenu.sep)\n":
                                holdword = word
                                NewItem = "ItemAdded"
                                itemadded = 1
                                flag = 1
                                word = "#===========================================\n"
                            else:
                                if word == "plugins.map1addonsmenu.OtherMenu.items.append(qmenu.sep)\n":
                                    holdword = word
                                    NewItem = "ItemAdded"
                                    itemadded = 1
                                    flag = 1
                                    word = "#===========================================\n"
                    if itemadded == 1:
                        me = 1
                    else:
                        if catagory == "TerrainMenu":
                            if word == "plugins.map1addonsmenu.OtherMenu.items.append(qmenu.sep)\n":
                                holdword = word
                                NewItem = "ItemAdded"
                                itemadded = 1
                                flag = 1
                                word = "#===========================================\n"
                        else:
                            if catagory == "OtherMenu":
                                if word == "# End Of File\n":
                                    holdword = word
                                    NewItem = "ItemAdded"
                                    itemadded = 1
                                    flag = 1
                                    word = "#===========================================\n"


                    if flag == 1:
                        if word == "#===========================================\n":

# ********* This part adds the new data then finishes copying the old file data *******

                            text = text + ("plugins.map1addonsmenu."+catagory+".items.append(qmenu.sep)\n\n")

                            text = text + ("# ------------ Delete This Item ------------\n\n")

                            text = text + ("# Menu Catagory: "+catagory+"\n")

                            text = text + ("# Menu Title: Run "+name+"\n\n")

                            text = text + ("def Run_"+name+"(self):\n    pass\n    cmdline = '"+cmdline+"'\n    currentdir = '"+currentdir+"'\n    quarkx.runprogram(cmdline, currentdir)\n\n")

                            text = text + ("plugins.map1addonsmenu."+catagory+".items.append(quarkpy.qmenu.item('Run "+name+"', Run_"+name+",'|This programs location is:\\n\\n"+proglocate+"'))\n\n")

                            text = text + ("# ------------ End Item Cutting ------------\n\n")

                            text = text + ("# ------------ Delete This Item ------------\n\n")

                            text = text + ("# Menu Catagory: "+catagory+"\n")

                            text = text + ("# Menu Title: Import "+name+" map\n\n")

                            text = text + ("def Load_"+name+"_Map(editor):\n    pass\n    editor = mapeditor()\n    info = quarkx.openfileobj('"+objfile+"')\n    mygroup = quarkx.newobj('group:g')\n")

                            text = text + ("    mygroup.copyalldata(info.subitem(0))\n    quarkpy.mapbtns.dropitemsnow(editor, [mygroup], 'draw map')\n\n")

                            text = text + ("plugins.map1addonsmenu."+catagory+".items.append(quarkpy.qmenu.item('Import "+name+" map', Load_"+name+"_Map,'|This maps location is:\\n\\n"+objfile+"'))\n\n")

                            text = text + ("# ------------ End Item Cutting ------------\n\n")

                            flag = 0
                    if NewItem == "ItemAdded":
                        text = text + ("#===========================================\n\n")
                        word = holdword
                        NewItem = ""

                    text = text + word

            f.close()
            file = quarkx.newfileobj(files[0])
            file["Data"] = text
            file.savefile(quarkx.exepath + "plugins\map1AddonsMenuEdit.py")
            del file
            quarkx.msgbox("The item has been added to the Addons Menu Edit file: "+("\r\n" + quarkx.exepath + "plugins\map1AddonsMenuEdit.py")+"\n\nYou need to restart QuArK to undate the menu", MT_INFORMATION, MB_OK)


    editor=mapeditor()
    if editor is None: return
    AddonsDlg(quarkx.clickform,editor,action)

# ****************** END OF ADD TO MENU SECTION ******************


# ****************** Remove Menu Items Function ******************

# ******************* Delete Menu Items Dialog ******************

class DeleteDlg(quarkpy.qmacro.dialogbox):


    def BuildCheckboxesForDialog(self, array):

# creates the menu array data from the map1AddonsMenuEdit.py file

# *************************** start of array ********************

        cat = '0'
        shapes = '0'
        terrain = '0'
        other = '0'
        text = ''
        shapestext = ''
        terraintext = ''
        othertext = ''

        try:
            f = open(quarkx.exepath + "plugins\map1AddonsMenuEdit.py")

        except (IOError):
            quarkx.msgbox("No custom items have been\nadded to the Category menus\n\n    Nothing To Do", MT_INFORMATION, MB_OK)
            return None

        while 1:
            line = f.readline()
            if line == '': # completely empty line means end-of-file
                break
            words = line.split('\n')
            words = line.split(' ')
            for word in words:
                if word == 'Catagory:':
                    catagory = (line[2:+16])
                    if cat == '0':
                        cat = '1'
                        menuname = (line[17:+62])
                        if menuname == 'ShapesMenu\012':
                            if shapes == '0':
                                shapestext = menuname
                                shapes = '1'
                        if menuname == 'TerrainMenu\012':
                            if terrain == '0':
                                terraintext = menuname
                                terrain = '1'
                        if menuname == 'OtherMenu\012':
                            if other == '0':
                                othertext = menuname
                                other = '1'
                    else:
                        menuname = (line[17:+62])
                        if menuname == 'ShapesMenu\012':
                            if shapes == '0':
                                shapestext = menuname
                                shapes = '1'
                        if menuname == 'TerrainMenu\012':
                            if terrain == '0':
                                terraintext = menuname
                                terrain = '1'
                        if menuname == 'OtherMenu\012':
                            if other == '0':
                                othertext = menuname
                                other = '1'

                if word == 'Title:':
                        itemname = (line[14:+62])
                        if menuname == 'ShapesMenu\012':
                            shapestext = shapestext + itemname
                        if menuname == 'TerrainMenu\012':
                            terraintext = terraintext + itemname
                        if menuname == 'OtherMenu\012':
                            othertext = othertext + itemname

        data = shapestext + terraintext + othertext
        f.close()

# ************** MAKE DIALOG *******************

        contentstemplate = """
        Contents:={Txt="<text>" Typ="S" Hint="Check to remove items below"} """

        septemplate = """sep: = { Typ="S" Txt="" }"""

        checkboxtemplate = """
        cb<number>: =
            { Typ="X" Cap="<caption>" Txt="<text>" } """

        dlgdef = """
            {
            Style="9"
            Caption="Delete Checked Items from Menu"
            <checkboxes>
            sep: = { Typ="S" Txt="" }
            close:py = {Txt="" }
            cancel:py = {Txt="" }
            } """

        Contents = ""
        labelArray = ""
        array = data
        checkboxes_string = ""
        num = 0
        words = array.split('\n')

        for item in words:
            if item == '': # completely empty line means end-of-file
                break

            if item == "ShapesMenu":
                labelArray = "Shapes Menu :"
                contents = contentstemplate.replace("<text>", labelArray)
                checkboxes_string = checkboxes_string + contents
            else:

                if item == "TerrainMenu":
                    labelArray = "Terrain Menu :"
                    contents = septemplate + contentstemplate.replace("<text>", labelArray)
                    checkboxes_string = checkboxes_string + contents
                else:

                    if item == "OtherMenu":
                        labelArray = "Other Menu :"
                        contents = septemplate + contentstemplate.replace("<text>", labelArray)
                        checkboxes_string = checkboxes_string + contents

                    else:
                        num = num + 1
                        my_caption = item
                        my_text = ""
                        checkbox_string = checkboxtemplate.replace("<number>", str(num))
                        checkbox_string = checkbox_string.replace("<caption>", my_caption)
                        checkbox_string = checkbox_string.replace("<text>", my_text)
                        checkboxes_string = checkboxes_string + checkbox_string

        new_dlgdef = dlgdef.replace("<checkboxes>", checkboxes_string)

        return new_dlgdef


# ********************** end of dialog definition ***********************

    #
    # dialog layout
    #

    endcolor = AQUA
    size = (220,300)
    dfsep = 0.05
    flags = FWF_KEEPFOCUS

    #
    # __init__ initialize the object
    #

    def __init__( self, form, editor, action):

        self.dlgdef = self.BuildCheckboxesForDialog(self)

    #
    # General initialization of some local values
    #
        self.editor = editor
        src = quarkx.newobj(":")
        self.src = src
        self.action = action
        self.form = form

    #
    # Create the dialog form and the buttons
    #
        quarkpy.qmacro.dialogbox.__init__(self, form, src,
        close = quarkpy.qtoolbar.button(
            self.close,
            "Remove the selected items\nfrom their Menu Catagories",
            ico_editor, 3,
            "Reload"),
        cancel = quarkpy.qtoolbar.button(
            self.cancel,
            "Cancel & close window",
            ico_editor, 0,
            "Cancel"))

    def onclose(self, dlg):
        if self.src is None:
            qmacro.dialogbox.onclose(self, dlg)
            return
        quarkx.globalaccept()
        line = self.BuildCheckboxesForDialog(self)
        self.action(self)
        qmacro.dialogbox.onclose(self, dlg)

    def cancel(self, dlg):
        self.src = None 
        qmacro.dialogbox.close(self, dlg)


#     ********** Delete Dialog Setup Ends Here **********

# *************** Start of Click function ***************

def RemoveItemClick(m):

# ******** If map1AddonsMenuEdit.py file exists but no items ********

    try:
        f = open(quarkx.exepath + "plugins\map1AddonsMenuEdit.py")

        NbrOfBoxes = 0

        while 1:
            line = f.readline()
            if line == '': # completely empty line means end-of-file
                break

            words = line.split('\r\n')
            for word in words:

                if word == "# ------------ Delete This Item ------------\n":
                    NbrOfBoxes = NbrOfBoxes + 1
        if NbrOfBoxes == 0:
            f.close()

            quarkx.msgbox("No custom items exist\nin the Category menus\n\nNothing To Remove", MT_INFORMATION, MB_OK)

            return None
    except (IOError):
        me = 1

# ******** End of check. If there are items now it gos on ********


    def action(self):

# files is the Data output file

        files = (quarkx.exepath + "plugins\map1AddonsMenuEdit.py")

#used just to get the looping to work
# Checkbox layout text

        line = self.BuildCheckboxesForDialog(self)

# To get the number of check boxes there are

        totalboxes = line.count('cb') + 1

# This lets us setup the format needed later
# to see if a check box is checked (returns 1)
# to delete the menu item or unchecked (returns none)
# to include it in the AddonsEditMenu file rewrite

        checkboxtemplate = """cb<number>"""

# Sets our checkbox number to 0
# loops, creates the checkbox number

        loops = 0

# Sets up text file to write to and checkbox format to test

        text = ""
        cbx = checkboxtemplate.replace("<number>", str(loops))
        deleteflag = 0
        deleteLF = 0

# Opens the data file and starts rewrite function
# Data input file

        f = open(quarkx.exepath + "plugins\map1AddonsMenuEdit.py")
        while 1:
            file = f.readline()
            if file == '': # completely empty line means end-of-file
                f.close()
                break
            words = file.split('\r\n')
            for word in words:
                if word == "# ------------ Delete This Item ------------\n":
                    loops = loops + 1
                    cbx = checkboxtemplate.replace("<number>", str(loops))

# If the box is checked, we skip it for the rewrite process

                    if self.src[cbx] == "1":
                        deleteflag = 1

                if deleteflag == 1:
                    if word == "# ------------ End Item Cutting ------------\n":
                        deleteLF = 1

                    if deleteLF == 1:
                        if word == "\n":
                            deleteLF = 0
                            deleteflag = 0
                    else:
                        me = 1

# If it is not checked, we rewrite it to the new menu edit file

                else:
                    text = text + word

        file = quarkx.newfileobj(files[0])
        file["Data"] = text
        file.savefile(quarkx.exepath + "plugins\map1AddonsMenuEdit.py")
        del file


# Reopens file 1st time to test and remove unwanted spacer lines

        text = ""
        flag = 0
        DulLines = ""
        holdLFs = ""
        SpacerWord = ""
        f = open(quarkx.exepath + "plugins\map1AddonsMenuEdit.py")
        while 1:
            file = f.readline()
            if file == '': # completely empty line means end-of-file
                f.close()
                break
            words = file.split('\r\n')

            for word in words:
                if word == "#===========================================\n":
                    if flag == 0:
                        text = text + word + "\n"
                        DulLines = word
                        flag = 1
                        break

                if flag == 1:
                    if word == "\n":
                        break
                    else:
                        holdLFs = ""
                        flag = 3

                if flag == 2:
                    if word == "\n":
                        flag = 3
                        break

                if flag == 3:
                    if word == "# ------------ Delete This Item ------------\n":
                        text = text + SpacerWord + "\n" + word
                        flag = 4
                        break

                    if word == "#===========================================\n":
                        text = text + word
                        holdLFs = ""
                        SpacerWord = ""
                        flag = 2
                        break

                    if word == "# End Of File\n":
                        text = text + word
                        flag = 5
                        break

                    else:
                        SpacerWord = word
                        holdLFs = ""
                        flag = 2
                        break

                if flag == 4:
                    if SpacerWord == word:
                        holdLFs = ""
                        flag = 2
                        break

                    if word == "#===========================================\n":
                        text = text + word + "\n"
                        SpacerWord = ""
                        holdLFs = ""
                        flag = 2
                        break

                    else:
                        text = text + word
                        break

                else:
                    text = text + word

        file = quarkx.newfileobj(files[0])
        file["Data"] = text
        file.savefile(quarkx.exepath + "plugins\map1AddonsMenuEdit.py")
        del file


# Reopens file 2nd time to test and remove unwanted double lines

        files = (quarkx.exepath + "plugins\map1AddonsMenuEdit.py")
        text = ""
        flag = 0
        DulLines = "#===========================================\n"
        f = open(quarkx.exepath + "plugins\map1AddonsMenuEdit.py")
        while 1:
            file = f.readline()
            if file == '': # completely empty line means end-of-file
                f.close()
                break
            words = file.split('\r')

            for word in words:
                if flag == 0:
                    if DulLines == word:
                        flag = 1
                        text = text + word
                        break

                if flag == 1:
                    if "\n" == word:
                        text = text + word
                        flag = 2
                        break
                    else:
                        text = text + word
                        flag = 0
                        break

                if flag == 2:
                    if DulLines == word:
                        flag = 0
                        break
                    else:
                        flag = 0
                        text = text + word
                        break
                else:
                    text = text + word

        file = quarkx.newfileobj(files[0])
        file["Data"] = text
        file.savefile(quarkx.exepath + "plugins\map1AddonsMenuEdit.py")
        del file

# ********* End of Remove Double Lines function *********


        quarkx.msgbox("The checked menu items have been removed\nfrom the recreated Addons Menu Edit file:\n"+("\r\n" + quarkx.exepath + "plugins\map1AddonsMenuEdit.py")+"\n\nYou need to restart QuArK to undate the menu", MT_INFORMATION, MB_OK)

    editor=mapeditor()
    if editor is None: return
    DeleteDlg(quarkx.clickform,editor,action)

# **************** END OF REMOVE FROM MENU SECTION ****************


# ********* This creates the Addons Amend menu items ***************

def ViewAmendMenu(editor):

    grouplist = filter(lambda o: o.type==':g', editor.layout.explorer.sellist)
    onclick = quarkpy.mapbtns.groupview1click

    X0 = quarkpy.qmenu.item("Add menu item", AddItemClick, "|Add menu item:\n\nThis will add a 3rd party program to the menu.\n\nUsing the 'Add Item Dialog' window, select a category to place your menu items under and then find the program you want to add by using the 'select program' file browser '...' button to the right of the input box.\n\nYou can either leave the output/input default file at its current setting and point the programs output to it or use the 'File Browser' button ... to select another map file and location to use.\n\nOnce the program items are added, you will be given a notice as such and to restart QuArk to complete the process of adding the items to your menu.\n\nYou can add as many items to your menu as you like before restarting QuArk.\n\nEach program added will have two items (with the programs name) and a separation line to isolate them for easy recognition, as well as F1 popup windows to remind you where the program and import files are located on your hard drive.\n\nThe first item starts the program. Once you have exported its finished product to the default map file, then use the second item to import the map file into the QuArk editor. The entire product will be added to the map you are currently working on as a separate group item.\n\nAlthough the 'worldspawn' entity will NOT be imported, other entities can be and may require you to delete them, like another 'info_player_start' for example.\n\nBecause these ARE 3rd party programs, QuArK does not provide any documentation on their use and makes no warranty for them.|intro.mapeditor.menu.html#addonsmenu")

    X1 = quarkpy.qmenu.item("Remove menu items", RemoveItemClick, "|Remove menu items:\n\nUse this function to remove the desired custom menu items that have been added.|intro.mapeditor.menu.html#addonsmenu")


    menulist = [X0, X1]
    return menulist


shortcuts = {}

# ************************************************************
# ************************************************************

def ViewAmendMenu1click(m):
    editor = mapeditor(SS_MAP)
    if editor is None: return
    m.items = ViewAmendMenu(editor)


AmendMenuCmds = [quarkpy.qmenu.popup("&Add \ Delete menu items", [], ViewAmendMenu1click, "|Add \ Delete menu items:\n\nThese functions allow you to add and delete 3rd party programs to this menu, that save or export their output to a map file which can then be imported to the QuArK editor and used in the file you are editing.\n\nYou can use any .map file that the program outputs to, at any location, or a default map file as your input file.\n\nThe default import file should be created and saved to YourGame\\tmpQuArk\maps folder and named '1SaveImport.map' .\n\nIf this file is damaged or lost it can be recreated by simply making a basic map file in QuArk (with world_spawn ONLY) and saved with the default file name above.", "intro.mapeditor.menu.html#addonsmenu")]


# ----------- REVISION HISTORY ------------
#
#$Log: map1addonsamendmenu.py,v $
#Revision 1.7  2010/02/21 15:42:49  danielpharos
#Fixed orangebox compiler not finishing compile.
#
#Revision 1.6  2005/10/15 00:49:51  cdunde
#To reinstate headers and history
#
#Revision 1.3  2005/07/21 20:50:09  cdunde
#To correct code error in previous version for removal of string reliance
#
#Revision 1.2  2003/12/18 21:51:46  peter-b
#Removed reliance on external string library from Python scripts (second try ;-)
#
#Revision 1.1  2003/07/04 20:01:16  cdunde
#To add new Addons main menu item and sub-menus
#
