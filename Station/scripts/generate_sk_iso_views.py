#!/usr/bin/env python3
"""
Generate ISO view PNG images for all SK station FCStd files that need them.

Colour: sand/stone (0.75, 0.70, 0.60) to match platform ISOs.
Output: CADtrains/Station/images/<doc_name>_ISO.png  (1600×1000, white bg)
"""

import xmlrpc.client, sys
proxy = xmlrpc.client.ServerProxy("http://localhost:9875")

BASE     = "/home/abyrne/Projects/Trains/CADtrains/Station/"
FREECAD  = BASE + "freecad/"
IMAGES   = BASE + "images/"

TARGETS = [
    "SK_SidingWall",
    "SK_PassengerWall",
    "SK_GableWall",
    "SK_FloorBasic",
    "SK_FloorBasic_Plain",
    "SK_CeilingFull",
]

for doc_name in TARGETS:
    fc_path  = FREECAD + doc_name + ".FCStd"
    img_path = IMAGES  + doc_name + "_ISO.png"

    CODE = f'''
import FreeCAD, FreeCADGui, MeshPart

doc_name = "{doc_name}"
fc_path  = "{fc_path}"
img_path = "{img_path}"

try: FreeCAD.closeDocument(doc_name)
except: pass

doc = FreeCAD.openDocument(fc_path)
doc.recompute()

if FreeCAD.GuiUp:
    for obj in doc.Objects:
        if hasattr(obj, "ViewObject") and obj.ViewObject is not None:
            try:
                obj.ViewObject.ShapeColor = (0.75, 0.70, 0.60)
            except Exception:
                pass
    FreeCADGui.updateGui()
    view = FreeCADGui.ActiveDocument.ActiveView
    view.viewIsometric()
    view.fitAll()
    FreeCADGui.updateGui()
    view.saveImage(img_path, 1600, 1000, "White")
    print(f"Saved {{img_path}}")
else:
    print("GUI not available — skipping screenshot")

FreeCAD.closeDocument(doc_name)
_result_ = "Done"
'''

    print(f"Processing {doc_name} ...")
    result = proxy.execute(CODE)
    if result.get("success"):
        print(result.get("stdout", "").strip())
        print(f"  OK: {result.get('result')}")
    else:
        print(f"  ERROR: {result.get('error_message')}")
        print(result.get("error_traceback", ""))
