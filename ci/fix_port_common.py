#!/usr/bin/env python3
"""Fixes verified Android-port compilation errors on the public source clone."""
from pathlib import Path
import sys
root = Path(sys.argv[1] if len(sys.argv)>1 else "mobile-source")
def patch_once(path, old, new):
    p = root / path
    s = p.read_text(encoding="utf-8")
    count = s.count(old)
    if count != 1: raise RuntimeError(f"{path}: patch anchor expected once, found {count}: {old!r}")
    p.write_text(s.replace(old,new,1),encoding="utf-8")
    print("Fixed:",path,repr(old))
patch_once("Project.xml",
           '<haxedef name="MODS_FOR_DESKTOP" if="desktop" />',
           '<haxedef name="MODS_FOR_DESKTOP" if="desktop || android" />')
patch_once("source/cutscenes/DialogueBoxPsych.hx",
           'else if(back || currentText >= dialogueList.dialogue.length)',
           'else if(backButtonReleased || currentText >= dialogueList.dialogue.length)')
p = root/"source/mobile/Utils.hx"
s=p.read_text()
if s.count("Util.existsLOL(") < 3: raise RuntimeError("Expected at least 3 mobile Utils old references")
p.write_text(s.replace("Util.existsLOL(", "Utils.existsLOL("))
print("Fixed:",p,"Util.existsLOL => Utils.existsLOL")
