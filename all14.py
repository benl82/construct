import numpy as np
import pandas as pd
import itertools

s14 = pd.read_csv('s14s.txt', sep = "\t")
gma = pd.read_csv('gma.txt', sep = "\t")
gma[['Component', 'Value', 'string']] = gma[['Component', 'Value', 'string']].astype(str)
upperx = pd.read_csv('upperx.txt', sep = "\t")
gmat = pd.read_csv('xcptest.txt', sep = "\t")

def z(ch):
    # converts abcd-ef... to actual string index
    k = {"A": 0, "B": 1, "C": 2, "D": 3,
    "E": 5, "F": 6, "G": 7, "H": 8, "I": 9,
    "J": 11, "K": 12, "L": 13,
    "M": 15, "N": 16,
    "A2": 18, "B2": 19, "C2": 20, "E2": 21, "F2": 22, "G2": 23, "H2": 24}
    return k[ch]

def to21(str14):
    if len(str14) > 20:
        return str14
    if str14[z("M")] == "1":
        return str14 + "-0000000"
    return str14 + "-" + str14[0:3] + str14[5:9]

# A class
def lamp(ch, enh):
    k = {"0" : "000", "C" : "200", "B" : "400", "A" : "440"}
    j = {"0" : "000", "C" : "000", "B" : "000", "A" : "310"}
    if (enh):
        return j[ch]
    return k[ch]

def uamp(ch, enh):
    k = {"0" : "0000", "C" : "4000", "B": "4400", "A": "4442"}
    j = {"0" : "0000", "C" : "0000", "B" : "2000", "A" : "2400"}
    if (enh):
        return j[ch]
    return k[ch]

def ampto14(str, enh = False):
    if str[0] == str[1] and str[2] == str[3]:
        return lamp(str[0], enh) + "0-" + uamp(str[2], enh) + "0-000-00"
    elif str[0] == "0" and str[2] == "0":
        return lamp(str[1], enh) + "0-" + uamp(str[3], enh) + "0-000-10"
    elif str[1] == "0" and str[3] == "0":
        return lamp(str[0], enh) + "0-" + uamp(str[2], enh) + "0-000-10"
    else:
        return lamp(str[0], enh) + "0-" + uamp(str[2], enh) + "0-000-20-" + lamp(str[1], enh) + "" + uamp(str[3], enh)

# S class
def sto14(str, seed = 9):
    k = s14[s14['Archetype'] == str]
    for index, row in k.iterrows():
        if seed <= row['MaxSeed']:
            return row['string']
    return "Not Found. Check your string and seed."

def enhsto14(str, seed = 9):
    s1 = sto14(str, seed)
    if s1[z("H")] != "4":
        s1 = s1[:z("E")] + "24" + s1[z("E") + 2:]
    return s1

def s21enh(s1):
    s1 = s1[:z("E")] + "24" + s1[z("E") + 2:]
    s1 = s1[:z("E2")] + "24" + s1[z("E2") + 2:]
    return s1

def enhgmato14(str, seed = 9):
    s1 = gmato14(str, seed)
    if s1[z("H")] != "4":
        s1 = s1[:z("E")] + "24" + s1[z("E") + 2:]
    return s1

# X class
def gmato14(str1, seed = 9):
    # separate by :
    str = str1.split(":")
    j = 0; str14 = ""
    for i in ['G', 'M', 'A']:
        k = gma[gma['Component'] == i]
        k = k[k['Value'] == str[j]]
        for index, row in k.iterrows():
            if seed <= row['MaxSeed']:
                str14 += row['string']
                break
        if (j == 0):
            str14 += "-"
        j += 1
    return str14 + "-000-00"

def upperxto14(val, seed = 9, vent = 0):
    k = upperx[upperx['Value'] == val]
    str1 = ""; str2 = ""
    for index, row in k.iterrows():
        if seed <= row['MaxSeed']:
            str1 = row['string1']
            str2 = row['string2']
            break
    if str2 == "SYMM":
        return str1 + str(vent) + str(val % 10 - 1) + "-00"
    else:
        return str1 + str(vent) + str(val % 10 - 1) + "-20-" + str2

# Hybrids
def ashybrid(astr, sstr, seed = 0, enh = False):
    a1 = ampto14(astr, enh); s1 = sto14(sstr, seed); f1 = ""
    if a1[z('M')] == '0':
        for i in range(len(a1)):
            f1 = f1 + max(a1[i], s1[i])
    else:
        a1 = to21(a1); s1 = to21(s1)
        for i in range(len(a1)):
            f1 = f1 + max(a1[i], s1[i])
        f1 = f1[:z('M')] + '2' + f1[z('M')+1:]
    return f1

def axhybrid(astr, xstr, seed = 0, enh = False):
    a1 = ampto14(astr, enh); x1 = gmato14(xstr, seed); f1 = ""
    if a1[z('M')] == '0':
        for i in range(len(a1)):
            f1 = f1 + max(a1[i], x1[i])
    else:
        a1 = to21(a1); x1 = to21(x1)
        for i in range(len(a1)):
            f1 = f1 + max(a1[i], x1[i])
        f1 = f1[:z('M')] + '2' + f1[z('M')+1:]
    return f1

def sxhybrid(sstr, xstr, seed = 0):
    s1 = sto14(sstr, seed); x1 = gmato14(xstr, seed); f1 = ""
    for i in range(len(s1)):
        f1 = f1 + max(s1[i], x1[i])
    return f1

def univ(str1, seed, key, vent = 0, str2 = ""):
    # key is: A, S, X, XU, AS, AX, SX
    if key == "A":
        return ampto14(str1)
    elif key == "S":
        return sto14(str1, seed)
    elif key == "X":
        return gmato14(str1, seed)
    elif key == "XU":
        return upperxto14(str1, seed, vent)
    elif key == "AS":
        return ashybrid(str1, str2, seed)
    elif key == "AX":
        return axhybrid(str1, str2, seed)
    elif key == "SX":
        return sxhybrid(str1, str2, seed)
    return "Check key value."

# to simplify
def comp(str1, ch, upper, split = 0):
    # 0 = assert left, 1 = assert at least 1 is true, 2 = assert both are true
    # make sure only for ABCEFGH that you split 1 and 2
    str1 = to21(str1)
    req = int(str1[z(ch)])
    if (split > 0):
        req2 = int(str1[z(ch+"2")])
    else:
        req2 = req
    if split == 0:
        return req <= upper
    elif split == 1:
        return req <= upper or req2 <= upper
    else:
        return req <= upper and req2 <= upper

# routine
def ute(str1):
    str1 = to21(str1)
    req1 = comp(str1, "D", 1)
    req2 = str1[z("E"):z("G")+1] == "000"
    req3 = str1[z("E2"):z("G2")+1] == "000"
    return req1 and (req2 or req3)

def changeu(str1, x = False):
    req1 = comp(str1, "E", 2, 2) or comp(str1, "F", 1, 2)
    req2 = comp(str1, "G", 2, 2)
    req3 = comp(str1, "G", 1, 2) or comp(str1, "H", 1, 2)
    req4 = comp(str1, "I", 2)
    req5 = comp(str1, "D", 1) or not x
    return req1 and req2 and req3 and req4 and req5

def changel(str1):
    req1 = comp(str1, "E", 2, 2) or comp(str1, "F", 1, 2)
    req3 = comp(str1, "G", 1, 2) or comp(str1, "H", 1, 2)
    return req1 and req3

def cat(str1):
    req1 = comp(str1, "E", 1, 2)
    req2 = comp(str1, "H", 2, 2)
    req3 = comp(str1, "I", 3)
    return req1 and req2 and req3

def catbag(str1):
    req1 = comp(str1, "E", 2, 2) or comp(str1, "F", 1, 2)
    req2 = comp(str1, "H", 2, 2)
    return req1 and req2

def support(str1):
    req1 = comp(str1, "E", 2, 2)
    req2 = comp(str1, "H", 1, 2)
    req3 = comp(str1, "J", 0)
    return req1 and req2 and req3

def changed(str1):
    req1 = comp(str1, "E", 2, 2) or comp(str1, "F", 1, 2)
    req2 = comp(str1, "H", 2, 2)
    req3 = comp(str1, "G", 1, 2) or comp(str1, "H", 1, 2)
    return req1 and req2 and req3

def clean(str1):
    req1 = comp(str1, "A", 1, 2) and comp(str1, "B", 1, 2) and comp(str1, "C", 1, 2) and comp(str1, "D", 1)
    req2 = comp(str1, "G", 1, 2) or comp(str1, "H", 1, 2)
    req3 = comp(str1, "G", 2, 2) or comp(str1, "I", 2)
    return req1 or (req2 and req3)

def swing(str1, x = False):
    req1 = comp(str1, "A", 1, 2) and comp(str1, "B", 1, 2) and comp(str1, "C", 1, 2) and comp(str1, "D", 1)
    req2 = comp(str1, "F", 2, 2) and comp(str1, "G", 1, 2) and comp(str1, "H", 2, 2)
    req5 = comp(str1, "D", 1) or not x
    return (req1 or req2) and req5

def ohp(str1):
    return comp(str1, "G", 2, 1) and comp(str1, "H", 3, 1) and comp(str1, "I", 2)

def manual(str1):
    return (comp(str1, "E", 2, 1) or comp(str1, "F", 1, 1)) and comp(str1, "G", 3, 1) and comp(str1, "H", 3, 1) and comp(str1, "I", 3)

def driver(str1, isxac = False):
    req1 = comp(str1, "A", 1, 1) and comp(str1, "C", 1, 1) and comp(str1, "E", 2, 1) and comp(str1, "F", 2, 1)
    req2 = comp(str1, "E", 2, 2) and comp(str1, "F", 2, 2)
    req3 = (comp(str1, "E", 2, 1) or comp(str1, "F", 2, 1)) and comp(str1, "J", 1)
    req4 = comp(str1, "J", 0) and comp(str1, "L", 3)
    req5 = comp(str1, "J", 1) and comp(str1, "L", 3) and not isxac
    if req1:
        return 1
    elif req2:
        return 2
    elif req3:
        return 3
    elif req4:
        return 4
    elif req5:
        return 5
    return 0

def bread(str1):
    req1 = (comp(str1, "E", 2, 1) or comp(str1, "F", 2, 1)) and comp(str1, "G", 3, 1) and comp(str1, "H", 3, 1) and comp(str1, "I", 3) and comp(str1, "L", 2)
    req2 = comp(str1, "A", 0, 1) and comp(str1, "B", 0, 1) and comp(str1, "C", 0, 1) and comp(str1, "D", 0, 1) and comp(str1, "L", 2)
    req3 = (comp(str1, "E", 2, 1) or comp(str1, "F", 2, 1)) and comp(str1, "H", 2, 1) and not comp(str1, "L", 2)
    return req1 or req2 or req3

def fire(str1):
    return comp(str1, "E", 2, 2) and comp(str1, "H", 2, 2) and comp(str1, "I", 3)

def firemw(str1):
    return (comp(str1, "E", 2, 2) or comp(str1, "F", 3, 2)) and comp(str1, "G", 3, 2)

def water(str1):
    return (comp(str1, "E", 2, 2) or comp(str1, "F", 1, 2)) and comp(str1, "G", 1, 2) and comp(str1, "I", 1)

# control scheme mapping, use 21length
def getinputs(str14, isx = False, isxa = False):
    str21 = to21(str14); inputs = []
    if int(str21[z("A")]) <= 1:
        inputs.append("LF10")
    if int(str21[z("A")]) <= 2:
        inputs.append("LF02")
    if int(str21[z("A")]) <= 3:
        inputs.append("LF01")
    if int(str21[z("A2")]) <= 1:
        inputs.append("RF10")
    if int(str21[z("A2")]) <= 2:
        inputs.append("RF02")
    if int(str21[z("A2")]) <= 3:
        inputs.append("RF01")
    if int(str21[z("E")]) <= 3 or int(str21[z("F")]) <= 3:
        inputs.append("LH01")
    if int(str21[z("E")]) <= 2 or int(str21[z("F")]) <= 2:
        inputs.append("LH02")
    if (int(str21[z("E")]) <= 2 and int(str21[z("F")]) <= 2) or int(str21[z("E")]) <= 1 or (int(str21[z("G")]) <= 3 and (int(str21[z("E")]) <= 2 or int(str21[z("F")]) <= 1)):
        inputs.append("LH10")
    if int(str21[z("E2")]) <= 3 or int(str21[z("F2")]) <= 3:
        inputs.append("RH01")
    if int(str21[z("E2")]) <= 2 or int(str21[z("F2")]) <= 2:
        inputs.append("RH02")
    if (int(str21[z("E2")]) <= 2 and int(str21[z("F2")]) <= 2) or int(str21[z("E2")]) <= 1 or (int(str21[z("G2")]) <= 3 and (int(str21[z("E2")]) <= 2 or int(str21[z("F2")]) <= 1)):
        inputs.append("RH10")
    # priority RH for xH
    if (int(str21[z("E2")]) <= 2 or int(str21[z("F2")]) <= 1) and int(str21[z("G2")]) <= 3 and int(str21[z("H2")]) <= 2:
        inputs.append("RH21")
    elif (int(str21[z("E")]) <= 2 or int(str21[z("F")]) <= 1) and int(str21[z("G")]) <= 3 and int(str21[z("H")]) <= 2:
        inputs.append("LH21")
    if int(str21[z("G2")]) <= 3 and int(str21[z("H2")]) <= 3 and int(str21[z("I")]) <= 3 and not isx:
        inputs.append("RH31")
    elif int(str21[z("G")]) <= 3 and int(str21[z("H")]) <= 3 and int(str21[z("I")]) <= 3 and not isx:
        inputs.append("LH31")
    if int(str21[z("E2")]) <= 3 or (int(str21[z("G2")]) <= 3 and int(str21[z("H2")]) <= 3):
        inputs.append("RH41")
        inputs.append("RH42")
    elif int(str21[z("E")]) <= 3 or (int(str21[z("G")]) <= 3 and int(str21[z("H")]) <= 3):
        inputs.append("LH41")
        inputs.append("LH42")
    if int(str21[z("J")]) <= 1:
        inputs.append("HD00")
    if int(str21[z("J")]) <= 2:
        inputs.append("HD11")
    if isx:
        if int(str21[z("J")]) <= 0:
            inputs.append("HD12")
            inputs.append("HD13")
        if int(str21[z("J")]) <= 3:
            inputs.append("HD21")
            inputs.append("HD22")
    else:
        if int(str21[z("J")]) <= 3:
            inputs.append("HD12")
            inputs.append("HD13")
        if int(str21[z("J")]) <= 0:
            inputs.append("HD21")
            inputs.append("HD22")
    if int(str21[z("L")]) <= 3:
        inputs.append("SP01")
        inputs.append("SP02")
        if int(str21[z("K")]) == 0:
            inputs.append("SP03")
            inputs.append("SP04")
    if int(str21[z("L")]) <= 2:
        inputs.append("SP11")
    if int(str21[z("L")]) <= 1:
        inputs.append("SP21")
    if isxa:
        if int(str21[z("L")]) <= 0 and int(str21[z("J")]) <= 2:
            inputs.append("SP31")
    elif int(str21[z("L")]) <= 2 and int(str21[z("J")]) <= 2:
        inputs.append("SP31")
    inputs.append("EE01")
    inputs.append("EE11")
    inputs.append("EE12")
    inputs.append("EE21")
    inputs.append("EE22")
    inputs.append("EE23")
    inputs.append("EE24")
    inputs.append("EE25")
    return inputs

'''
# testing all possibles...
def gen_a():
    return list(map(''.join, itertools.product("0CBA", repeat = 4)))

def enhtest(un, enh):
    if un and enh:
        return 3
    elif not un and enh:
        return 2
    elif un and not enh:
        return 1
    return 0

def enhtest2(un, enh):
    return bool(enhtest(un, enh))

gmat['string'] = gmat.apply(lambda row: gmato14([row.G, row.M, row.A], row.seed), axis = 1)
gmat['stringenh'] = gmat.apply(lambda row: enhgmato14([row.G, row.M, row.A], row.seed), axis = 1)
gmat['untoenh'] = gmat.apply(lambda row: ute(row.string), axis = 1)
gmat['changeu'] = gmat.apply(lambda row: changeu(row.string, True), axis = 1)
gmat['changeuENH'] = gmat.apply(lambda row: changeu(row.stringenh, True), axis = 1)
gmat['changel'] = gmat.apply(lambda row: changel(row.string), axis = 1)
gmat['changelENH'] = gmat.apply(lambda row: changel(row.stringenh), axis = 1)
gmat['cat'] = gmat.apply(lambda row: cat(row.string), axis = 1)
gmat['catENH'] = gmat.apply(lambda row: cat(row.stringenh), axis = 1)
gmat['catbag'] = gmat.apply(lambda row: catbag(row.string), axis = 1)
gmat['catbagENH'] = gmat.apply(lambda row: catbag(row.stringenh), axis = 1)
gmat['support'] = gmat.apply(lambda row: support(row.string), axis = 1)
gmat['supportENH'] = gmat.apply(lambda row: support(row.stringenh), axis = 1)
gmat['changed'] = gmat.apply(lambda row: changed(row.string), axis = 1)
gmat['changedENH'] = gmat.apply(lambda row: changed(row.stringenh), axis = 1)
gmat['clean'] = gmat.apply(lambda row: clean(row.string), axis = 1)
gmat['swing'] = gmat.apply(lambda row: swing(row.string, True), axis = 1)
gmat['swingENH'] = gmat.apply(lambda row: swing(row.stringenh, True), axis = 1)
gmat['ohp'] = gmat.apply(lambda row: ohp(row.string), axis = 1)
gmat['ohpENH'] = gmat.apply(lambda row: ohp(row.stringenh), axis = 1)
gmat['manual'] = gmat.apply(lambda row: manual(row.string), axis = 1)
gmat['manualENH'] = gmat.apply(lambda row: manual(row.string), axis = 1)
# gmat.to_csv('xcptest2.txt',sep="\t")

s14['stringenh'] = s14.apply(lambda row: enhsto14(row.Archetype, row.MaxSeed), axis = 1)
s14['untoenh'] = s14.apply(lambda row: ute(row.string), axis = 1)
s14['changeu'] = s14.apply(lambda row: changeu(row.string), axis = 1)
s14['changeuENH'] = s14.apply(lambda row: changeu(row.stringenh), axis = 1)
s14['changel'] = s14.apply(lambda row: changel(row.string), axis = 1)
s14['changelENH'] = s14.apply(lambda row: changel(row.stringenh), axis = 1)
s14['cat'] = s14.apply(lambda row: cat(row.string), axis = 1)
s14['catENH'] = s14.apply(lambda row: cat(row.stringenh), axis = 1)
s14['catbag'] = s14.apply(lambda row: catbag(row.string), axis = 1)
s14['catbagENH'] = s14.apply(lambda row: catbag(row.stringenh), axis = 1)
s14['support'] = s14.apply(lambda row: support(row.string), axis = 1)
s14['supportENH'] = s14.apply(lambda row: support(row.stringenh), axis = 1)
s14['changed'] = s14.apply(lambda row: changed(row.string), axis = 1)
s14['changedENH'] = s14.apply(lambda row: changed(row.stringenh), axis = 1)
s14['clean'] = s14.apply(lambda row: clean(row.string), axis = 1)
s14['swing'] = s14.apply(lambda row: swing(row.string), axis = 1)
s14['swingENH'] = s14.apply(lambda row: swing(row.stringenh), axis = 1)
s14['ohp'] = s14.apply(lambda row: ohp(row.string), axis = 1)
s14['ohpENH'] = s14.apply(lambda row: ohp(row.stringenh), axis = 1)
s14['manual'] = s14.apply(lambda row: manual(row.string), axis = 1)
s14['manualENH'] = s14.apply(lambda row: manual(row.stringenh), axis = 1)

amplist = gen_a()
df = pd.DataFrame({'source': amplist})
df['string'] = df.apply(lambda row: ampto14(row.source), axis = 1)
df['stringenh'] = df.apply(lambda row: ampto14(row.source, True), axis = 1)
df['untoenh'] = df.apply(lambda row: ute(row.string), axis = 1)
df['changeu'] = df.apply(lambda row: changeu(row.stringenh), axis = 1)
df['changel'] = df.apply(lambda row: changel(row.stringenh), axis = 1)
df['clean'] = df.apply(lambda row: clean(row.string), axis = 1)
df['swing'] = df.apply(lambda row: swing(row.stringenh), axis = 1)
df['ohp'] = df.apply(lambda row: ohp(row.stringenh), axis = 1)
df['manual'] = df.apply(lambda row: manual(row.stringenh), axis = 1)

colns = ['source', 'class', 'string', 'untoenh', 'changeu', 'changel', 'cat_any', 'support', 'changed', 'clean', 'swing', 'ohp', 'manual']
all14 = pd.DataFrame(columns = colns)
for ind, row in df.iterrows():
    all14.loc[len(all14.index)] = [row['source'], "A", row['string'], row['untoenh'], row['changeu'], row['changel'], "N/A", "N/A", "N/A", row['clean'], row['swing'], row['ohp'], row['manual']]
for ind, row in s14.iterrows():
    source = row['Archetype'] + "." + str(row['MaxSeed']); strng = row['string']; 
    chgl = enhtest(row['changel'], row['changelENH']); chgd = enhtest(row['changed'], row['changedENH'])
    ct = enhtest(row['cat'], row['catENH']); ct2 = enhtest(row['catbag'], row['catbagENH']); spt = enhtest(row['support'], row['supportENH'])
    mn = enhtest(row['manual'], row['manualENH'])
    untoe = "N/A"
    for i in [chgl, chgd, ct, ct2, spt, mn]:
        if i == 2:
            untoe = row['untoenh']
            break
    ct3 = "True (Inter)"
    if ct == 0 and (ct2 == 1 or ct2 == 3):
        ct3 = "True (Bag)"
    elif ct == 0 and ct2 == 2:
        ct3 = "True (Bag ENH)"
    else:
        ct3 = "False"
    all14.loc[len(all14.index)] = [source, "S", strng, untoe, row['changeu'], bool(chgl), ct3, bool(spt), bool(chgd), row['clean'], row['swing'], row['ohp'], bool(mn)]
for ind, row in gmat.iterrows():
    source = row['G'] + row['M'] + row['A'] + "." + str(row['seed']); strng = row['string']
    chgl = enhtest(row['changel'], row['changelENH']); chgd = enhtest(row['changed'], row['changedENH'])
    ct = enhtest(row['cat'], row['catENH']); ct2 = enhtest(row['catbag'], row['catbagENH']); spt = enhtest(row['support'], row['supportENH'])
    mn = enhtest(row['manual'], row['manualENH'])
    untoe = "N/A"
    for i in [chgl, chgd, ct, ct2, spt, mn]:
        if i == 2:
            untoe = row['untoenh']
            break
    ct3 = "True (Inter)"
    if ct == 0 and (ct2 == 1 or ct2 == 3):
        ct3 = "True (Bag)"
    elif ct == 0 and ct2 == 2:
        ct3 = "True (Bag ENH)"
    else:
        ct3 = "False"
    all14.loc[len(all14.index)] = [source, "X", strng, untoe, row['changeu'], bool(chgl), ct3, bool(spt), bool(chgd), row['clean'], row['swing'], row['ohp'], bool(mn)]
all14.to_csv('all14.txt', sep="\t")
'''