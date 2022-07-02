from re import I
import all14 as src
import pandas as pd
import copy
import numpy as np
intrepid = (11, 0, "XU", 0, "", False, False)
kaga = (11, 5, "XU", 0, "", True, False)
spica = (12, 8, "XU", 0, "", True, False)
diana = (21, 2, "XU", 0, "", True, False) # person C
ingrid = (21, 4, "XU", 0, "", True, False)
lara = (22, 8, "XU", 0, "", True, False)
kelly = (33, 5, "XU", 0, "", True, False)
audrey = (33, 9, "XU", 0, "", False, False)
claire = (42, 2, "XU", 0, "", True, False)
marin = (44, 3, "XU", 1, "", False, False) # person B
sera = (45, 5, "XU", 0, "", True, True)
selica = (53, 5, "XU", 0, "", True, True)
jade = (54, 5, "XU", 0, "", True, False)
ayaka = (55, 5, "XU", 0, "", True, True) # person A
ellie = (55, 9, "XU", 0, "", True, True)

tiffany = ("C4", 9, "S", 0, "", False, False) # person D
keqing = ("C3", 9, "S", 0, "", False, False)
amelie = ("C2", 9, "S", 0, "", False, False)
mia = ("C1", 7, "S", 0, "", False, False)
ahri = ("C1", 9, "S", 0, "", False, False)
ruby = ("1C", 2, "S", 1, "", False, False)
pyrrha = ("C1V", 3, "S", 1, "", False, False)
akari = ("C1V", 9, "S", 1, "", False, False)
eula = ("CX12", 0, "S", 0, "", False, False)
symmetra = ("CX12", 9, "S", 0, "", False, False)
cori = ("1B", 0, "S", 1, "", False, False)
fasca = ("1B", 9, "S", 1, "", False, False)
laffey = ("CX5", 0, "S", 0, "", False, False)
athena = ("CX5", 9, "S", 0, "", False, False)
sayu = ("C1VCX5", 0, "S", 0, "", False, False)
marina = ("C1VCX5", 0, "S", 0, "", False, False)
alyx = ("C1H", 0, "S", 0, "", False, False)
korrina = ("1A", 0, "S", 1, "", False, False)

controls = pd.read_csv('tech_controls.txt', sep = '\t')
cursorprio = ["RH21", "LH21", "RH31", "LH31", "SP31", "EE01"]

def t21(str1, seed, key, vent = 0, str2 = "", isx = False, isxa = False):
    return src.to21(src.univ(str1, seed, key, vent, str2))

def inputs(str1, seed, key, vent = 0, str2 = "", isx = False, isxa = False):
    return src.getinputs(src.univ(str1, seed, key, vent, str2), isx, isxa)

# building the scheme...
def getabsdir(person):
    ins = inputs(*person); use = "EE01"; lcrc = []
    for i in cursorprio:
        if i in ins:
            use = i
            break
    for i in cursorprio:
        if i in ins:
            ins.remove(i)
    if use == "SP31":
        lcrc.append("SP11"); ins.remove("SP11")
    elif use == "LH21":
        lcrc.append(["LH41", "LH42"]); ins.remove("LH41"); ins.remove("LH42")
    elif use == "RH21":
        lcrc.append(["LRH41", "RH42"]); ins.remove("RH41"); ins.remove("RH42")
    return (use, ins, lcrc)

def getpairs(inst):
    ins = copy.deepcopy(inst)
    preserve_dir = ["RH10", "LH10", "HD00", "RF10", "LF10"]
    preserve_2s = [("HD11", "HD12", "HD13"), ("RH41", "RH42"), ("LH41", "LH42"), ("RH01", "RH02"), ("LH01", "LH02"), ("SP01", "SP02"), ("SP03", "SP04"), ("HD21", "HD22"), ("HD12", "HD13"), ("RF01", "RF02"), ("LF01", "LF02")]
    preserve_1s = ["RH41", "RH42", "LH41", "LH42", "SP01", "SP02", "SP03", "SP04", "RH01", "RH02", "LH01", "LH02", "SP11", "HD21", "HD22", "RF01", "RF02", "LF01", "LF02", "HD12", "HD13"]
    dirs = []; sw2 = []; sw1 = []
    for i in preserve_dir:
        if i in ins:
            dirs.append(i); ins.remove(i)
    for i in preserve_2s:
        k = True
        for j in i:
            if j not in ins:
                k = False
        if k:
            sw2.append(i)
            for j in i:
                ins.remove(j)
    for i in preserve_1s:
        if i in ins:
            sw1.append(i); ins.remove(i)
    return (dirs, sw2, sw1, ins)

def build(person):
    inst = getabsdir(person)[1]; reserved = []; mapped = []; lcrc = getabsdir(person)[2]
    dirs, sw2, sw1, ins = getpairs(inst); enh = False
    # initial build
    for i in dirs:
        reserved.append(i); reserved.append(i); reserved.append(i); reserved.append(i)
        mapped.append(4)
    for i in sw2:
        for j in i:
            if j == "HD11":
                enh = True
            else:
                reserved.append(j)
        mapped.append(2)
    for i in sw1:
        reserved.append(i)
        mapped.append(1)
    # rounding down to some multiple
    mults = [10, 8, 6, 4, 2, 1]
    for i in mults:
        if len(reserved) == 0:
            break
        if len(reserved) >= i:
            reserved = reserved[0:i]
            break

    counter = 0; xp = 1
    for i in range(len(mapped)):
        counter += mapped[i]
        if counter > len(reserved):
            xp = -1 * i
            break
    if xp < 0:
        mapped = mapped[:-xp]

    # adding unary if possible...
    unary = False
    if len(sw1) > 0:
        for i in sw1:
            if i not in reserved:
                reserved.append(i)
                unary = True
                break
    if len(sw2) > 0 and not unary:
        for i in sw2:
            for j in i:
                if j not in reserved:
                    reserved.append(j); unary = True
                    break
            else:
                continue
            break
    if enh and not unary:
        reserved.append("HD11"); enh = False; unary = True
    if "SP21" in inst and not unary:
        reserved.append("SP21>1"); unary = True
    if not unary:
        reserved.append("EE01>1"); unary = True
    mapped.append(0)

    for i in np.unique(reserved):
        if i != "SP21>1" and i != "EE01>1":
            inst.remove(i)
    if enh:
        inst.remove("HD11")
    return (reserved, inst, mapped, enh, lcrc)
    
def universal(person):
    pass

#print(inputs(*kaga))
# print(getabsdir(tiffany))
#print(build9(tiffany))
print(build(sera))
print(build(marin))

#print(getabsdir(tiffany))