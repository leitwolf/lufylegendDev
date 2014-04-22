#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Author: lonewolf
# Date: 2013-10-26 11:23:48
# 
import sublime
import sublime_plugin
import functools
import os
import datetime
import json
import re
import subprocess
import sys
import time
import codecs
try:
    import helper
    import rebuild
    import definition
    import template
except ImportError:
    from . import helper
    from . import rebuild
    from . import definition
    from . import template

TEMP_PATH=""
DEFINITION_LIST=[]
USER_DEFINITION_LIST=[]

# init plugin,load definitions
def init():
    global TEMP_PATH,DEFINITION_LIST,USER_DEFINITION_LIST
    TEMP_PATH=sublime.packages_path()+"/User/lufylegendDev.cache"
    lufylegend_root = checkRoot(False)
    if lufylegend_root:
        initDefinition(lufylegend_root)
    path=os.path.join(TEMP_PATH,"user_definition.json")
    if os.path.exists(path):
        USER_DEFINITION_LIST=json.loads(helper.readFile(path))

# load definition when root defined
def initDefinition(root):
    global DEFINITION_LIST
    if len(DEFINITION_LIST)!=0:
        return
    list1=json.loads(definition.data)
    for item in list1:
        path=os.path.join(root, "src")
        item[2]=os.path.join(path, item[1])
        DEFINITION_LIST.append(item)


# check lufylegend_root exists
def checkRoot(showError=True):
    settings = helper.loadSettings("lufylegendDev")
    lufylegend_root = settings.get("lufylegend_root", "")
    if len(lufylegend_root)==0 and showError:
        sublime.error_message("lufylegend_root no set")
        return False
    return lufylegend_root


class JsNewFileCommand(sublime_plugin.WindowCommand):
    def run(self, dirs):
        self.window.run_command("hide_panel")
        title = "untitle"
        on_done = functools.partial(self.on_done, dirs[0])
        v = self.window.show_input_panel(
            "File Name:", title + ".js", on_done, None, None)
        v.sel().clear()
        v.sel().add(sublime.Region(0, len(title)))

    def on_done(self, path, name):
        filePath = os.path.join(path, name)
        if os.path.exists(filePath):
            sublime.error_message("Unable to create file, file exists.")
        else:
            code = template.jsTemplate
            # add attribute
            settings = helper.loadSettings("lufylegendDev")
            format = settings.get("date_format", "%Y-%m-%d %H:%M:%S")
            date = datetime.datetime.now().strftime(format)
            code = code.replace("${date}", date)
            author=settings.get("author", "Your Name")
            code = code.replace("${author}", author)
            # save
            helper.writeFile(filePath, code)
            v=sublime.active_window().open_file(filePath)
            # cursor
            v.run_command("insert_snippet",{"contents":code})
            sublime.status_message(name+" create success!")

    def is_enabled(self, dirs):
        return len(dirs) == 1


class CreateBuildXmlCommand(sublime_plugin.WindowCommand):
    def run(self, dirs):
        self.window.run_command("hide_panel")
        title = "build"
        on_done = functools.partial(self.on_done, dirs[0])
        v = self.window.show_input_panel(
            "File Name:", title + ".xml", on_done, None, None)
        v.sel().clear()
        v.sel().add(sublime.Region(0, len(title)))

    def on_done(self, path, name):
        filePath = os.path.join(path, name)
        if os.path.exists(filePath):
            sublime.error_message("Unable to create file, file exists.")
        else:
            code = template.buildTemplate
            settings = helper.loadSettings("lufylegendDev")
            compiler_path=settings.get("google_closure_compiler_path", "")
            if len(compiler_path)==0:
                compiler_path="<path>/compiler-latest/compiler.jar"
            code = code.replace("${compiler}", compiler_path)
            # save
            helper.writeFile(filePath, code)
            sublime.active_window().open_file(filePath)
            sublime.status_message(name+" create success!")

    def is_enabled(self, dirs):
        return len(dirs) == 1


class LufylegendGotoDefinitionCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        # select text
        sel=self.view.substr(self.view.sel()[0])
        if len(sel)==0:
            return
        lufylegend_root = checkRoot()
        if not lufylegend_root:
            return
        if len(DEFINITION_LIST)==0:
            initDefinition(lufylegend_root)
        # find all match file
        matchList=[]
        showList=[]
        for item in DEFINITION_LIST:
            if item[0]==sel:
                matchList.append(item)
                showList.append(item[1])
        for item in USER_DEFINITION_LIST:
            if item[0]==sel:
                matchList.append(item)
                showList.append(item[1])
        if len(matchList)==0:
            sublime.status_message("Can not find definition '%s'"%(sel))
        elif len(matchList)==1:
            filepath=matchList[0][2]
            if os.path.exists(filepath):
                self.view.window().open_file(filepath+":"+str(matchList[0][3]),sublime.ENCODED_POSITION)
            else:
                sublime.status_message("%s not exists"%(filepath))
        else:
            # multi match
            self.matchList=matchList
            self.lufylegend_root=lufylegend_root
            on_done = functools.partial(self.on_done)
            self.view.window().show_quick_panel(showList,on_done)
        
    def on_done(self,index):
        if index==-1:
            return
        item=self.matchList[index]
        filepath=item[2]
        filepath=os.path.abspath(filepath)
        if os.path.exists(filepath):
            self.view.window().open_file(filepath+":"+str(item[3]),sublime.ENCODED_POSITION)
        else:
            sublime.status_message("%s not exists"%(filepath))
        
    def is_enabled(self):
        sel=self.view.substr(self.view.sel()[0])
        if len(sel)==0:
            return False
        return True

    def is_visible(self):
        return helper.checkFileExt(self.view.file_name(),"js")


class LufylegendRebuildUserDefinitionCommand(sublime_plugin.WindowCommand):
    def __init__(self,window):
        super(LufylegendRebuildUserDefinitionCommand,self).__init__(window)
        self.lastTime=0

    def run(self, dirs):
        curTime=time.time()
        if curTime-self.lastTime<3:
            sublime.status_message("Rebuild frequently!")
            return
        self.lastTime=curTime
        global USER_DEFINITION_LIST
        USER_DEFINITION_LIST=rebuild.rebuild(dirs[0],TEMP_PATH)
        path=os.path.join(TEMP_PATH, "user_definition.json")
        data=json.dumps(USER_DEFINITION_LIST)
        if not os.path.exists(TEMP_PATH):
            os.makedirs(TEMP_PATH)
        helper.writeFile(path,data)
        sublime.status_message("Rebuild user definition complete!")
    
    def is_enabled(self, dirs):
        return len(dirs)==1

    def is_visible(self, dirs):
        return self.is_enabled(dirs)


class LufylegendCompressJsCommand(sublime_plugin.WindowCommand):
    def run(self, files):
        settings = helper.loadSettings("lufylegendDev")
        ant_path = settings.get("ant_path", "")
        if len(ant_path)==0:
            sublime.error_message("ant_path no set")
            return
        cmdPath=ant_path
        arr=os.path.split(files[0]) 
        path=arr[0]
        args=[ant_path,"-buildfile",arr[1]]
        if sublime.platform()=="osx":
            subprocess.Popen(args,cwd=path)
        elif sublime.platform()=="windows":
            child=subprocess.Popen(args,cwd=path)
            child.wait()
            self.window.run_command("refresh_folder_list")
    
    def is_enabled(self, files):
        return len(files)==1 and helper.checkFileExt(files[0],"xml")

    def is_visible(self, files):
        return self.is_enabled(files)


class LufylegendListener(sublime_plugin.EventListener):
    def __init__(self):
        self.lastTime=0

    def on_post_save(self, view):
        filename=view.file_name()
        if not filename:
            return
        if not helper.checkFileExt(filename,"js"):
            return
        # rebuild user definition
        curTime=time.time()
        if curTime-self.lastTime<2:
            return
        self.lastTime=curTime
        a=rebuild.rebuildSingle(filename,TEMP_PATH)
        arr=a[0]
        path=a[1]
        # remove prev
        global USER_DEFINITION_LIST
        for i in range(len(USER_DEFINITION_LIST)-1,0,-1):
            item=USER_DEFINITION_LIST[i]
            if item[2]==path:
                USER_DEFINITION_LIST.remove(item)
        USER_DEFINITION_LIST.extend(arr)
        path=os.path.join(TEMP_PATH, "user_definition.json")
        data=json.dumps(USER_DEFINITION_LIST)
        if not os.path.exists(TEMP_PATH):
            os.makedirs(TEMP_PATH)
        helper.writeFile(path,data)
        sublime.status_message("Current file definition rebuild complete!")

# st3
def plugin_loaded():
    sublime.set_timeout(init, 200)

# st2
if not helper.isST3():
    init()

