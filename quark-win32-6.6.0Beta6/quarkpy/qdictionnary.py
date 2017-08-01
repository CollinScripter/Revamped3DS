"""   QuArK  -  Quake Army Knife

Dictionary of all strings used within the program
"""
#
# Copyright (C) 1996-99 Armin Rigo
# THIS FILE IS PROTECTED BY THE GNU GENERAL PUBLIC LICENCE
# FOUND IN FILE "COPYING.TXT"
#

# The filename has a typo in it! :|

#$Header: /cvsroot/quark/runtime/quarkpy/qdictionnary.py,v 1.158 2013/06/30 15:18:29 danielpharos Exp $


Strings = {
    0: "QuArK 6.6 Beta 6", #This is also used for version number checks between executable and Python scripts
    1: "  QuArK - Quake Army Knife      %s    by Armin Rigo     -  logo McKay & Brian",

    2: "&New %s",
    3: "&%d. %s",
    4: "   &?   ",
    5: "&Toolboxes",
    6: "Console",
    7: "note: this console may not display the program output before it's terminated",
    44: "&Undo %s",
    45: "&Redo %s",
    # 87: "&Force to grid",
    # 88: "&Force everything to grid",
    98: "Paste face &into polyhedron",
    99: "Paste &into group",
    113: "nothing to undo",

    126: " Selected patch ",
    127: " %d patches sel. ",
    128: " (no bezier patch) ",
    129: " (no face selected) ",
    130: "parent only",
    131: "%d polyhedron(s)",
    132: "Not a valid face",
    133: "(not used)",
    134: " Selected face ",
    135: " %d faces selected ",
    136: "Entities",
    137: "Map structure",
    138: "poly",
    139: "face",
    140: "%d faces",
    141: "%d faces (+%d)",
    142: " Selected polyhedron ",
    143: " %d polyhedrons selected ",
    144: "several groups",
    145: " (no polyhedron selected) ",
    146: "(specific)",
    155: "-- Specifics common to entities in this group --",
    156: "Creating view...",
    # 157: "The map contains %d unused faces. Delete them now ?",
    # 158: "The map contains an unused face. Delete it now ?",
    157: "You left %d faces unused. Delete them now ?",
    158: "You left a face unused. Delete it now ?",
    159: "You made %d invalid polyhedrons. Delete them now ?",
    160: "The resulting polyhedron is no longer valid -- %s\nDelete it now ?",
    161: "You made %d invalid polyhedron(s) plus %d invalid face(s). Delete them now ?",
    163: "-- Specifics common to selected items --",
    172: "Searching for holes...",
    175: "Extracting files...",
#   176: "// This map has been written by QuArK - Quake Army Knife, %s\n// It is a map for the game %s.\n\n// It is recommended that you compile this map using TXQBSP, a version of QBSP\n// that can process floating-point coordinates and enhanced texture positioning.\n// For more information see QuArK's Home Page :  http://quark.sourceforge.net//\n\n",
    ### The entries 176,177,178 are used in [QkMap.PAS] QMapFile.SaveFile()
    176: "This map has been written by QuArK - Quake Army Knife, %s",
    177: "It is a map for the game %s.",
    178: "For more information see QuArK's Home Page: http://quark.sourceforge.net/",
    179: "(%d textures)",
    180: "noname",
    181: "  Map for the game %s",
    182: "  Unknown game",
    183: "corner",
    184: "  Model for the game %s",
    185: "Textures used in this map",
    186: "[any directory]",

    192: "You must enter %d value(s)//Text : %s",
    193: "No matching item found.",
    194: "One matching item found.",
    195: "%d matching item(s) found.",

    216: "Cannot move an item into one of its sub-items",

    221: "No help available about '%s'",
    222: "No selection.",
    223: "Select the polyhedrons, entities, and groups to include in the test build, and try again.\n\nNote that the game will crash if there is no player start in the selection. If the normal player start is not in the selection, you should use a 'testplayerstart' entity (see the New Items window).",
    226: "Thank you for having registered, %s !",
    229: "intersection",
    230: "Duplicators should not be put directly under 'worldspawn', because they duplicate 'worldspawn' itself; the resulting .map file is not valid.",
    236: "Position of the selected vertex",
    237: "Position of the duplicator image",
    238: "Enter the new origin :   (X Y Z)",
    240: "less than 4 sides",
    # 241: "two sides in a same plane",
    242: "no interior",
    243: "sides not closed",
    248: "unexpected char",
    249: "string without end quote",
    250: "a single side with more than %d vertexes",
    251: "invalid real number",
    252: "Only one \042worldspawn\042 is allowed",
    254: "Syntax error in map file, at line %d :\n%s",
    255: "\042worldspawn\042 entity not found in this file",
    256: "QuArK has found %d invalid polyhedron(s) in this file. Look for the \042broken polyhedron\042 icons in the list.",
    257: "QuArK has found %d invalid polyhedron face(s) in this file. Look for the \042broken face\042 icons in the list.",
    # 258: "Polyhedrons with the 'origin' content flag are not allowed in 'worldspawn'. Ignored.",

    260: "Unknown brushdef or patchdef found",
    261: "bezier",
    262: "Map beziers",
    265: "unexpected surface attribute",
    # 266: "Sorry, Doom 3 version 2 maps are not currently supported",
    267: "Unknown map version",
    268: "Sorry, unsupported HL2 map format",

    288: "Help snippet - (press ESC to close window)",
    289: "||Red line : these red lines delimit which portion of the map are to be considered visible on the other view. The objects that are not visible on both map views are considered invisible, and if you see them on one view, they will be grayed out and not selectable with the mouse.\n\nMove these red lines if you need, for example, a quick way to select objects in a room without selecting the ceiling first every time : in this case, scroll the XZ view and/or move its red line until it is below the ceiling, so that the ceiling doesn't come in the way any more.|intro.mapeditor.menu.html#optionsmenu",
    # 290: "This would display help about entity if an entity was selected",

    384: "Impossible to create the file :\n\n%s",
    385: "QuArK failed to open the file :\n\n%s",

    389: "Add a Specific/Arg",
    390: "Delete Specific/Arg",

    400: "Warning...",
    401: "Fatal Error",
    402: "Unknown Error",

    501: "Checking map...",
    502: "Saving compiled model...",
    503: "Reworking model...",
    504: "Conifying...",
    505: "Interrupted !\nCanceling, please wait...",
    507: "Making hollow...",
    508: "Brush subtraction...",
    509: "Map operation...",
    # 511: "Interrupt",
    512: "edit Specific/Arg",
    513: "rotation",
    514: "move",
    515: "move polyhedron",
    516: "resize polyhedron",
    517: "polyhedron distortion",
    518: "set side orientation",
    519: "glue side to plane",
    520: "move entity",
    521: "move selection",
    522: "move group",
    524: "move Duplicator image",
    525: "move vertex",
    526: "change entity angle",
    527: "linear distortion/shear",
    528: "linear rotation/zoom",
    539: "move here",
    540: "insert into group",
    541: "duplicate",
    542: "cut",
    543: "paste",
    544: "new item",
    546: "apply texture",
    547: "apply texture (%d faces)",
    548: "enlarge / shrink",
    549: "inflate / deflate",
    550: "rotation",
    551: "symmetry",
    552: "move (from tool palette)",
    553: "delete Specific",
    556: "create new group",
    558: "move with arrow key",
    559: "force angle to grid",
    560: "force to grid",
    563: "cut out corner",
    564: "intersect polyhedrons",
    565: "make hollow",
    566: "rename object",
    568: "drag new item",
    579: "delete selection",
    582: "delete item '%s'",
    586: "lines through hole",
    590: "set group view flags",
    592: "duplicate item",
    593: "save in Explorer",
    594: "drop file(s)",
    595: "change palette",
    596: "set texture flags",
    597: "move face or texture",
    598: "move texture on face",
    599: "(cannot undo)",
    600: "paste into group",
    601: "paste and cut in two",
    602: "delete unused faces and polys",
    603: "click on form button",
    604: "make file links",
    605: "import files",
    606: "toolbox main folder",
    607: "toolbox folder",
    608: "edit description",
    609: "edit object Spec/Arg",
    610: "delete Specific",
    611: "negative polyhedron",
    612: "external editor",
    613: "set texture link",
    614: "update BSP",
    615: "set file name",
    616: "drop new item",
    617: "texture distortion",
    618: "texture rotation",
    619: "adjust tex. to face",
    620: "reset tex. scale",
    621: "negative poly",
    622: "set group color",
    623: "new texture links",
    624: "auto. delete unused faces and polys",
    625: "resize texture",
    626: "image resize or conversion",
    627: "bezier reshape",
    628: "move bezier texture",

    720: "Press a key or select one in the list :",
    721: "Key mapping for special actions",
    722: "Key",
    723: "Associated action",
    725: "&Key...",

    768: "Known types (%s)|%s",
    769: "Structured text for hand-editing (*.%0:s)|*.%0:s",
    770: "Save file as... (enter name and select type)",
    771: "Choose the file(s) to open",
    772: "QuArK Explorer file (*.qrk)|*.qrk",
    773: "QuakeC code (*.qc)|*.qc",
    774: "All files (*.*)|*.*",
    775: "QuArK Map (*.qkm)|*.qkm",
    776: "Texture Wads (*.wad)|*.wad",
    777: "Quake 2 textures (*.wal)|*.wal",
    778: "Pak files (*.pak)|*.pak",
    779: "Compiled BSP (*.bsp)|*.bsp",
    780: "HexenC code (*.hc)|*.hc",
    781: "PCX image (*.pcx)|*.pcx",
    782: "Bitmap image (*.bmp)|*.bmp",
    783: "Old QuArK format (*.qme)|*.qme",
    784: "Quake .map file (*.map)|*.map",
    785: "QuArK Model (*.qkl)|*.qkl",
    786: "Classic Quake .mdl file (*.mdl)|*.mdl",
    787: "Quake 2 .md2 file (*.md2)|*.md2",
    788: ".wav Sound (*.wav)|*.wav",
    789: "Quake 2 Video (*.cin)|*.cin",
    790: "Text file (*.txt)|*.txt",
    791: "Config. file (*.cfg)|*.cfg",
    792: "Heretic II textures (*.m8)|*.m8",
    793: "Sin textures (*.swl)|*.swl",
    794: "Sin Pak files (*.sin)|*.sin",
    795: "Heretic II models (*.fm)|*.fm",
    796: "TGA image (*.tga)|*.tga",
    797: "ZIP archives (*.zip)|*.zip",
    798: "Quake 3 Pak Files (*.pk3)|*.pk3",
    799: "Quake 1 / Half-Life Sprite Files (*.spr)|*.spr",
    800: "Quake 2 Sprite Files (*.sp2)|*.sp2",
    801: "JPEG Image (*.jpg)|*.jpg",
    802: "C Files (*.c)|*.c",
    803: "C Header Files (*.h)|*.h",
    804: "Quake 3 Shaders (*.shader)|*.shader",
    805: "Quake 3 .md3 file (*.md3)|*.md3",
    806: "SoF Texture (*.m32)|*.m32",
    807: "3d studio file (*.3ds)|*.3ds",
    808: "Hmf (6DX) map file (*.hmf)|*.hmf",
    809: "Sylphis Pak files (*.col)|*.col",
    810: "PNG image (*.png)|*.png",
    811: "Tribes 2 VL2 Files (*.vl2)|*.vl2",
    812: "Tribes 2 CS-script Files (*.cs)|*.cs",
    813: "Doom 3 Pak Files (*.pk4)|*.pk4",
    814: "Valve Texture File (*.vtf)|*.vtf",
    815: "Valve Material File (*.vmt)|*.vmt",
    816: "Steam Game Cache File (*.gcf)|*.gcf",
    817: "Valve Map File (*.vmf)|*.vmf",
    818: "Steam FS (*.SteamFS)|*.SteamFS",
    819: "DDS image (*.dds)|*.dds",
    820: "FTX image (*.ftx)|*.ftx",
    821: "Call of Duty 2 Pak Files (*.iwd)|*.iwd",
    822: "Sylphis Map File (*.cmap)|*.cmap",
    823: "Doom 3 Material File (*.mtr)|*.mtr",
    824: "Call of Duty 2 Image Files (*.iwi)|*.iwi",
    825: "Valve Pak File (*.vpk)|*.vpk",
    826: "Steam No Cache File (*.ncf)|*.ncf",
    827: "WorldCraft Rich Map Format file (*.rmf)|*.rmf",
    828: "Call of Duty 2 Bsp Files (*.d3dbsp)|*.d3dbsp",

    2368: "Skins",
    2369: "Frames",
    2370: "Main component",
    2371: "Model",
    2372: "skin%d",
    2373: "Frame group",
    2374: "Skin group",

    2432: "This model contains no data to save",
    2433: "Internal error : Invalid packed model structure//Please report : %s",
    2434: "The current structure of this model is invalid. It cannot be saved in %s format.",
    2435: "The model contains no skin and the skin size is unspecified",
    2448: "Writing model's bones index data",
    2449: "Writing component weights index data",
    2450: "Writing component vertex index data",
    2451: "Writing component u,v texture data",
    2452: "Writing component frame vertices data",
    2453: "Writing component triangle index data",
    2454: "Preparation data read...Importing model",
    2455: "Preparation data read...Exporting model",
    2456: "Importing model's bones index data",
    2457: "Importing component weights index data",
    2458: "Importing component vertex index data",
    2459: "Importing component u,v texture data",
    2460: "Importing component frame vertices data",
    2461: "Importing component triangle index data",
    2462: "Importing model animation",

    2549: "shift left / right",

    2600: "No valid image found",
    2601: "No image data found",
    2602: "No palette data found",
    2603: "No alpha data found",
    2604: "Invalid U,V coordinates",
    2605: "Invalid color value",
    2606: "Invalid palette index value",
    2607: "Invalid alpha coordinate",
    2608: "Invalid alpha value",
    2609: "Image is not a paletted picture",

    3001: "Esc",
    3002: "1",
    3003: "2",
    3004: "3",
    3005: "4",
    3006: "5",
    3007: "6",
    3008: "7",
    3009: "8",
    3010: "9",
    3011: "0",
    3012: "-",
    3013: "=",
    3014: "BackSpace",
    3015: "Tab",
    3016: "q",
    3017: "w",
    3018: "e",
    3019: "r",
    3020: "t",
    3021: "y",
    3022: "u",
    3023: "i",
    3024: "o",
    3025: "p",
    3026: "[",
    3027: "]",
    3028: "Enter",
    3029: "Ctrl",
    3030: "a",
    3031: "s",
    3032: "d",
    3033: "f",
    3034: "g",
    3035: "h",
    3036: "j",
    3037: "k",
    3038: "l",
    3039: ";",
    3040: "'",
    3041: "~",
    3042: "Shift",
    3043: "\\",
    3044: "z",
    3045: "x",
    3046: "c",
    3047: "v",
    3048: "b",
    3049: "n",
    3050: "m",
    3051: ",",
    3052: ".",
    3053: "/",
    3054: "Shift",
    3055: "*",
    3056: "Alt",
    3057: "Space",
    3058: "CapsLock",
    3059: "F1",
    3060: "F2",
    3061: "F3",
    3062: "F4",
    3063: "F5",
    3064: "F6",
    3065: "F7",
    3066: "F8",
    3067: "F9",
    3068: "F10",
    3069: "NumLock",
    3070: "ScrollLock",
    3071: "Home",
    3072: "UpArrow",
    3073: "PgUp",
    3074: "-",
    3075: "LeftArrow",
    3076: "5",
    3077: "RightArrow",
    3078: "+",
    3079: "End",
    3080: "DownArrow",
    3081: "PgDn",
    3082: "Ins",
    3083: "Del",
    3086: "\\",
    3087: "F11",
    3088: "F12",
    3256: "Tab",
    3257: "Pause",
    3258: "F10",
    3259: "Alt",
    3260: "Mouse1",
    3261: "Mouse2",
    3262: "Mouse3",
    3263: "Joy1",
    3264: "Joy2",
    3265: "Joy3",
    3266: "Joy4",

    4095: "Invalid version number in Quake's original Progs.dat",
    4096: "Real number expected",
    4097: "Unexpected symbol.    Expected : %s    Found : %s",
    4098: "\253 ' \273 expected",
    4099: "Unexpected end of line",
    4100: "Unexpected char",
    4101: "Wrong operand types (if it's a function that returns a vector, you must directly assign it to a vector variable)",
    4102: "Error in expression",
    4103: "\253 . \273 must follow an expression of type Entity",
    4104: "Cannot assign a value to an expression",
    4105: "Identifier already defined",
    4107: "Original function had not the same number of arguments",
    4108: "Original function had other arguments",
    4109: "Cannot initialize these type of variable",
    4110: "Declaration expected",
    4111: "\042void()\042 function expected",
    4112: "Too much code! Overflow is due to the structure of Progs.dat",
    4113: "frame name expected",
    4114: "Unknown identifier ('%s')",
    4115: "Wrong argument count in function call",
    4116: "Wrong argument type in function call",
    4117: "Too many arguments (maximum is 8)",
    4159: "Compile error :  %s  in entry '%s', at line %d//The error was found in this part of the code, within the last two lines :\n%s",
    4160: "unknown symbol",
    4161: "data type",
    4162: "identifier",
    4163: "variable",
    4164: "object variable",
    4165: "':'",
    4166: "';'",
    4167: "'.'",
    4168: "'='",
    4169: "','",
    4170: "'+'",
    4171: "'-'",
    4172: "'*'",
    4173: "'/'",
    4174: "'&'",
    4175: "'|'",
    4176: "'!'",
    4177: "'||'",
    4178: "'&&'",
    4179: "'=='",
    4180: "'!='",
    4181: "'<'",
    4182: "'>'",
    4183: "'<='",
    4184: "'>='",
    4185: "'{'",
    4186: "'}'",
    4187: "'('",
    4188: "')'",
    4189: "'LOCAL'",
    4190: "'BIND'",
    4191: "'AUTOEXEC'",
    4192: "'IF'",
    4193: "'ELSE'",
    4194: "'WHILE'",
    4195: "'DO'",
    4196: "'RETURN'",
    4197: "real number",
    4198: "string constant",
    4199: "vector",
    4200: "end of file",
    4201: "'$'",
    4202: "'['",
    4203: "']'",
    4204: " or ",

    4416: "Cannot set this attribute to screen panel objects",
    4417: "QuArK file object expected",
    4418: "Cannot load bitmap file '%s'",
    4419: "Invalid dock position",
    4420: "Subitem index out of bounds",
    4421: "QuArK object expected",
    4422: "Object cannot have multiple parents",
    4423: "Insertitem index out of bounds",
    4424: "Removeitem index out of bounds",
    4425: "No such item to remove",
    4426: "Unexpected end of data",
    4427: "Cannot write into this file",
    4428: "Write error (disk may be full)",
    4429: "Unknown attribute",
    4430: "Internal icon index out of bounds",
    4431: "Image1 object expected",
    4432: "QuArK File object attribute not found",
    4433: "Internal error",
    4434: "Callable object expected",
    4435: "Loading error",
    4436: "Saving error",
    4437: "Invalid operation on the main panel",
    4438: "expected a QuArK object of type '%s'",
    4439: "expected a tuple (object to display, object with default values)",
    4440: "expected a tuple of floats",
    4441: "expected a 3D vector",
    4442: "The module 'quarkx.action' is closed",
    4443: "Invalid vector operation",
    4444: "Invalid matrix operation",
    4445: "ImageList index out of range",
    4446: "Not a face of the given polyhedron",
    4447: "Points must all be projected",
    4448: "Operation not allowed on 3D perspective views",
    4449: "Duplicator macro did not create a list of TreeMap objects",
    4450: "Expected a list of Internal objects of class '%s'",
    4451: "ProgressBar already closed",
    4452: "Operation aborted",
    4453: "Cannot execute this program",
    4454: "Expected a file object or equivalent",
    4455: "No such file or file still opened",
    4456: "Copy text to clipboard ?",
    4457: "Are you sure you want to delete this item(s) ?",
    4458: "Invalid arguments to 'extendcoplanar'",
    4459: "positive integer expected",
    4460: "Cannot find '%s', using '%s' instead",
    4461: "Unknown value '%s' for setting '%s'",
    4462: "expected a 3D matrix",

    4614: "&More >>",
    4616: "                     *** EXCEPTION REPORT ***\n\n%s       Address in the program : %p (%p)\n",
    4617: "\n\nPlease report this error to the QuArK development team, so that they can fix the issue promptly.",
    4618: "//Description of the invalid polygon :",
    4620: "Impossible to create the surface for a polygon//Three aligned points don't define a plane.",
    4621: "Cannot set this as a background image: This is not a valid image file, or an unsupported format.",
    4622: "QuArK could not switch to '%s' game mode : this game support is currently not installed",
    4623: "QuArK could not switch to '%s' game mode : this game cannot be switched to",
    4624: "No installed game supports found. QuArK cannot start.",
    4625: "Restoring default setting will overwrite all changes made. Are you sure?",

    5119: "(new)",
    5120: "Explorer Group",
    5121: "Imported File",
    5122: "(clipboard)",
    5123: "QuArK %s editor",
    5124: "QuakeC Code",
    5125: "file",
    5126: "Map",
    5127: "ToolBox",
    5128: "New %s",
    5129: "Texture Wad",
    5130: "Texture Link",
    5131: "Quake 1 texture",
    5132: "Quake 2 texture",
    5133: "Pak file",
    5134: "BSP",
    5135: "Texture List",
    5136: "Pak folder",
    5137: "PCX image",
    5138: "Bitmap image",
    5139: "HexenC code",
    5140: "ToolBox folder",
    5141: "Qme (old QuArK format)",
    5142: ".map file",
    5143: "Model",
    5144: ".mdl file",
    5145: ".md2 file",
    5146: "Doom 3 Pak",
    5147: "Call of Duty 2 Pak",
    5148: "Sylphis Pak",
    5149: "Sylphis Map file",
    5150: "WorldCraft Rich Map Format file",
    5151: "Call of Duty 2 Bsp file",

    5155: "Quake Context",
    5156: "Tool bar",
    5157: ".wav Sound",
    5158: "Video",
    5159: "QuArK Macro",
    5160: "Text file",
    5161: "Config file",
    5162: "Files for the game",
    5163: "M8 texture (Heretic II)",
    5164: "Half-Life texture",
    5165: "Sin texture",
    5166: "Sin Pak file",
    5167: ".fm file (Heretic II)",
    5168: "TGA image",
    # Zip File Support
    5169: "Zip Archive",
    5170: "Quake 3 Pak",
    5171: "Sprite file",
    5172: "JPEG image",
    5173: "C File",
    5174: "C Header File",
    5175: "Shader list (Quake 3)",
    5176: ".md3 file",
    5177: "M32 texture (SoF)",
    5178: "3d studio file",
    5179: "Form Context",
    5180: ".hmf (6DX) file",
    5181: "PNG image",
    5182: "Tribes 2 VL2 file",
    5183: "Tribes 2 CS-script file",
    5184: "'%s' is not a QuArK-5 file",
    5185: "'%s' was created with a more recent version of QuArK",
    5186: "'%s' is invalid (the end of the file seems to be missing)",
    5187: "The file extension of '%s' does not match the file contents, which seems to be of type '%s'",
    5188: "The file '%s' does not exist",
    5189: "Cannot write into file '%s', because it is currently opened in another window. Save your work in another file",
    5190: "File corruption in '%s'. You can try to continue to load it, but Warning ! This will likely cause serious troubles like mess in the object trees !\n\nThis error message may be displayed several times per file.\n\nReally continue ?",
    # 5191: "Cannot read file objects of type '%s' with format %d",
    5192: "DDS image",
    5193: "Syntax error in source file %s, line %d : %s",
    5194: "'{' expected",
    5195: "unexpected data after the final '}' has been ignored.",
    5196: "invalid property definition",
    5197: "'=' expected",
    5198: "unexpected end of line, unbalanced quotes",
    5199: "hexadecimal code expected",
    5200: "// This file has been written by QuArK %s\n// It's the text version of file: %s\n",
    5201: "Could not open '%s' : Unknown file extension",
    5202: "'%s' cannot be opened in a new window",
    5203: "File not found : %s//Current directory is %s",
    5204: "Cannot load the configuration file (Defaults.qrk). Be sure QuArK is correctly installed. You may need to reinstall it.\n\n%s",
    5205: "Invalid configuration file (Defaults.qrk). Please reinstall QuArK.  (Missing SetupSet '%s')",
    5206: "Wrong version of configuration file (Defaults.qrk). Please reinstall QuArK.  (QuArK is '%s' and Defaults.qrk is '%s')",
    # 5207: "Error loading file '%s'.//Object initialization failed",
    5207: "Polyhedron has no width.",
    5208: "Only %d valid faces are left.",
    5209: "integer or floating-point value expected - '%s' is not a floating-point value",
    5210: "You are changing the name of the file. This will make a new file; the file with the old name will not be deleted.",
    5211: "Save changes to this file ?",
    5212: "Save changes to '%s' ?",
    5213: "\n\n(Memory undo buffer too small, reduced to %d)",
    5214: "You will no longer be able to undo any of the previous operations if you go on.",
    5215: "You will no longer be able to undo all of the previous operations if you go on.",
    5216: "QuArK has left %d temporary file(s) in path %s, probably because it crashed or because of a bug. Do you want to delete this(these) file(s) now ?",
    5217: "'%s' : Cannot (un)do this operation any more because the file has been closed",
    # 5218: "Warning: the tree view you see is incomplete, because the Explorer views of QuArK cannot display the same objects more than once.",
    5219: "The file %s's \"save\" support has not (yet) been added. File ignored.",
    5220: "'%s' : Invalid file size. The file is %d bytes length instead of %d",
    5221: "Cannot display '%s' in the tree view, because it is already visible in another Explorer views in QuArK.",
    5222: "This file contains a link to the file '%s' which cannot be found. The link has been ignored (and deleted).",
    5223: "Internal error (%s) - this program is buggy !//Please report: %0:s",
    # 5224: "Cannot open file '%s' because it is already opened as file link",
    5225: "This file contains a link to the file '%s' which is already opened elsewhere. The link has been ignored (and deleted).",
    5226: "FTX image",
    5227: "Cannot save image as FTX file: it has a palette, which is not supported by FTX files. Please convert before saving.",
    5228: "Unable to open link: Cannot find file: '%s'",
    5229: "integer or floating-point value expected - '%s' is not an integer value",
    5230: "Custom Add-on",
    5231: "IWI image",

    5248: "Cancel",
    5249: "&Move here",
    5250: "&Copy here",
    5251: "&Move selected items here",
    5252: "&Copy selected items here",
    5253: "&Insert into this group",
    5254: "C&opy into this group",
    5255: "&Insert selected items into this group",
    5256: "C&opy selected items into this group",
    5257: "Name your new Add-on",
    5258: "Toolbox Folders",
    5259: "New Folder",

    5376: "Configuration",
    # 5376: "The minimal value is %s",
    # 5377: "The maximal value is %s",
    5377: "Cancel",
    5378: "Close",
    5379: "View %0:s%2:s (%1:s %3:s)",
    5380: "Angle Side view",
    5381: "Specific",
    5382: "Arg",
    5383: "&Add a Specific\n&Delete Specific\nCop&y\n&Paste\n&Cut",
    5384: "Palette",
    5385: "%s palette",
    # 5386: "You cannot change this palette directly here. Do you want to open the file that contains the %s ?",
    5386: "You cannot change this palette directly here",
    5387: "%s texture - %d x %d",
    5388: "Texture Flags",
    5389: "Groups",
    5390: "Flags",
    5391: "\267 differs \267",
    5392: "%d bytes",
    5393: "  Paste",
    5394: "This stores your settings",
    5395: "view of textures is disabled - click here to enable",
    5396: "Paste special...",
    5397: "(full-screen)",
    5398: "Elapsed time: %d second",
    5399: "Elapsed time: %d seconds",
    5400: "Byte count: %d bytes (%d KB)",
    5401: " Group: %s",
    5402: "This group contains %d KB of data in %d hidden objects (impossible to edit them directly).",
    5403: "Browse for directory",
    5404: "Browse for texture",
    5405: "Browse for file",
    5406: "Hull *%d",
    5407: "%d objects",
    5408: "Press on shaded areas, or use keypad arrows",

    5440: "Loading ToolBox...",
    5441: "ToolBox",
    5442: "Copying data...",
    5443: "Writing as text...",
    5444: "Loading ToolBoxes data...",
    5445: "Loading configuration files...",
    5446: "Loading tree view...",
    5447: "Reading as text...",
    5448: "Reading image...",
    5449: "Writing image...",
    5450: "Saving...",
    5451: "Loading .map file...",
    5452: "Opening...",
    5453: "Preparing textures...",
    5454: "Loading textures for 3D view...",
    5455: "Fast forward...",
    5456: "Building .pak file...",
    5457: "Pasting...",
    5458: "Searching add-ons...",
    5459: "preparing Faces...",
    5460: "preparing Models...",
    5461: "Loading from pak file...",
    5462: "Searching online for updates...",

    5502: "Sprite object not found!",
    5503: "'%s' is a Half-Life Model which cannot be read (yet)",
    5504: "No texture image//Missing or invalid %s",
    5505: "'%s' is not a WAD file//%d should be %d or %d",
    5506: "'%s' is not a PACK file//%d should be %d",

    5508: "Files names in PACK files are limited to %d characters, including the path. '%s' is too long",
    5509: "Invalid data. The file is probably corrupted//Error %d",

    5511: "The WAD file contains data that cannot be written to this type of file.//'%s' invalid",

    5514: "'%s' : structure invalid for a Quake %d-like texture",
    5515: "FILE ERROR !!\n\nThe file has been correctly saved to :\n\n%s\n\nbut QuArK cannot reopen it. You can't continue editing the file.\n\nQuit QuArK now, find this temporary file and rename it '%s'",
    5516: "Could not save the file '%s'. The file is maybe read-only or opened in another application.//The file has been correctly saved to :\n\n%s\n\nbut QuArK failed to move it to the correct location. You can look for this temporary file and rename it '%s' yourself",
    5517: "Could not save the file. The disk is maybe full or read-only.//%s",
    5518: "Invalid texture link - no link !",
    5519: "No data - the file is empty",
    5520: "'%s' is not a Quake 1, Hexen II nor Quake 2 BSP file//%d should be %d or %d",
    5521: "Missing BSP data. You can't use or save an empty or incomplete .bsp file",
    5522: "(Missing)",
    5523: "(Empty data)",
    5524: "Texture '%s' not found in %s",
    5525: "Unable to save entity, invalid type",
    5526: "Could not add this file to the QuArK Explorer",
    5527: "This file is opened in several windows. You must close them before you can do this operation",
    # 5528: "You cannot make changes here because QuArK could not find in which file this data is stored",
    # 5529: "Do you want to save the changes you made ? They will be stored in the following file(s) :\n",
    # 5530: "\n   %s",
    5528: "Are you sure you want to make changes here ? QuArK could not find in which file this data is stored.",
    5529: "This data comes from the file '%s'.\n\nIt is possible to make changes there. QuArK will let you save or discard these changes later.",
    5530: "Cannot make changes here, because QuArK could not find from which file this data comes",
    5531: "Cannot save '%s' because it has been attached to something else. You should save changes you make before you do other complex operations on the objects",
    5532: "'%s' is not a 256-colors PCX file//%d-%d should be %d-%d",
    5533: "'%s' is a PCX file but contains no palette. QuArK cannot open such files",
    5534: "No image data//Missing or invalid %s",
    5535: "'%s' is not a Bitmap file//%d should be %d",
    5536: "'%s' is not a 256-colors bitmap. Do you want to convert it to the %s palette ?",
    # 5537: "Failed to load the bitmap image. This may come from incompatible video drivers//Error code %d\nInternals %d %d %d\nSize %dx%d %dx%d",
    # 5537: "Not a supported bitmap format",
    5538: "Failed to convert the object to the required file type",
    5539: "The width and the height of textures must be multiples of 8. This image's size is %d by %d pixels. The image will be expanded up to %d by %d.",
    # 5540: "The image is too large to be converted. Its size is %d by %d. It will be reduced down to %d by %d pixels.",
    5541: "The image's palette is different from the %s palette. The colors will have to be converted.",
    5542: "QuArK tried to switch to a game that's not installed.//Mode %s",
    5543: "QuArK must switch to %s game mode.",
    5544: "You are converting this texture between different games. Because of the palette, the colors might slightly change. Do you want to map the colors to the palette of the new game ?",
    5545: "You cannot drop files of this type here.",
    5546: "Do you want to put a link to the file here ? If you answer No, the file will be copied. If you want to simply open this file instead, don't drag it to the Explorer panel.",
    5547: "QuArK could not switch to '%s' game mode : this game seems unsupported in this version",
    5548: "QuArK could not determine the game for which this file is made. The current game mode is '%s'.",
    5549: "The information required to work with %s could not be loaded. Be sure that the supporting files for this game are installed. The missing file is '%s'; if you do not have it, you need to download it from the web site.",
    5550: "The following file(s) have been indirectly modified. Save the changes ?\n",
    5551: "\n   %s",
    5552: "(error: no filename found)",
    5553: " However, it is recommended that you make a QuArK add-on instead of modifying this file.\n\nTo make a new Add-on, choose New Main Folder in the Folders menu.",
    5554: "Sorry, this version of QuArK cannot save files in the old .qme format. Use 'Save object as file' or 'Copy object as'",
    5555: "'%s' is not a QME file//%d should be %d",
    5556: "'%s' contains unsupported version numbers. It might have been done with an old version of QuArK (2.x). This version of QuArK cannot read these files.//Version code : %d\nType code : %d",
    5557: "QuArK did not find the registered add-on '%s'.",
    5558: "This map is invalid and contains no data.",
    5559: "QuArK needs the file '%1:s' from %0:s and could not find it on your disk. Please insert the CD-ROM now.",
    5560: "QuArK needs the file '%1:s' from %0:s and could not find it. You must set up the correct path(s) to %0:s in the Configuration dialog box",
    5561: "QuArK needs the file '%1:s' from %0:s (directory '%2:s') and could not find it. You must set up the correct path(s) to %0:s in the Configuration dialog box",
    # 5562: "The clipboard contains %d objects. Do you want to open them all ?",
    5563: "You must enter a Specific",
    5564: "A Specific cannot begin with the symbol '%s'",
    5565: "A Specific cannot contain the symbol '%s'",
    5566: "This map contains unsupported objects. It might have been created with a more recent version of QuArK.\n\n%d object(s) of unknown type deleted",
    5567: "Cannot undo this operation, sorry",
    5568: "Could not build the tool bar '%s'.",
    5569: "The filename-data in this file ('%s') does not match the actual file name ('%s').",
    5570: "(switch back to %s game mode)",
    5571: "'%s' is not a Quake 2 MD2 file//%d-%d should be %d-%d",
    5572: "'%s' looks like a Quake-2 (or one of its game descendants) BSP file,\nbut its BSP-version is not recognized and therefore not supported.//%d should be %d",
    5573: "QuArK does not know if '%s' is a Quake 1 or Hexen II file. Is it an Hexen II map ?",
    5574: "Missing information : QuArK cannot determine the target game for this file//Specific 'Game' missing",
    # 5575: "The skin path in this Model is ambiguous : several .pcx files with the same name exist in various paths. QuArK may have chosen a wrong one.",
    5575: "Missing skin image file '%s' in model '%s'",
    5576: "This Model is invalid and contains no data.",
    5577: "Macro processing error in '%s' : %s",
    5578: "unbalanced '['",
    5579: "invalid character after '['",
    5580: "unbalanced '<'",
    5581: "'>' must be followed by ']'",
    5582: "'%s' is not an add-on for the game %s but for %s. You must switch to the correct game mode before you can use it.",
    5583: "Cannot open the palette to choose a color from",
    5584: "(missing caption)",
    5585: "Could not execute this program//Command line: '%s'\nDefault directory: '%s'",
    5586: "QuArK could not execute this or these programs. You must be sure they are installed on your system, and then enter the path to them in the configuration dialog box. Do you want to enter the path now ?",
    5587: "Impossible to create the directory '%s'. Be sure you entered the path to %s correctly in the configuration dialog box//Error code %d",
    5588: "Texture '%s' not found.",
    5589: "%d textures written to '%s'.",
    5590: "%d textures and shader or script files written to '%s'. Of this %d were animated textures and/or shaders or scripts.",
    5591: "Choose the file(s) to link to",
    5592: "Choose the file(s) to import",
    5593: "'%s' is not a Quake1 MDL file//%d-%d should be %d-%d",
    5594: "Skin '%s' has no image",
    5595: "Failed to convert this map into a .map file",
    5596: "The Add-ons should be put in the same directory as QuArK itself",
    5597: "You are deleting the main toolbox folder '%s' and its container '%s'.\n\nAre you sure ? (this operation can of course be undone)",
    5598: "Enter the description of this item :",
    5599: "QuArK must switch to %s game mode, but it cannot do so now because you are working in a ToolBox. You need to copy this data outside the toolbox before you can work on it. When copying textures, copy them using the standard 'Copy' command and then use 'Paste as...' to convert it to another game.",
    5600: "This file is already registered as an Add-on",
    5601: "Save this file in the QuArK Explorer ?\n\nFor organization purposes, this option lets you pack your files into a single .qrk file. If you answer No, QuArK will let you save your file normally.",
    5602: "'%s' is a BSP file (version %d) that\n cannot (yet) be loaded by QuArK.",
    5603: "Cannot access the WAVE sound output. There is probably another sound currently played//waveOutOpen failed",
    5604: "Cannot access the WAVE sound output. Internal error//waveOutPrepareHeader failed",
    5605: "'%s' is not a WAV file//%d should be %d",
    5606: "Wave output timed out",
    5607: "'%s' is probably not a CIN file//Invalid frame size (%d by %d) or sound format (%d-%d-%d)",
    5608: "Error while reading the CIN file. The end of the file is probably missing",
    5609: "Time out",
    5610: "Invalid path. You must select or type the path to the file '%s'",
    5611: "Cannot save an empty file",
    5612: "About QuArK - Quake Army Knife",
    5613: "Impossible to delete the Registry association for '.%s'.",
    # 5614: "QuArK will associate itself with the following file types :\n\n%s\nThe files with these extensions will be given a custom icon and double-clicking on them will open them with QuArK. Do you want to continue ? If No, you might want to select exactly the file types you want in the Configuration dialog box.",
    # 5615: "\t.%s\t(%s)\n",
    5616: "Impossible to create the Registry association for '.%s'.",
    5617: "This program failed to build the following file(s) :\n\n%s\nPlease see its documentation to learn more about this program. You may also want to look at the program's log file (if any) or run the program again from an MS-DOS box if you didn't have the time to read its screen output.",
    5618: "\t%s\n",
    # 5619: "The texture '%s' is not for Quake 2",
    5619: "Texture file format could not be converted : %s",
    5620: "Your map is 'leaked', i.e. there is a hole. To help you find it, QuArK can display a list of points going through the hole. Ok ?",
    5621: "The map is not opened. Cannot load .lin file",
    5622: "Cannot use macro 'O' (Operation) without an object to operate on",
    5623: "Duplicator behaviour '%s' not found",
    5624: "This map contains a special Duplicator whose behaviour is unknown to QuArK 5//'Sym' is '%s'",
    5625: "%s cannot run multiple TCs together :\n%s\nOnly the last one is used.",
    5626: "the temporary directory '%s'",
    5627: "The directory to %s seems to be wrong : could not find %s. Do you want to enter the correct path now ?",
    5628: "Remove the temporary tag of file '%s' ? QuArK will then no more consider it a temporary file.",
    5629: "Always create pak files instead of writing files in '%s'",
    5630: "Cannot create a new temporary pak file. The names are in use up to '%s'",
    5631: "There is an error in the definition of this button//Form '%s' not found",
    5632: "The WAVE file has bad formatted data at the end that will be ignored.",
    5633: "This object has been moved or deleted",
    5634: "Error in hull number %d : %s",
    5635: "The BSP file structure seems to be invalid.\nError code %d",
    5636: "Update the BSP file ?\n\nNote that no group information nor any polyhedron added in this map can be saved. You can only change entities and textures in BSPs.",
    5637: "This BSP or parts of it are still opened. Cannot open the map display again",
    5638: "The hull number %d contains %d invalid face(s).\n%s",
    5639: "No texture number %d",
    5640: "Cannot edit BSP faces (yet).",
    5641: "The BSP structure seems a bit strange. Be sure the file didn't get truncated.",
    5642: "Save changes in the configuration ?",
    5643: "Load-time include command '%s' : not found",
    5644: "Unknown file extension '%s'",
    5645: "Press the key you want for this action...",
    5646: "%s\n\nAre you sure you want to INTERRUPT this process ?",
    5647: "You are about to remove all association to QuArK from your Windows Registry. Note that the next time you run QuArK, it will automatically associate itself with .qrk files again.\n\nDo you want to continue ?",
    5648: "Done ! To explicitly remove file associations, use the button\n'remove all associations' below.",
    5649: "This documentation is in HTML format, but QuArK failed to open your web browser.\n\nTried to open : %s//Error: %s",
    5650: "No .html or .htm key in Registry",
    5651: "No key \"%s\" in Registry",
    5652: "Cannot execute command : %s",
    5653: "Operation terminated.",
    5654: "To compile the QuakeC or HexenC code in this file, you must first switch to the appropriate game mode",
    5655: "'%s' is not a M8 texture file//%d should be %d",
    5656: "This directory is not valid.\n\nYour path: %s\nRequired path: %s",
    5657: "Cannot save the setup file",
    5658: "QuArK could not save your configuration :\n\n %s",
    5659: "QuArK cannot save any file because your system's temporary directory is invalid.",
    5660: "No texture found in '%s'",
    5661: "The Heretic II texture sizes stored in '%s' seem invalid//%d x %d  should be  %d x %d",
    5662: "Select the directory where you want to extract the files to :",
    5663: "%d file(s) have been extracted to the directory '%s'.",
    5664: "Cannot save skin groups in this file format.",
    5665: "Cannot save frame groups in this file format.",
    5666: "The attached file '%s' should be stored in the same folder as in the main file, that is, '%s'.",
    5667: "The Model Component and its current Frame are incompatible : the Frame has not enough vertices",
    5668: "No problem found in this map.",
    5669: "There is a problem in this map :\n%s",
    5670: "You cannot remove this button. It comes from the '%s' toolbox.",
    5671: "The structure of the texture file is invalid. The Heretic II tool 'WAL2M8' is known to create such strange files that result in display errors if you look at textures from very far away in the game. You should use QuArK instead of WAL2M8 to make your Heretic II textures.",
    5672: "'%s' has a missing section, or a section designed for another version of the game//Missing section '%s'",
    5673: "Cannot convert '%s' to '%s'",
    5674: "Texture size",
    5675: "Enter a new size for this texture :",
    5676: "Texture resize can only apply to a texture, not a texture link",
    5677: "Invalid texture size. Try '%d %d'",
    5678: "Data image format error",
    5679: "%s contains an unsupported format (colormap %d, type %d, bpp %d)",
    5680: "This operation is not supported with 24-bit images; it requires a 256-color palettized image.",
    5681: "You have copied a large amount of data to the clipboard.\nDo you want to keep this data in the clipboard now ?",
    5682: "The file '%s' was automatically saved but not deleted, which means that QuArK crashed. Do you want to save it ?\n\nWarning : if you answer No, the auto-saved file will be deleted !",
    5683: "\nThe image quality will suffer from this operation.",
    5684: "* The image is about to be shrinked.\n",
    5685: "* The new image format does not support an alpha mask (transparency).\n",
    5686: "* A new palette is applied to the image.\n",
    5687: "* The image will be converted to the palette of %s.\n",
    5688: "Invalid texture extension in Defaults.qrk",
    5689: "This image has got no palette : it is a true-color 24-bit image",
    5690: "Welcome to QuArK!\n\nThis appears to be the first time you have started QuArK. You can press F1 at any time to get help.\n\nPlease report any bugs you might find to the QuArK development team at http://quark.sourceforge.net/forums/\nThank you!",
    5691: "Invalid Sprite File!",
    5692: "The file %s is not compressed\nusing stored, shrunk, imploded and deflated methods.\n\nLoading Aborted! (%d)",
    5693: "'%s' expected in %s",
    5694: "Syntax error in Shader file %s, line %d",
    5695: "Shader '%s' has no image to display",
    5696: "Shader images are read-only",
    5697: "Shader stage '%s' has no image to display",
    5698: "Shader '%s' not found in %s",
    5699: "(complex)",
    #5700: "%s or %s",
    5701: "The configuration-setting '.MAP comments prefix' for %s is empty.\nPlease correct this, or set the \"Don't write comments in .map files\" in Configuration->Map->Options.",
    5702: "Unknown map format: %s",

    # alexander would like to reserve 5703 .. 5729 for HL2 :-)
    5703: "%s contains an unsupported format (width %d, height %d, format %d)",
    5704: "Unable to retrieve the location of '%s'. Please make sure the location is set correctly in the Half-Life 2 configurations.",
    #5705: "reserved for hl2",
    #5706: "reserved for hl2",
    5707: "Error while handling GCF file:\nCall: %s\nError: %s",
    5708: "Image found",
    5709: "VTF image",
    5710: "GCF file",
    5711: "GCF folder",
    5712: "QuArK is about to clear the Steam cache in %s. Are you sure you want QuArK to do this?",
    5713: "steam file system",
    5714: "bad content id: %s",
    5715: "VMF file",
    5716: "VMT file",
    5717: "Syntax error in Material file %s, line %d",
    5718: "Could not load the VTF Lib//Error code %d",
    5719: "Could not load the HL Lib//Error code %d",
    5720: "Unable to load VTF file. Call to %s failed.",
    5721: "Unable to save VTF file. Call to %s failed.",
    5722: "Unable to load GCF file. Call to %s failed.\nError: %s",
    5723: "Unable to save GCF file. Call to %s failed.\nError: %s",
    5724: "Unable to load VPK file. Call to %s failed.\nError: %s",
    5725: "Unable to save VPK file. Call to %s failed.\nError: %s",
    5726: "Error while handling VPK file:\nCall: %s\nError: %s",
    5727: "Unable to load NCF file. Call to %s failed.\nError: %s",
    5728: "Unable to save NCF file. Call to %s failed.\nError: %s",
    5729: "Error while handling NCF file:\nCall: %s\nError: %s",
    5730: "Could not load the %s//Error code %d",
    5731: "An error occurred in the %s: %s",
    5732: "VPK file",
    5733: "VPK folder",
    5734: "NCF file",
    5735: "NCF folder",

    # Rowdy would like to reserve 5750..5769 for Doom 3 :-)
    5750: "Material '%s' has no image to display",
    5751: "Material images are read-only",
    5752: "Material stage '%s' has no image to display",
    5753: "Material list (Doom 3)",
    5754: "Syntax error in Material file %s, line %d",
    5755: "Material '%s' not found in %s",
    # 5756: reserved
    # 5757: reserved
    # 5758: reserved
    # 5759: reserved
    # 5760: reserved
    # 5761: reserved
    # 5762: reserved
    # 5763: reserved
    # 5764: reserved
    # 5765: reserved
    # 5766: reserved
    # 5767: reserved
    # 5768: reserved
    # 5769: reserved
	
	5770: "There were errors reading the map; please check the console.",

    # DanielPharos would like to reserve 6000 .. 6099 for all renderers
    6000: "Unable to create SceneObject//%s",
    6001: "No 3D driver configured. Please select a 3D driver in the Configuration dialog box",
    6002: "Could not find the 3D drivers (%s). You need either a graphics card with installed drivers or the software 3D library, depending on the choice you made in the Configuration dialog box//Error code %d",
    6003: "BuildScene - empty face",
    6004: "Bad LOD",
    6005: "Bad reverse LOD",
    6006: "Bad aspect ratio",

    6010: "Texture not loaded",
    6011: "Invalid value for %s found: %d. Using default",
    6012: "No valid value for %s found, defaulting to: %d",
    6013: "Unable to load Desktop Window Manager (DWM).//Desktop Composition may be enabled, causing corruption in OpenGL and DirectX viewports",
    6014: "Error during handling of the renderer Dummy Window: %s",

    # DanielPharos would like to reserve 6100 .. 6199 for the software renderer
    6100: "Error with the Software 3D drivers//%s failed",

    6120: "Software 3D renderer does not support fullscreen views (yet)",
    6121: "You must first call Open3Dfx",

    # DanielPharos would like to reserve 6200 .. 6299 for the Glide renderer
    6200: "Error with the 3Dfx Glide drivers//%s failed",

    6220: "Glide renderer does not support fullscreen views (yet)",
    6221: "You must first call Open3Dfx",

    # DanielPharos would like to reserve 6300 .. 6399 for the OpenGL renderer
    6300: "Could not load the OpenGL drivers//Error code %d",
    6301: "Error in OpenGL initialization//'%s' failed",
    6302: "Error in OpenGL commands [Error code(s) %s step %d]",
    6303: "An error '%s' occurred in the OpenGL routine '%s'",
    6304: "Unable to load OpenGL extension list. All OpenGL extensions will be disabled",
    6305: "Error in OpenGL finalization//'%s' failed",

    6310: "Unable to make OpenGL context current. Try updating your video card drivers. If that doesn't work, use another renderer",
    6311: "Unable to create OpenGL context. Try updating your video card drivers. If that doesn't work, use another renderer",
    6312: "Unable to delete OpenGL context. Try updating your video card drivers. If that doesn't work, use another renderer",
    6313: "Out of OpenGL display lists. Try updating your video card drivers. If that doesn't work, disable the display lists option in the Configuration dialog box",
    6314: "Out of OpenGL texture numbers. Try updating your video card drivers. If that doesn't work, use another renderer",
    6315: "Failed to swap buffers. Try updating your video card drivers. If that doesn't work, disable the double buffering option in the Configuration dialog box",

    6320: "OpenGL renderer does not support fullscreen views (yet)",
    6321: "An error occurred in the OpenGL routines: CurrentSurf is nil!",

    # DanielPharos would like to reserve 6400 .. 6499 for the DirectX renderer
    6400: "Error in DirectX initialization//'%s'",
    6401: "Error in DirectX uninitialization//'%s'",
    6402: "Could not load the DirectX drivers//Error code %d",
    6403: "Error using DirectX//Function '%s' failed with '%s'",

    6410: "Internal driver error in DirectX. Try updating your video card drivers and DirectX. If that doesn't work, use another renderer",
    6411: "Unable to load DirectX 9. Make sure DirectX 9.0c is installed",
    6412: "Unable to find a DirectX 9 compatible device",

    6420: "DirectX renderer does not support fullscreen views (yet)",
    6421: "Direct3D: Hardware vertex processing selected",
    6422: "Direct3D: Software vertex processing selected",
    6423: "Direct3D: Pure device enabled",
    6424: "Direct3D: Pure device disabled",

# Negative numbers are never used directly by QUARK5.EXE.

    -101: "Cannot drop this item into a map.",
    #-102: "\nNote: to use a bitmap as a texture, you must first convert the bitmap into a texture : in the Texture Browser, choose 'Paste Special' instead of 'Paste'.",
    -103: "%d texture(s) could not be found. Are you sure you want to continue ?",
    -104: "This command uses the 3D viewer selected in options. Note that if you get a black screen it probably means you are looking at a part of your map where there is no light. In case of trouble (or to disable light computation) see the viewer section of the configuration dialog box and try again.\n\nIt is recommended to save your work first. Ok to load 3D viewer now ?",
    -105: "Note: when this button is pressed, the normal handles around the objects in your map are replaced by pink handles that let you do 'linear mapping' operations.\n\n'Linear mapping' operations include rotations, zooms, and various distortions.\n\nClick again on this button to get the normal handles.",
    -106: "Cannot drop this item here.",
    -107: "Incompatible items.",
    -151: "No Current Component !\n\nYou must first select a component\nto receive this item then try again.",

    -409: "Bezier",

    -459: "Parameters about the selected Bezier patch(es)|bezier patches",

}

# ----------- REVISION HISTORY ------------
#$Log: qdictionnary.py,v $
#Revision 1.158  2013/06/30 15:18:29  danielpharos
#Updated for 6.6 Beta 6 release.
#
#Revision 1.157  2012/07/01 12:24:12  danielpharos
#Improved MapError error message.
#
#Revision 1.156  2011/07/29 15:19:31  danielpharos
#Bumped version number to 6.6 Beta 5.
#
#Revision 1.155  2011/05/11 20:10:13  danielpharos
#Updated all version numbers for 6.6 Beta 4 release.
#
#Revision 1.154  2010/12/11 22:29:33  danielpharos
#Added CoD2 bsp file type.
#
#Revision 1.153  2010/10/16 22:50:17  danielpharos
#Added experimental RMF file loading support; poly's only, no UV's or textures.
#
#Revision 1.152  2010/10/16 22:31:04  danielpharos
#Added NCF file loading support (for example: Alien Swarm). Also, corrected VPK dictionnary mistake.
#
#Revision 1.151  2010/10/16 22:14:57  danielpharos
#Added VPK file loading support (for example: Left 4 Dead).
#
#Revision 1.150  2010/10/16 21:47:42  danielpharos
#Reworked GCF file loading. HLLib now directly called. Updated to HLLib 2.3.0. Fixed JPG-library setting being used in VTF file saving.
#
#Revision 1.149  2010/05/03 04:06:09  cdunde
#Code update.
#
#Revision 1.148  2010/04/16 20:07:25  danielpharos
#Move some version-stuff about. quarkpy now also checks the minor version number.
#
#Revision 1.147  2010/03/07 09:45:44  cdunde
#Added strings for model editor.
#
#Revision 1.146  2010/02/16 20:16:47  danielpharos
#Updated website address.
#
#Revision 1.145  2010/01/31 21:36:08  danielpharos
#Cleaned up some wording.
#
#Revision 1.144  2009/07/14 23:19:54  danielpharos
#Fixed typo.
#
#Revision 1.143  2009/06/03 05:16:22  cdunde
#Over all updating of Model Editor improvements, bones and model importers.
#
#Revision 1.142  2009/04/28 21:30:56  cdunde
#Model Editor Bone Rebuild merge to HEAD.
#Complete change of bone system.
#
#Revision 1.141  2009/03/16 08:46:00  danielpharos
#Updated to DevIL 1.7.8, added IWI loading, and added many new image loading/saving options.
#
#Revision 1.140  2009/03/13 09:15:10  danielpharos
#Added a Reset-button to the configuration window.
#
#Revision 1.139  2009/02/14 17:35:41  danielpharos
#You can now "uninstall" gamemodes: just delete the addons-directory of that game. Also, small code changes to accommodate this.
#
#Revision 1.138  2008/11/20 23:45:53  danielpharos
#Big update to renderers: mostly cleanup, and stabilized Direct3D a bit more.
#
#Revision 1.137  2008/10/14 00:07:12  danielpharos
#Add an integer list as a specific type.
#
#Revision 1.136  2008/10/12 11:31:27  danielpharos
#Moved 6DX map format to separate file, and re-factored QkMap and QkQuakeMap.
#
#Revision 1.135  2008/10/10 19:43:33  danielpharos
#Fix .mtr files showing up as .shader.
#
#Revision 1.134  2008/10/09 12:58:40  danielpharos
#Added decent Sylphis map file support, and removed some redundant 'uses'.
#
#Revision 1.133  2008/10/09 11:31:46  danielpharos
#Added decent .col Sylphis archive support.
#
#Revision 1.132  2008/10/08 21:41:47  danielpharos
#Fixed website address.
#
#Revision 1.131  2008/09/20 21:07:51  danielpharos
#Removed MarsCaption option and added nice FirstRun dialogbox.
#
#Revision 1.130  2008/09/16 12:13:12  danielpharos
#Added support for CoD2 iwd files.
#
#Revision 1.129  2008/08/26 16:22:00  danielpharos
#Added filename of broken shader/material file to error-message.
#
#Revision 1.128  2008/08/26 15:11:45  danielpharos
#Added filename of broken qrk source file to error-message.
#
#Revision 1.127  2008/07/24 15:02:31  danielpharos
#Cleaned up texture name checking code and interface.
#
#Revision 1.126  2008/07/17 00:45:19  cdunde
#Added new .md2 exporter with progress bar and logging capabilities.
#
#Revision 1.125  2008/06/28 14:52:35  cdunde
#Added .lwo lightwave model export support and improved the importer.
#
#Revision 1.124  2008/05/24 19:02:26  danielpharos
#Moved a string to the dictionary
#
#Revision 1.123  2008/05/05 01:24:52  cdunde
#Update for new release.
#
#Revision 1.122  2008/04/26 15:44:42  danielpharos
#Added a new game-specific: ShadersType. This is a gamecode-value indicating what game-style shaders a game uses.
#
#Revision 1.121  2008/04/19 14:28:36  cdunde
#To activate RMB menu items.
#
#Revision 1.120  2008/02/24 14:41:32  danielpharos
#Fixed web-links not working anymore, and added a decent error message if a local file cannot be found.
#
#Revision 1.119  2008/02/23 18:54:02  danielpharos
#A lot of improvements to the OpenGL error messages.
#
#Revision 1.118  2008/02/23 18:25:02  danielpharos
#Fix a typo.
#
#Revision 1.117  2008/02/21 21:21:30  danielpharos
#Small auto-update update: just some minor things.
#
#Revision 1.116  2008/02/19 16:23:30  danielpharos
#Possible fix for OpenGL hanging on shutdown. Also removes some hacks, and should fix some OpenGL leaks.
#
#Revision 1.115  2008/02/11 13:56:09  danielpharos
#Added error messages, and fixed some RGB -> BGR
#
#Revision 1.114  2008/02/07 14:09:55  danielpharos
#Display progressbar when searching for updates
#
#Revision 1.113  2008/01/31 16:07:24  danielpharos
#Added FTX file loading and saving support (Heavy Metal: F.A.K.K. 2 textures).
#
#Revision 1.112  2007/12/06 15:47:53  danielpharos
#Fixed a wrong text.
#
#Revision 1.111  2007/11/19 00:08:39  danielpharos
#Any supported picture can be used for a view background, and added two options: multiple, offset
#
#Revision 1.110  2007/10/24 14:58:12  cdunde
#To activate all Movement toolbar button functions for the Model Editor.
#
#Revision 1.109  2007/10/23 14:47:51  danielpharos
#Fixed the filename being double in the not-found error message.
#
#Revision 1.108  2007/09/23 21:04:35  danielpharos
#Add Desktop Window Manager calls to disable Desktop Composition on Vista. This should fix/workaround corrupted OpenGL and DirectX viewports.
#
#Revision 1.107  2007/09/21 21:19:51  cdunde
#To add message string that is model editor specific.
#
#Revision 1.106  2007/09/10 10:24:25  danielpharos
#Build-in an Allowed Parent check. Items shouldn't be able to be dropped somewhere where they don't belong.
#
#Revision 1.105  2007/09/04 14:38:21  danielpharos
#Fix the white-line erasing after a tooltip disappears in OpenGL. Also fix an issue with quality settings in software mode.
#
#Revision 1.104  2007/08/15 16:28:11  danielpharos
#HUGE update to HL2: Took out some code that's now not needed anymore.
#
#Revision 1.103  2007/08/14 16:33:33  danielpharos
#HUGE update to HL2: Loading files from Steam should work again, now using the new QuArKSAS utility!
#
#Revision 1.102  2007/08/05 19:55:55  danielpharos
#Corrected and commented-out an unused and wrong line.
#
#Revision 1.101  2007/07/05 10:18:34  danielpharos
#Moved a string to the dictionary.
#
#Revision 1.100  2007/06/13 11:57:33  danielpharos
#Added FreeImage as an alternative for DevIL. PNG and JPEG file handling now also uses these two libraries. Set-up a new section in the Configuration for all of this.
#
#Revision 1.99  2007/06/13 11:44:46  danielpharos
#Changed a number of a string and removed an unused one.
#
#Revision 1.98  2007/06/13 11:43:23  danielpharos
#Small cleanup in code for reading setup.
#
#Revision 1.97  2007/05/15 15:25:27  danielpharos
#Added a vertical mirror/flip options for Glide, and changed the caption of the 3Dfx name.
#
#Revision 1.96  2007/05/09 16:14:47  danielpharos
#Big update to the DirectX renderer. Fade color should now display. Stability is still an issue however.
#
#Revision 1.95  2007/05/05 17:55:41  cdunde
#To fix small typo error.
#
#Revision 1.94  2007/05/02 22:34:43  danielpharos
#Added DDS file support. Fixed wrong (but unused then) DevIL DDL interface. DDS file saving not supported at the moment.
#
#Revision 1.93  2007/04/14 11:33:31  danielpharos
#Fixed a few typo's.
#
#Revision 1.92  2007/04/12 15:28:04  danielpharos
#Minor clean up.
#
#Revision 1.91  2007/04/12 10:51:03  danielpharos
#Added brushdef2 loading support.
#
#Revision 1.90  2007/04/02 22:12:21  danielpharos
#Moved one line to the dictionnary.
#
#Revision 1.89  2007/03/29 21:01:35  danielpharos
#Changed a few comments and error messages
#
#Revision 1.88  2007/03/29 17:27:27  danielpharos
#Updated the Direct3D renderer. It should now initialize correctly.
#
#Revision 1.87  2007/03/26 21:06:40  danielpharos
#Big change to OpenGL. Fixed a huge memory leak. Better handling of shared display lists.
#
#Revision 1.86  2007/03/25 13:51:50  danielpharos
#Moved a few dictionnary words around.
#
#Revision 1.85  2007/03/17 15:43:02  danielpharos
#Made another few dictionnary changes. Also fixed a double entry. And a small change in unloading the dll-files of VTFLib.
#
#Revision 1.84  2007/03/17 14:32:50  danielpharos
#Moved some dictionary entries around, moved some error messages into the dictionary and added several new error messages to improve feedback to the user.
#
#Revision 1.83  2007/03/01 17:34:44  danielpharos
#Added two new error messages for HL2.
#
#Revision 1.82  2007/02/08 16:36:43  danielpharos
#Updated VTF handling to use VTFLib. The HL2 memory leak is gone! Warning: SaveFile not working!
#
#Revision 1.81  2007/02/02 21:14:55  danielpharos
#Added a DirectX error message
#
#Revision 1.80  2006/12/03 23:13:28  danielpharos
#Fixed the maximum texture dimension for OpenGL
#
#Revision 1.79  2006/11/30 01:19:33  cdunde
#To fix for filtering purposes, we do NOT want to use capital letters for cvs.
#
#Revision 1.78  2006/11/29 07:00:25  cdunde
#To merge all runtime files that had changes from DanielPharos branch
#to HEAD for QuArK 6.5.0 Beta 1.
#
#Revision 1.76.2.8  2006/11/29 05:00:37  cdunde
#For version change to 6.5 Beta.
#
#Revision 1.76.2.7  2006/11/23 20:05:03  danielpharos
#Added new OpenGL error messages
#
#Revision 1.76.2.6  2006/11/01 22:22:41  danielpharos
#BackUp 1 November 2006
#Mainly reduce OpenGL memory leak
#
#Revision 1.77  2006/09/27 02:59:06  cdunde
#To add Copy, Paste and Cut functions to Specifices\Arg
#page RMB pop-up menu.
#
#Revision 1.76  2006/05/19 18:46:55  cdunde
#For the configuration revamping of RTCW.
#
#Revision 1.75  2005/10/15 00:47:57  cdunde
#To reinstate headers and history
#
#Revision 1.72  2005/09/21 15:42:59  peter-b
#More useful error message for core exceptions
#
#Revision 1.71  2005/08/15 21:18:53  cdunde
#update version to QuArK 6.5.0 alpha 1
#
#Revision 1.70  2005/07/03 20:24:32  alexander
#text for parse error in material
#
#Revision 1.69  2005/06/23 23:30:39  alexander
#vmt file string
#
#Revision 1.68  2005/04/01 19:33:33  alexander
#more progress indicators (textures and polys)
#
#Revision 1.67  2005/01/27 00:16:03  alexander
#added vmf file loading (brushes only)
#
#Revision 1.66  2005/01/26 23:40:22  alexander
#hl2 map format warning
#
#Revision 1.65  2005/01/11 01:45:21  alexander
#nicer messages
#
#Revision 1.64  2005/01/02 15:21:31  alexander
#access files via steam service - first
#
#Revision 1.63  2004/12/27 10:58:39  alexander
#changed some hl2 messages
#
#Revision 1.62  2004/12/22 11:37:40  rowdy
#Rowdy - first pass of support for Doom 3
#
#Revision 1.61  2004/12/21 09:03:02  alexander
#changed vtf loading to use QuArKVTF.dll
#
#Revision 1.60  2004/12/02 19:36:58  alexander
#added format names for hl2
#
#Revision 1.59  2004/12/02 18:55:15  alexander
#added vtf format name
#
#Revision 1.58  2004/11/23 10:52:45  rowdy
#added a few messages for Doom 3 (more to come), replaced non-ASCIi character in item 5387
#
#Revision 1.57  2004/11/18 18:15:49  alexander
#new messages for gcf files
#
#Revision 1.56  2004/11/07 16:24:22  alexander
#new: support for vtf file loading
#
#Revision 1.55  2003/07/21 04:50:02  nerdiii
#Linux compatibility ( '/' '\' )
#
#Revision 1.54  2003/04/29 14:31:12  nerdiii
#no message
#
#Revision 1.53  2003/03/17 01:51:13  cdunde
#Update hints and add infobase links where needed
#
#Revision 1.52  2002/05/16 09:09:15  tiglari
#Update version to 6.4 alpha (no diff from 6,3 yet)
#
#Revision 1.51  2002/05/13 11:32:30  tiglari
#update version
#
#Revision 1.50  2002/05/07 23:21:44  tiglari
#new syntax error
#
#Revision 1.49  2002/04/28 21:28:33  tiglari
#update version
#
#Revision 1.48  2002/02/26 23:22:59  tiglari
#update version
#
#Revision 1.47  2002/02/24 13:45:29  decker_dk
#Update version to "QuArK 6.3snap 2002feb24"
#Added #5181 and #810 for .PNG-images support.
#Added #5182 and #811 for Tribes 2 .VL2-files support.
#Added #5183 and #812 for Tribes 2 .CS-files support.
#
#Revision 1.46  2002/01/06 10:37:04  decker_dk
#update version to "QuArK 6.3snap 2002jan06"
#
#Revision 1.45  2001/08/06 00:19:01  tiglari
#update version
#
#Revision 1.44  2001/07/19 12:01:39  tiglari
#add 5180 string for 6dx map format
#
#Revision 1.43  2001/07/19 02:23:47  tiglari
#.hmf extension support for 6dx
#
#Revision 1.42  2001/07/09 09:53:11  tiglari
#update version #
#
#Revision 1.41  2001/06/18 02:36:19  tiglari
#update version
#
#Revision 1.40  2001/05/21 12:07:12  tiglari
#update version
#
#Revision 1.39  2001/05/07 08:54:18  tiglari
#update version
#
#Revision 1.38  2001/04/28 02:40:19  tiglari
#update version
#
#Revision 1.37  2001/03/09 09:33:43  tiglari
#update version
#
#Revision 1.36  2001/03/08 23:25:06  aiv
#entity tool finished completly i think.
#
#Revision 1.35  2001/02/27 20:29:03  decker_dk
#Item 5590 rewritten due to shaders.
#
#Revision 1.34  2001/02/25 11:22:51  tiglari
#bezier page support, transplanted with permission from CryEd (CryTek)
#
#Revision 1.33  2001/02/23 19:28:30  decker_dk
#KB to bytes, due to change in QkUnknown.PAS
#
#Revision 1.32  2001/02/14 23:34:59  alexander
#set name
#
#Revision 1.31  2001/02/12 03:46:54  tiglari
#reset snapshot #
#
#Revision 1.30  2001/02/02 08:24:24  tiglari
#updated version #
#
#Revision 1.29  2001/01/28 17:25:24  decker_dk
#Added entries 177 and 178. Modified 176, which split its text up into the two others.
#Added entry 5701.
#
#Revision 1.28  2001/01/21 15:52:31  decker_dk
#changed the error text #5572.
#
#Revision 1.27  2001/01/07 13:22:05  decker_dk
#Set Versionname.
#
#Revision 1.26  2001/01/02 19:29:20  decker_dk
#Help Snippet, press ESC to close
#
#Revision 1.25  2000/12/30 15:27:02  decker_dk
#- Direct3D
#
#Revision 1.24  2000/10/15 16:09:48  alexander
#added missing file type names for 3ds files
#added error message for bsp file type V46
#set name
#
#Revision 1.23  2000/09/25 00:11:19  alexander
#set name
#
#Revision 1.22  2000/09/14 17:59:17  decker_dk
#Altered msg #5505
#
#Revision 1.21  2000/09/10 13:02:12  alexander
#set name
#
#Revision 1.20  2000/09/01 00:49:52  alexander
#set name
#
#Revision 1.19  2000/08/20 11:08:22  aiv
#Added Error Code 5503
#
#Revision 1.18  2000/07/28 15:10:58  alexander
#set snapshot name
#
#Revision 1.17  2000/07/25 16:01:41  alexander
#set snapshot name
#
#Revision 1.16  2000/07/18 13:50:53  alexander
#set snapshot name
#
#Revision 1.15  2000/07/03 23:16:16  alexander
#set snapshot version
#
#Revision 1.14  2000/06/09 23:39:02  aiv
#More MD3 Support Stuff
#
#Revision 1.13  2000/06/02 16:00:22  alexander
#added cvs headers
#
#
#
