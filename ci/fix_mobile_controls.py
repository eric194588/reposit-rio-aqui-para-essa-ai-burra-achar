#!/usr/bin/env python3
"""Fixes broken touch-input hooks in the public Android port on a temporary CI checkout.
This is NOT an Android runtime test.
"""
from pathlib import Path
import sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "mobile-source")
p=root/"source/backend/Controls.hx"
s=p.read_text(encoding="utf-8")
before=s
def replace_once(a,b):
    global s
    n=s.count(a)
    if n != 1:
        raise RuntimeError(f"Controls.hx unexpected anchor count {n}: {a[:80]!r}")
    s=s.replace(a,b,1)

for method,flag,phase in [("justPressed","anyJustPressed","0"),("pressed","anyPressed","1"),("justReleased","anyJustReleased","2")]:
    # Preserve keyboard/controller behaviour, add touch as an additional source.
    old=f"\t\treturn result || _myGamepad{method[0].upper()+method[1:]}(gamepadBinds[key]) == true;"
    new=(f"\t\t#if mobile\n\t\tif (touchState(key, {phase})) return true;\n\t\t#end\n"+old)
    replace_once(old,new)
# The old source contains FlxAction APIs from an incompatible controller design,
# including missing Control enum, forEachBound, and action collections.
start=s.index("\t#if mobile\n\tpublic var trackedInputsUI:")
end=s.index("\t// IGNORE THESE",start)
touch_source=r'''
	#if mobile
	public var trackedInputsUI:Array<FlxButton> = [];
	public var trackedInputsNOTES:Array<FlxButton> = [];
	private var _touchBindings:Map<String, Array<FlxButton>> = new Map();

	private function bindTouch(key:String, button:FlxButton, tracked:Array<FlxButton>):Void
	{
		if(button == null) return;
		var bound = _touchBindings.get(key);
		if(bound == null)
		{
			bound = [];
			_touchBindings.set(key, bound);
		}
		if(bound.indexOf(button) < 0) bound.push(button);
		if(tracked.indexOf(button) < 0) tracked.push(button);
	}

	private function touchState(key:String, phase:Int):Bool
	{
		var bound = _touchBindings.get(key);
		if(bound == null) return false;
		for (button in bound)
		{
			if(button == null) continue;
			var hit = switch(phase)
			{
				case 0: button.justPressed;
				case 1: button.pressed;
				case 2: button.justReleased;
				default: false;
			}
			if(hit)
			{
				controllerMode = false;
				return true;
			}
		}
		return false;
	}

	public function setHitBox(hitbox:FlxHitbox):Void
	{
		if(hitbox == null) return;
		bindTouch("note_left", hitbox.buttonLeft, trackedInputsNOTES);
		bindTouch("note_down", hitbox.buttonDown, trackedInputsNOTES);
		bindTouch("note_up", hitbox.buttonUp, trackedInputsNOTES);
		bindTouch("note_right", hitbox.buttonRight, trackedInputsNOTES);
	}

	public function setVirtualPadUI(pad:FlxVirtualPad, dpad:FlxDPadMode, action:FlxActionMode):Void
	{
		if(pad == null) return;
		switch(dpad)
		{
			case UP_DOWN:
				bindTouch("ui_up", pad.buttonUp, trackedInputsUI);
				bindTouch("ui_down", pad.buttonDown, trackedInputsUI);
			case LEFT_RIGHT:
				bindTouch("ui_left", pad.buttonLeft, trackedInputsUI);
				bindTouch("ui_right", pad.buttonRight, trackedInputsUI);
			case UP_LEFT_RIGHT:
				bindTouch("ui_up", pad.buttonUp, trackedInputsUI);
				bindTouch("ui_left", pad.buttonLeft, trackedInputsUI);
				bindTouch("ui_right", pad.buttonRight, trackedInputsUI);
			case LEFT_FULL | RIGHT_FULL | BOTH_FULL:
				bindTouch("ui_up", pad.buttonUp, trackedInputsUI);
				bindTouch("ui_down", pad.buttonDown, trackedInputsUI);
				bindTouch("ui_left", pad.buttonLeft, trackedInputsUI);
				bindTouch("ui_right", pad.buttonRight, trackedInputsUI);
				if(dpad == BOTH_FULL)
				{
					bindTouch("ui_up", pad.buttonUp2, trackedInputsUI);
					bindTouch("ui_down", pad.buttonDown2, trackedInputsUI);
					bindTouch("ui_left", pad.buttonLeft2, trackedInputsUI);
					bindTouch("ui_right", pad.buttonRight2, trackedInputsUI);
				}
			case NONE:
		}
		switch(action)
		{
			case A:
				bindTouch("accept", pad.buttonA, trackedInputsUI);
			case B:
				bindTouch("back", pad.buttonB, trackedInputsUI);
			case A_B | A_B_C | A_B_E | A_B_X_Y | A_B_C_X_Y | A_B_C_X_Y_Z | A_B_C_D_V_X_Y_Z:
				bindTouch("accept", pad.buttonA, trackedInputsUI);
				bindTouch("back", pad.buttonB, trackedInputsUI);
			case NONE:
		}
	}

	public function setVirtualPadNOTES(pad:FlxVirtualPad, dpad:FlxDPadMode, action:FlxActionMode):Void
	{
		if(pad == null) return;
		switch(dpad)
		{
			case UP_DOWN:
				bindTouch("note_up", pad.buttonUp, trackedInputsNOTES);
				bindTouch("note_down", pad.buttonDown, trackedInputsNOTES);
			case LEFT_RIGHT:
				bindTouch("note_left", pad.buttonLeft, trackedInputsNOTES);
				bindTouch("note_right", pad.buttonRight, trackedInputsNOTES);
			case UP_LEFT_RIGHT:
				bindTouch("note_up", pad.buttonUp, trackedInputsNOTES);
				bindTouch("note_left", pad.buttonLeft, trackedInputsNOTES);
				bindTouch("note_right", pad.buttonRight, trackedInputsNOTES);
			case LEFT_FULL | RIGHT_FULL | BOTH_FULL:
				bindTouch("note_up", pad.buttonUp, trackedInputsNOTES);
				bindTouch("note_down", pad.buttonDown, trackedInputsNOTES);
				bindTouch("note_left", pad.buttonLeft, trackedInputsNOTES);
				bindTouch("note_right", pad.buttonRight, trackedInputsNOTES);
				if(dpad == BOTH_FULL)
				{
					bindTouch("note_up", pad.buttonUp2, trackedInputsNOTES);
					bindTouch("note_down", pad.buttonDown2, trackedInputsNOTES);
					bindTouch("note_left", pad.buttonLeft2, trackedInputsNOTES);
					bindTouch("note_right", pad.buttonRight2, trackedInputsNOTES);
				}
			case NONE:
		}
		switch(action)
		{
			case A:
				bindTouch("accept", pad.buttonA, trackedInputsNOTES);
			case B:
				bindTouch("back", pad.buttonB, trackedInputsNOTES);
			case A_B | A_B_C | A_B_E | A_B_X_Y | A_B_C_X_Y | A_B_C_X_Y_Z | A_B_C_D_V_X_Y_Z:
				bindTouch("accept", pad.buttonA, trackedInputsNOTES);
				bindTouch("back", pad.buttonB, trackedInputsNOTES);
			case NONE:
		}
	}

	public function removeVirtualControlsInput(inputs:Array<FlxButton>):Void
	{
		if(inputs == null || inputs.length == 0) return;
		for(key in _touchBindings.keys())
		{
			var old = _touchBindings.get(key);
			if(old == null) continue;
			var kept:Array<FlxButton> = [];
			for(button in old)
				if(inputs.indexOf(button) < 0) kept.push(button);
			if(kept.length == 0) _touchBindings.remove(key);
			else _touchBindings.set(key, kept);
		}
	}
	#end

'''
s=s[:start]+touch_source+s[end:]
for stale in ("forEachBound(", "FlxActionInputDigitalIFlxInput", "digitalActions", "Control.NOTE_"):
    if stale in s:
        raise RuntimeError("Old action API survived replacement: "+stale)
p.write_text(s,encoding="utf-8")

for name in ("MusicBeatState.hx","MusicBeatSubstate.hx"):
    p=root/"source/backend"/name
    code=p.read_text(encoding="utf-8")
    old="import flixel.input.actions.FlxActionInput;"
    assert code.count(old)==1, name+" import changed"
    code=code.replace(old,"import mobile.flixel.FlxButton;\nimport mobile.flixel.FlxVirtualPad.FlxDPadMode;\nimport mobile.flixel.FlxVirtualPad.FlxActionMode;")
    old_type="Array<FlxActionInput>"
    assert code.count(old_type)>=1, name+" tracked type changed"
    code=code.replace(old_type,"Array<FlxButton>")
    p.write_text(code,encoding="utf-8")
print("Rewired touch controls to existing FlxButton input states in temporary checkout")
