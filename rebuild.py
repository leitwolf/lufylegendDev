#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Author: lonewolf
# Date: 2013-11-11 23:08:52
# 
import os
import re
import codecs
try:
    import helper
except ImportError:
    from . import helper

snippetTemplate = """<snippet>
    <content><![CDATA[$content]]></content>
    <tabTrigger>$trigger</tabTrigger>
    <scope>source.js</scope>
    <description>$desc</description>
</snippet>
"""

# user definition path: SAVE_DIR/user_definition.json
USER_DEFINITIONS=[]
# auto completions path: SAVE_DIR/md5(filePath)/...
SAVE_DIR=""

def rebuild(dir,saveDir):
    global USER_DEFINITIONS
    global SAVE_DIR
    USER_DEFINITIONS=[]
    SAVE_DIR=saveDir
    # delete files first
    deleteFiles(saveDir,saveDir)
    parseDir(dir)
    return USER_DEFINITIONS

def rebuildSingle(file,saveDir):	
    global USER_DEFINITIONS
    global SAVE_DIR
    USER_DEFINITIONS=[]
    SAVE_DIR=saveDir
    parseJs(file)
    return [USER_DEFINITIONS,file]

def parseDir(dir):
    for item in os.listdir(dir):
        path=os.path.join(dir,item)
        if os.path.isdir(path):
            parseDir(path)
        elif os.path.isfile(path):
            if helper.checkFileExt(path,"js"):
                parseJs(path)

def parseJs(file):
    # remove all file
    md5filename=helper.md5(file)
    saveDir=os.path.join(SAVE_DIR,md5filename)
    deleteFiles(saveDir,saveDir)
    # create dir
    if not os.path.exists(saveDir):
        os.makedirs(saveDir)
    # add filepath to filepath.txt for debug
    filepath=os.path.join(saveDir,"filepath.txt")
    helper.writeFile(filepath,file)
    f=codecs.open(file,"r","utf-8")
    lineNum=0
    while True:
        line=f.readline()
        if line:
            lineNum+=1
            # function
            m=re.match("^\s*function\s*(\w+)\s*\((.*)\)",line)
            m2=re.match("^\s*(\w+)\:\s*function\s*\((.*)\)",line)
            if m2:
                m=m2
            if m:
                handleFunction(saveDir,"",m.group(1),m.group(2))
                handleDefinition(m.group(1),file,lineNum)
                continue            
            m=re.match("^\s*(\w+)\.prototype\.(\w+)\s*=\s*function\s*\((.*)\)",line)
            if m:
                handleFunction(saveDir,m.group(1),m.group(2),m.group(3))
                handleDefinition(m.group(2),file,lineNum)
                continue
            # vars
            m=re.match("^\s*var\s+(\w+)",line)
            if m:
                handleVar(saveDir,m.group(1))
                handleDefinition(m.group(1),file,lineNum)
                continue
        else:
            break
    f.close()
    
def handleDefinition(keyword,file,lineNum):
    global USER_DEFINITIONS
    USER_DEFINITIONS.append([keyword,file,file,lineNum])

def handleFunction(saveDir,classname,funcName,params):
    arr=handleParams(params)
    content=funcName+"(%s)"%(arr[1])
    trigger=funcName+"(%s)"%(arr[0])
    template=snippetTemplate.replace("$content",content)
    template=template.replace("$trigger",trigger)
    template=template.replace("$desc",classname)
    a=""
    if arr[0]!="":
        args=arr[0].split(",")
        for i in range(0,len(args)):
            args[i]=re.sub("\W","",args[i])
        a="_".join(args)
        a="_"+a
    saveName=funcName+a+".sublime-snippet"
    savePath=os.path.join(saveDir,saveName)
    f=open(savePath, "w+")
    f.write(template)
    f.close()

def handleVar(saveDir,varName):
    template=snippetTemplate.replace("$content",varName)
    template=template.replace("$trigger",varName)
    template=template.replace("$desc",".")
    name=re.sub("\W","",varName)
    saveName=name+".sublime-snippet"
    savePath=os.path.join(saveDir,saveName)
    f=open(savePath, "w+")
    f.write(template)
    f.close()

def handleParams(params):
    args=[]
    for item in params.split(","):
        str1=re.sub("\s","",item)
        if str1!="":
            args.append(str1)
    args2=[]
    for i in range(0,len(args)):
        args2.append("${%d:%s}"%(i+1,args[i]))
    a1=", ".join(args)
    a2=", ".join(args2)
    return [a1,a2]

def loadRoot():	
    global lufylegend_root
    settings = helper.loadSettings("lufylegendDev")
    lufylegend_root = settings.get("lufylegend_root", "")

# delete files under dir
def deleteFiles(path,root):
    if not os.path.exists(path):
        return
    if os.path.isfile(path):
        try:
            os.remove(path)
        except Exception:
            pass
    elif os.path.isdir(path):
        for item in os.listdir(path):
            itemsrc=os.path.join(path,item)
            deleteFiles(itemsrc,root)
        if path!=root:            
            try:
                os.rmdir(path)
            except Exception:
                pass