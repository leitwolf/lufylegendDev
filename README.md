lufylegendDev ver 1.9.7
=========

Powerful lufylegend develop plugin for sublime text 2/3

## Description

[lufylegend](https://github.com/lufylegend/lufylegend.js) is a html5 game engine,light weight and powerful.
And lufylegendDev is a develop tool for lufylegend on sublime.

##Features

 * lufylegend api completions support
 * js system api completions support
 * goto definition
 * compress js files with ant and Google Closure Compiler
 * user definition auto completion
 * create new js file with template
 * create build.xml with template

## Installation

Download .zip source file, then unzip it,rename it with "lufylegendDev",then clone "lufylegendDev" folder into the SublimeText ```Packages``` directory.  A restart of SublimeText might be nessecary to complete the install.


## Usage

###setting

```
{
    "lufylegend_root": "<path>/lufylegend",
    "author": "<your name>",
    "ant_path": "ant",
    "google_closure_compiler_path": ""
}
```
you must set "lufylegend_root"

### goto definition

select a word then right click ->Goto Definition or press key ctrl+shift+g

### Compress js files

 right click a xml file on the sidebar,select "Compress js".

### User definition auto completion

 right click a folder on the sidebar,select "Rebuild User Definition".
 and when you save a js file in sublime,it will auto build all user definition in the current file.