import all14 as src
import pandas as pd
import copy
import numpy as np
sgrraw = pd.read_csv('sgrraw.txt', sep = "\t")
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 5000) # these dont fucking work...

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
    return (reserved, inst, mapped, enh, lcrc)

def uniq(x):
    inds = np.unique(x, return_index = True)[1]
    return [x[i] for i in sorted(inds)]

def buildsgr(person):
    kx = sgrraw[sgrraw["ShortName"].isin(person)]
    kx = kx.reset_index()
    df = pd.DataFrame(columns = ["Name", "Reserved", "Available", "Mapped", "Enhanced", "LC RC"])
    for index, row in kx.iterrows():
        x = [row['ShortName']]
        x.extend(build((row['Source'], row['Seed'], row['Key'], row['Vent'], "", row['XCP'], row['ATH'])))
        df.loc[len(df.index)] = x
    df['Reserved'] = df.apply(lambda row: uniq(row.Reserved), axis = 1)
    return df

def universal(person):
    pass

#print(inputs(*kaga))
night71 = ["Ayaka", "Seraphine", "Zuikaku", "Pyra", "Federica", "Claire R", "Fujin", "Diana", "Ingrid", "Kaga"]
#print(buildsgr(night71)['Reserved'])
df1 = sgrraw[sgrraw['Key'] == "XU"]
df1 = df1.reset_index()
night72 = list(df1["ShortName"])
df2 = buildsgr(night72)

hasrf10 = []
hasotherdir = []; hasnodir = []
for index, row in df2.iterrows():
    if "RF10" in row["Reserved"] or "LF10" in row["Reserved"]:
        hasrf10.append(index)
    elif ("RF01" in row["Reserved"] or "LF01" in row["Reserved"]) and ("HD00" not in row["Reserved"]) and len(row["Reserved"]) <= 5:
        hasnodir.append(index)
    else:
        hasotherdir.append(index)
print(df2.iloc[hasrf10])
print(df2.iloc[hasnodir])
print(df2.iloc[hasotherdir])