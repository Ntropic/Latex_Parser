# -*- coding: utf-8 -*-
"""
by: Michael Schilling (22.05.2020)
Script for converting latex documents in pieces, so that files included with 
\external{directoryname}{filename without '.tex'} are converted separately and 
imported as .pdf's


Install this function (for windows) by using "pyinstall --onefile latex_parse.py

Add resulting .exe to path variable in windows (to call from anywhere)

Call this function via: latex_parse "filename"

 -> The conversion settings are saved in variable compiler at the top 
 
 -> the header file can be split into two parts, separated by  the comment 
    "%%Minimal_Setup". so that the external pdf's can be converted faster using 
    only the top of the header file. 

 -> The external files are only updated if the loaded file has been changed 
    after the last conversion into pdf was executed

 -> The pdfs are saved next to the external files
 
 -> the compilation of external will try to convert the different files in 
    parallel
 
"""

import sys
import os
import csv
import subprocess


compiler='lualatex -shell-escape -synctex=1 -interaction=nonstopmode '

recalc_files=0

#filename="test_page" # This file is used to test this function
arglength=len(sys.argv) # How many arguments

if arglength<2:
    raise Exception("ERROR: Filename Required")
    sys.exit(1)
else:
    filename=sys.argv[1]
    
if arglength>2:
    recalc_files=sys.argv[2]
else:
    recalc_files=0 # Do not recalculate all files    

print("Parsing the file: "+filename)

## Scan File(s) for includetikz and includetikzsubentries
if not os.path.exists('Cache'):
    os.makedirs('Cache')

to_comp=[]
inputs=[]
inputs.append(filename)
inputs_checked=[]
i=0
while i<len(inputs): # More documents to still check
    with open(inputs[i]+'.tex','r') as curr_tex:
        j=0
        for line in curr_tex:
            j=j+1
            index_input=line.find("%%Minimal_Setup") #Ends the header
            if index_input>=0:
                #Create a cache header
                with open(inputs[i]+'.tex','r') as curr_tex:
                    #Check weather header existed
                    head_name=inputs[i]
                    cache_head=os.path.join('Cache',inputs[i]+'.tex')
                    if not os.path.exists(cache_head):
                        recalc_files=1
                        with open(cache_head,'w+') as new_tex:
                            k=0
                            for line in curr_tex:
                                new_tex.write(line)
                                k=k+1
                                if k>=j-1:
                                    break
                    else:
                        cache_head_time=os.path.getmtime(cache_head)
                        head_time=os.path.getmtime(inputs[i]+'.tex')
                        if head_time>cache_head_time:
                            recalc_files=1
                            with open(cache_head,'w+') as new_tex:
                                k=0
                                for line in curr_tex:
                                    new_tex.write(line)
                                    k=k+1
                                    if k>=j-1:
                                        break
                break
            else:
                is_done=line.find("%")
                if is_done<0:
                    is_done=1000000
                index_input=line.find("\input{")+7
                if index_input>=7:
                    line2=line[index_input:]
                    end_index=line2.find("}")+index_input
                    if is_done>end_index:
                        inputs.append(line[index_input:end_index])
                    #print(inputs)
                else:
                    index_input=line.find("\include{")+9
                    if index_input>=9:
                        line2=line[index_input:]
                        end_index=line2.find("}")+index_input
                        if is_done>end_index:
                            inputs.append(line[index_input:end_index])
                        #print(inputs)
                    else:
                        index_input=line.find("\external{")+10
                        if is_done>index_input:
                            if index_input>=10:
                                line2=line[index_input:]
                                end_index=line2.find("}{")+index_input
                                first_part=line[index_input:end_index]
                                line3=line[end_index+2:]
                                end_index2=line3.find("}")+end_index+2
                                second_part=line[end_index+2:end_index2]
                                to_comp.append(os.path.join(first_part,second_part))
#                            else:
#                                index_input=line.find("\includetikzsub{")+16
#                                if index_input>=16:
#                                    line2=line[index_input:]
#                                    end_index=line2.find("}{")+index_input
#                                    first_part=line[index_input:end_index]
#                                    line3=line[end_index+2:]
#                                    end_index2=line3.find("}{")+end_index+3
#                                    second_part=line[end_index+3:end_index2]
#                                    line4=line[end_index2+2:]
#                                    end_index3=line4.find("}")+end_index2+2
#                                    third_part=line[end_index2+2:end_index3]
#                                    if is_done>index_input:
#                                        to_comp.append(os.path.join(first_part,second_part,third_part))
                            
    i=i+1

#Find to_comp files and check when they were last changed
not_all=0
comp_index_list=[]
for i in range(0,len(to_comp)):
    curr_tex=to_comp[i]+'.tex'
    curr_pdf=to_comp[i]+'.pdf'
    if not os.path.exists(curr_tex):
        print('Cannot find the file '+curr_tex)
        not_all=1
    else:
        comp=0
        if not os.path.exists(curr_pdf):
            #Compile file
            comp=1
        else:
            #Check times
            time_tex=os.path.getmtime(curr_tex)
            time_pdf=os.path.getmtime(curr_pdf)
            if time_tex>time_pdf:
                #Compile file again
                comp=1
        if comp==1: #Create the file for compiling
            comp_index_list.append(i)

if recalc_files==1: #Add all files to compile list
    comp_index_list=list(range(0,len(to_comp)))
    
#Create files for compilation
j=0;
name_list=[]
for i in comp_index_list:
    curr_name2='file_'+str(j)
    curr_name=curr_name2+'.tex'
    name_list.append(curr_name2)
    with open(os.path.join('Cache',curr_name),'w+') as curr_tex:
        curr_tex.write('\\input{'+head_name+'}\n')
        curr_tex.write('\\usepackage[active, tightpage]{preview}\n')
        curr_tex.write('\\setlength\\PreviewBorder{1pt}\n')
        curr_tex.write('\\begin{document}\n')
        curr_tex.write('\\begin{preview}\n')

        name=os.path.join('..',to_comp[i])
        name=name.replace('\\','/')
        curr_tex.write('\\input{'+name+'}\n')

        curr_tex.write('\\end{preview}')
        curr_tex.write('\\end{document}')
    j=j+1
        
    
#Compile each of the Cache files
p=[]
for i in comp_index_list:
    print('Compiling '+to_comp[i])
    cache_file=os.path.join('Cache',name_list[i])
    command=compiler+'-aux-directory=Cache -output-directory=Cache '+cache_file+'.tex'
    pipe=subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.append(pipe)
    
#Output results
k=0
for pipe in p:
    i=comp_index_list[k]
    res=pipe.communicate()
    error_code=str(res[0]).split('\\r\\n')
    founder=0
    for j in range(0,len(error_code)):
        found=error_code[j].find('Fatal error occurred')
        if found>=0:
            print(error_code[j])
            founder=1
    if founder==0:
        print('Successfully compiled '+to_comp[i])
    cache_file=os.path.join('Cache',name_list[i])
    cache_pdf=cache_file+'.pdf'
    curr_pdf=to_comp[i]+'.pdf'
    os.replace(cache_pdf, curr_pdf)
    k=k+1
    
if not_all==1:
    raise Exception("Not all files were found -> See previous output for list of the missing files.")      
    sys.exit(1)

#Compile main document
print('Compiling '+filename+'.tex')
command=compiler+'-aux-directory=Cache '+filename+'.tex'

pipe = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
res = pipe.communicate()
error_code=str(res[0]).split('\\r\\n')
founder=0
for j in range(0,len(error_code)):
    found=error_code[j].find('Fatal error occurred')
    if found>=0:
        print(error_code[j])
        founder=1
        raise Exception("Not all files were found -> See previous output for list of the missing files.")      
        sys.exit(1)
if founder==0:
    print('Successfully compiled '+filename)
