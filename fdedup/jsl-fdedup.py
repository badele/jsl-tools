#!/usr/bin/env python

# Sample, if you would like eliminate the duplicated file in folder2 (simulation mode)
#jsl-fdedup.py -n -i /subfolder/folder1 -e /subfolder/folder2 /subfolder/folder1/subfolder /subfolder/folder2/subfolder 

# Sample, if you would like eliminate the duplicated file in folder2 (execution mode)
#jsl-fdedup.py -m destinationfolder -i /subfolder/folder1 -e /subfolder/folder2 /subfolder/folder1/subfolder /subfolder/folder2/subfolder 


import os, sys, stat
import pprint
from subprocess import call
import getopt
import math
import shutil
import codecs

# Retrieve file with same size           
def getSameSizes(paths):
    size = 0
    samesizes = {}
    lastfile='\n'
    tmpfile = '/tmp/tmpfdedup'
    fslint='/usr/share/fslint/fslint/findup'

    os.system('rm -f %s' % tmpfile)
    params = ''
    for path in paths:
        params+="'%s' " % path
    #cmd = '%s -f %s > %s' % (fslint,params,tmpfile)
    cmd = '%s -f %s' % (fslint,params)
    
    #fstdout =  open(tmpfile, 'w','utf-8')
    fstdout = codecs.open(tmpfile, 'w','utf-8')
    fstderr =  open('%s.err' % tmpfile, 'w')
    call(cmd,stdout=fstdout,stderr=fstderr,shell=True)
    f = codecs.open(tmpfile,"r",'utf-8',errors='ignore')
    file = ''
    while 1:
        try:
            file = f.readline()

            # Line is empty
            if not file:
                break
    
            # New filename
            if file!='\n':
                filename = file.strip()
                
                if os.path.exists(file.strip()):
                    # If previous line is newfeed
                    if lastfile=='\n':
                        size = os.stat(filename).st_size
                        # If size not exist
                        if size not in samesizes:     
                            samesizes[size] = []
    
                    samesizes[size].append([filename,'?'])
                    lastfile = filename
            else:
                lastfile='\n'

        except (UnicodeDecodeError,OSError):
            print ('Error: %s' % filename)
            pass
            
    return samesizes

# Execute actions for all file in samesize 
def executeActions(size,samesizes,dstdir):

    for file in samesizes[size]:
        filename = file[0]
        action = file[1]
        if action=='>':
            dstfilename = '%s/%s' % (dstdir,filename)
    
            # Test and create directory
            srcdirname = os.path.dirname(filename)
            dstdirname = os.path.dirname('%s/%s' % (dstdir,filename))
            
            if os.path.exists(filename):
                if not os.path.exists(dstdirname):
                    os.makedirs(dstdirname)
                
                try:
                    shutil.move(filename,dstfilename)
                    os.rmdir(srcdirname)
                except:
                    pass

# Show actions for all file in samesize 
def showActions(size,samesizes):

    for file in samesizes[size]:
        filename = file[0]
        action = file[1]
        print ('%s %s' % (action,filename))
        
    print ('')

        
        
# Define actions for all file in samesize
def setActions(size,samesizes,**options):
    if options['move']=='':
        delaction = '-'
    else:
        delaction = '>'

    dirs = {}
    nbkeep = 0
    for file in samesizes[size]:
        filename = file[0]
        dirname = os.path.dirname(filename)

        file[1]='?'
        for exclude in excludes:
            if exclude in filename:
                file[1]=delaction

        for include in includes:
            if filename.find(include)==0:
                file[1]='+'
                nbkeep+=1

        if dirname not in dirs:
            dirs[dirname] = 1
        else:
            dirs[dirname]+=1
            

    if nbkeep==0:
        if options['keep']==1:
            samesizes[size][0][1] = '+'
        elif options['keep']==-1:
            samesizes[size][-1][1] = '+'

    if samedirectory:
        for dir in dirs:
            nb = dirs[dir]
            if nb>1:
                for file in samesizes[size]:
                    file[1] = '+'
    
# Analyse duplicates files
def deduplicateFiles(path,samesizes,**options):
    # Analyse
    final = {}
    if options['move']=='':
        delaction = '-'
    else:
        delaction = '>'
        
    

    # Set duplication action
    for size in samesizes:
        setActions(size,samesizes,**options)

        if options['norun']:
            showActions(size,samesizes)
        else:
            executeActions(size,samesizes,move)




# Main
opts, args = getopt.getopt(sys.argv[1:], "i:e:sflm:n" ,['includes=','excludes=','samedirectory','first','last','move=','norun'] )

move='' 
includes = []
excludes = []
norun=False
samedirectory = False
keep = 0 # (-1 last,0 None, 1 first, )
for opt, arg in opts:
        if opt in ("-i", "--includes"): includes.append(arg)
        elif opt in ("-e", "--excludes"): excludes.append(arg) 
        elif opt in ("-s", "--samedirectory"): samedirectory=True
        elif opt in ("-n", "--norun"): norun=True
        elif opt in ("-m", "--move"): move=arg
        elif opt in ("-f", "--first"): keep=1
        elif opt in ("-l", "--last"): keep=-1
 


if sys.argv[1:]:
    # Find same size

    samesizes = {}
    samesizes = getSameSizes(args)

    # Calc chunk
    deduplicateFiles(sys.argv[1:][0],samesizes,move=move,includes=includes,excludes=excludes,norun=norun,samedirectory=samedirectory,keep=keep)
    
else:
    print ("Please pass the paths to check as parameters to the script")



