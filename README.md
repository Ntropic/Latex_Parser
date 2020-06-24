# Latex_Parser
## Parses and compiles Latex documents, and comiles external files separately and in parallel. 

### Function: 
Similarly to *tikzexternalize* you can include files via the command *\external{directoryname}{filename without '.tex'}*, which are compiled separately by the **latex_parser** and then included as pdf's in the document. 

### Advantages:
As the external files are only compiled if the .tex definition of them was changed, this allows compile times to be reduced on subsequent compile runs, furthermore the compiles are parallelized, increasing compile time. tikzexternalize has the downside, that if a single externalized file doesn't compile correctly, all others are also not saved properly. With this approach, you will get informed which compilation failed, but the others will still be performed correctly. In the final output, the failed external part will then be replaced by an empty placeholder box with the name of the failed compile filename. 

### Installation:
Install this function (for windows) by using *"pyinstall --onefile latex_parse.py"*

Add resulting .exe to **path** variable in windows (to call from anywhere)

Call this function via: *latex_parse filename*

### How it works:
* The conversion settings are saved in the variable *compiler* at the top of the script, by default this is *compiler='lualatex -shell-escape -synctex=1 -interaction=nonstopmode '*
* the header file can be split into two parts, separated by the comment *%%Minimal_Setup*. This way the external pdf's can be converted faster using only the top of the header file, if they external files do not require every package to run. 
* The external files are only updated if the loaded file has been changed after the last conversion into pdf was executed
* The pdfs are saved in the folders together with the external files
* The *external* command has to be defined in the *header*, for this to work. Just paste the definition from the example *header*.
