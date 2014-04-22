#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Author: lonewolf
# Date: 2014-04-21 21:06:19
# 

jsTemplate="""/**
 * Author: ${author}
 * Date: ${date}
 */
"""

buildTemplate="""<?xml version="1.0"?>
<project name="Javascript compress project" basedir="." default="compile">
  <taskdef name="jscomp" classname="com.google.javascript.jscomp.ant.CompileTask" classpath="${compiler}"/>
  <target name="compile" depends="clear">
    <jscomp compilationLevel="simple" warning="quiet" debug="false" output="../js/Main.min.js">
      <sources dir="${basedir}">
        <file name="../src/a.js"/>
      </sources>
    </jscomp>
  </target>
  <target name="clear">
    <delete file="../js/Main.min.js"/>
  </target>
</project>
"""