import tkinter as tk
import re
from tkinter import LEFT, SCROLL, TRUE, filedialog 
import zipfile
import os
import shutil
import json
import fractions
import math
import time

filenamelist=[]
osulist=[]

def SelectOszFile():
    print("选择文件中......")
    global filepath
    filepath=filedialog.askopenfilename(title="Select .Osz file",
                                        filetypes=[("osz file","*.osz")],
                                        multiple=True)
    for i in range(len(filepath)):
        filenamelist.append(os.path.basename(filepath[i])[0:-4])
    print("文件选择完成！")

def UnzipFile():
    global filepath
    print("文件解压中......")
    if os.path.exists("./temp"):
        shutil.rmtree("./temp")
    if os.path.exists("./output"):
        shutil.rmtree("./output")
    for file in range(len(filenamelist)):
        os.makedirs(f"./temp/{filenamelist[file]}")
        os.makedirs(f"./temp/MCZ{filenamelist[file]}")
        with zipfile.ZipFile(filepath[file], 'r') as oszfile:
            oszfile.extractall(f"./temp/{filenamelist[file]}")
    print("文件解压完成！")

def Buildmc(osufile,i):
    print(f"正在处理{osufile}......")
    temposu=open(f"./temp/{filenamelist[i]}/{osufile}",encoding="utf-8")
    patterns=[r"AudioFilename:\s*(.+)",r"Artist:\s*(.+)",r"Creator:\s*(.+)",r'^0,0,"([^"]+)",\-?\d+,\-?\d+',r"Title:\s*(.+)",r"Version:\s*(.+)",r"BeatDivisor:\s*(.+)"]
    timepattern=r"(\d+),(\-?\d+\.?\d*),\d+,\d+,\d+,\d+,(\d),\d+"
    notepattern=r"^(\d+),\d+,(\d+),(\d+),\d+,(\d+):"
    artist="None"
    creator="None"
    title="None"
    version="None"
    beatdivisor=32
    timelist=[]
    bpmlist=[]
    bpmchangemslist=[]
    svmslist=[]
    notemslist=[]
    offset=0
    confirmedoffset=False
    effectlist=[]
    note=[]
    notepointer=[0,0,1]
    keys=set()
    temposu.seek(0)
    j=1
    k=1
    while True:
        line=temposu.readline()
        if not line:
            break
        match=re.search(patterns[0], line)
        if match:
            global audiofile
            audiofile=match.group(1)
            shutil.copyfile(f"./temp/{filenamelist[i]}/{audiofile}",f"./temp/MCZ{filenamelist[i]}/{audiofile}")
            break
    if audiofile=="None":
        print("未找到AudioFilename!")
        temposu.close()
        return
    temposu.seek(0)
    while True:
        line=temposu.readline()
        if not line:
            break
        match=re.search(patterns[1], line)
        if match:
            artist=match.group(1)
            break
    temposu.seek(0)
    while True:
        line=temposu.readline()
        if not line:
            break
        match=re.search(patterns[6], line)
        if match:
            beatdivisor=int(match.group(1))*25
            break
    temposu.seek(0)
    while True:
        line=temposu.readline()
        if not line:
            break
        match=re.search(patterns[5], line)
        if match:
            version=match.group(1)
            break
    temposu.seek(0)
    while True:
        line=temposu.readline()
        if not line:
            break
        match=re.search(patterns[2], line)
        if match:
            creator=match.group(1)
            break
    temposu.seek(0)
    while True:
        line=temposu.readline()
        if not line:
            break
        match=re.search(patterns[3], line)
        if match:
            global background
            background=match.group(1)
            shutil.copyfile(f"./temp/{filenamelist[i]}/{background}",f"./temp/MCZ{filenamelist[i]}/{background}")
            break
    if background=="None":
        print("未找到背景图!")
        temposu.close()
        return
    temposu.seek(0)
    while True:
        line=temposu.readline()
        if not line:
            break
        match=re.search(patterns[4], line)
        if match:
            title=match.group(1)
            break
    temposu.seek(0)
    while True:
        line=temposu.readline()
        match=re.search(timepattern, line)
        while True:
            if match and k+2<len(bpmlist) and int(match.group(1))>bpmlist[k+1]:
                k+=2
            if match and k>1 and int(match.group(1))<bpmlist[k-1]:
                k-=2
            else :
                break
        if match and match.group(3)=="1" and confirmedoffset == False:
            offset=int(match.group(1))
            timelist.append({"beat":[0,0,1],"bpm":round(float(60000/float(match.group(2))),3),"delay":0})
            confirmedoffset=True
            bpmlist.append(int(match.group(1)))
            bpmlist.append(round(float(60000/float(match.group(2))),3))
            bpmchangemslist.append(int(match.group(1)))
            svmslist.append(int(match.group(1)))
            pointer=[0,0,1]
            svpointer=[0,0,1]
            notemslist.append(int(match.group(1)))
        elif match and match.group(3)=="1" and confirmedoffset == True:

            deltabeats=(int(match.group(1))-bpmchangemslist[-1])/60000*bpmlist[-1]
            tempfrac=fractions.Fraction((pointer[0]+pointer[1]/pointer[2]+deltabeats)%1).limit_denominator(max_denominator=beatdivisor)
            pointer=[int(pointer[0]+pointer[1]/pointer[2]+deltabeats),tempfrac.numerator,tempfrac.denominator]
            bpmchangemslist.append(int(match.group(1)))

            bpmlist.append(int(match.group(1)))
            bpmlist.append(round(float(60000/float(match.group(2))),3))
            timelist.append({"beat":[pointer[0],pointer[1],pointer[2]],"bpm":bpmlist[-1],"delay":0})


        elif match and match.group(3)=="0":
            deltabeats=(int(match.group(1))-svmslist[-1])/60000*bpmlist[k]
            tempfrac=fractions.Fraction((svpointer[0]+svpointer[1]/svpointer[2]+deltabeats)%1).limit_denominator(max_denominator=beatdivisor)
            svpointer=[int(svpointer[0]+svpointer[1]/svpointer[2]+deltabeats),tempfrac.numerator,tempfrac.denominator]
            svmslist.append(int(match.group(1)))
            effectlist.append({"beat":[svpointer[0],svpointer[1],svpointer[2]],"scroll":-100/float(match.group(2))})

        elif line.startswith("[HitObjects]"):
            break
    while True:
        line=temposu.readline()
        match =re.search(notepattern, line)
        if match:
            keys.add(int(match.group(1)))
        if not line:
            break
    temposu.seek(0)
    while True:
        line=temposu.readline()
        match=re.search(notepattern, line)
        while True:
            if match and j+2<len(bpmlist) and int(match.group(2))>bpmlist[j+1]:
                j+=2
            else :
                break
        if match:
            deltabeats=0
            deltaendbeats=0
            p1list=[]
            p2list=[]
            pmslist=[]
            for p1 in range(len(bpmlist)):
                if bpmlist[p1]>notemslist[-1]:
                    p1list.append(p1)
            for p2 in range(len(bpmlist)):
                if bpmlist[p2]<int(match.group(2)):
                    p2list.append(p2)
            plist=list(set(p1list)&set(p2list))
            for a in range(len(plist)):
                pmslist.append(bpmlist[plist[a]])
            pmslist.append(int(match.group(2)))
            pmslist.append(notemslist[-1])
            pmslist.sort()

            for count in range(len(pmslist)-1):
                delta=(pmslist[len(pmslist)-count-1]-pmslist[len(pmslist)-2-count])/60000*bpmlist[j-count]
                deltabeats+=delta

            if match.group(3)!="128":

                tempfrac=fractions.Fraction((notepointer[0]+notepointer[1]/notepointer[2]+deltabeats)%1).limit_denominator(max_denominator=beatdivisor)
                notepointer=[int(notepointer[0]+notepointer[1]/notepointer[2]+deltabeats),tempfrac.numerator,tempfrac.denominator]
                note.append({"beat":[notepointer[0],notepointer[1],notepointer[2]],"column":math.floor(int(match.group(1))*len(keys)/512)})

                notemslist.append(int(match.group(2)))
            if match.group(3)=="128":

                endp1list=[]
                endp2list=[]
                endpmslist=[]
                for p1 in range(len(bpmlist)):
                    if bpmlist[p1]>int(notemslist[-1]):
                        endp1list.append(p1)
                for p2 in range(len(bpmlist)):
                    if bpmlist[p2]<int(match.group(4)):
                        endp2list.append(p2)
                endplist=list(set(endp1list)&set(endp2list))
                for a in range(len(endplist)):
                    endpmslist.append(bpmlist[endplist[a]])
                endpmslist.append(int(match.group(4)))
                endpmslist.append(notemslist[-1])
                endpmslist.sort()

                for count in range(len(endpmslist)-1):
                    enddelta=(endpmslist[len(endpmslist)-count-1]-endpmslist[len(endpmslist)-2-count])/60000*bpmlist[j-count]
                    deltaendbeats+=enddelta

                tempfrac=fractions.Fraction((notepointer[0]+notepointer[1]/notepointer[2]+deltaendbeats)%1).limit_denominator(max_denominator=beatdivisor)
                endbeatpointer=[int(notepointer[0]+notepointer[1]/notepointer[2]+deltaendbeats),tempfrac.numerator,tempfrac.denominator]

                deltabeats=(int(match.group(2))-notemslist[-1])/60000*bpmlist[j]
                tempfrac=fractions.Fraction((notepointer[0]+notepointer[1]/notepointer[2]+deltabeats)%1).limit_denominator(max_denominator=beatdivisor)
                notepointer=[int(notepointer[0]+notepointer[1]/notepointer[2]+deltabeats),tempfrac.numerator,tempfrac.denominator]

                notemslist.append(int(match.group(2)))
                note.append({"beat":[notepointer[0],notepointer[1],notepointer[2]],"endbeat":[endbeatpointer[0],endbeatpointer[1],endbeatpointer[2]],"column":math.floor(int(match.group(1))*len(keys)/512)})
        if not line:
            break
    note.append({"beat": [0,0,1],"type": 1,"sound": f"{audiofile}","x":10,"offset": -offset})
    mcfile={
        "meta":{"id":0,
                    "creator":creator,
                    "background":background,
                    "cover":"",
                    "version":version,
                    "mode":0,
                    "song":{"title":title,
                            "artist":artist,
                            "file":audiofile,
                            "bpm":bpmlist[1]},
                    "mode_ext":{"column":len(keys),
                                    "bar_begin":0},
                    "aimode":""},
        "time":timelist,
        "effect":effectlist,
        "note":note,
        "extra":None,
            }
    with open(f"./temp/MCZ{filenamelist[i]}/{osufile[0:-4]}.mc", "w", encoding="utf-8") as f:
        json.dump(mcfile, f, ensure_ascii=False,indent=None, separators=(',', ':'))
    print(f"{osufile}处理完成！")
    temposu.close()
    


def GetFileName(i):
    osulist.clear()
    for dirpath, dirnames, filenames in os.walk(f"./temp/{filenamelist[i]}"):
        for filename in filenames:
            if re.match(r'.*\.osu$', filename, flags=re.IGNORECASE):
                osulist.append(filename)
        break
    for name in osulist:
        Buildmc(name,i)



def CombinedFunction():
    starttime=time.time()
    SelectFileButton.config(state="disabled",text="转化中...")
    SelectOszFile()
    UnzipFile()
    for i in range(len(filenamelist)):
        GetFileName(i)
        with zipfile.ZipFile(f"./{filenamelist[i]}.mcz","w") as outputmcz:
            print(f"构建{filenamelist[i]}.mcz...")
            for dirpath, dirnames, filenames in os.walk(f"./temp/MCZ{filenamelist[i]}"):
                for filename in filenames:
                    outputmcz.write(os.path.join(dirpath, filename),arcname=filename)
            print(f"构建{filenamelist[i]}.mcz完毕！")
    SelectFileButton.config(state="disabled",text="转化完毕！")
    endtime=time.time()
    print(f"总用时：{endtime-starttime}秒")




root=tk.Tk()
root.title("osz to mcz tool by @NENENEKO")
root.geometry("400x200")

InfoLabel=tk.Label(root,
                   text="BugReport QQ:3125998062 Bilibili uid：348016585",
                   justify="left")
InfoLabel.place(x=0,y=170)

SelectFileButton = tk.Button(root, 
                             text="Select .osz File",
                             background='deepskyblue',
                             activebackground='royalblue',
                             command=CombinedFunction)
SelectFileButton.place(x=0, y=0)



root.mainloop()
