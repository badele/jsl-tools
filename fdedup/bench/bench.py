#!/usr/bin/env python

'''
Created on 5 sept. 2011

@author: bruno.adele@jesuislibre.org
'''

import os
import sys
import string
import time
import matplotlib.pyplot as plt
from numpy import  *  
import hashlib
import random as rd


# Generate Random text
def getRandText(size):
    r = ''.join(rd.choice(string.ascii_letters + ' \n') for x in range(size))
    return r


# Return pretty size
def getPrettySize(size):
    i = 0
    psize = ''
    unit = ["o", "Ko", "Mo", "Go", "To", "Po", "Eo", "Zo", "Yo"]
    
    while size>=1024 and i<8:
        size = size/1024
        i=i+1

    psize = str(round(size,2))+unit[i]
    
    return psize

# Create file with a random datas
def createRandFile(filename,size,blocksize=8192):
    total=0
    randtext = getRandText(blocksize)
    try:
        f = open(filename,'wt')
        while total<size:
            # Calc minimal bufer size
            bsize = min(size-total,blocksize)

            # Write loop random datas
            f.write(randtext)
            
            total=total+bsize
    finally:
        f.close()
        

#bench and create random datas 
def writeTempData(filesize):
    blocksize=256
    MB = 1024*1024

    realsize = filesize*MB
    filename = '/tmp/testfile-%s' % filesize
    if not os.path.exists(filename):
    
        before = time.time()
        createRandFile(filename,realsize,blocksize)
        after = time.time()
        
        elapsed = after-before
        speed = realsize / elapsed
        print ('%s(bs %s) at %s/s (%ss)' % (getPrettySize(realsize),blocksize,getPrettySize(speed),round(elapsed,2)))

# Write all file size
def writeTempAllData(filesizes):

    
    for filesize in filesizes:
        writeTempData(filesize)
            

# Disable HDD Cache
def dropCache():             
    drop_cache =  open('/proc/sys/vm/drop_caches', 'w') 
    drop_cache.write('3\n')
    drop_cache.close()



# Loop calc hash (filesize,hash mode, block size)
def benchReadOneTask(blocksizes,filesizes,functions,nbloop=20):
    writeresult = {}
    MB = 1024*1024
    
    
    for filesize in filesizes:

        if os.path.exists('/root/tmp/bench-%sMB.png' % filesize):
            continue 
        
        writeresult[filesize] = {} 
        for function in functions:
            writeresult[filesize][function] = []
            for blocksize in blocksizes:
                hash = eval('hashlib.%s()' % function)
                realsize = filesize*MB
    
                speeds=[]
                for i in range(0,nbloop):
                    end = False
                    #dropCache()
                    before = time.time()
                    try:
                        f = open('/tmp/testfile-%s' % filesize,"rb")
                        #end = True
                        while 1:
                            # Si tout les chunks sont different on arrete
                            if end:
                                break;
                    
                            buf = f.read(blocksize)
                            if buf:
                                hash.update(buf)
                                hash.hexdigest()
                            else:
                                end = True
                        
                        after = time.time()
                        elapsed = after-before
                        speed = realsize / elapsed
                        speeds.append(speed)
                        print ('%s-%s(bs %s) at %s/s (%ss)' % (function,getPrettySize(realsize),blocksize,getPrettySize(speed),round(elapsed,2)))
                        
                    except:
                        f.close()
                        raise
            
                aspeed = array(speeds)
                rspeed =  (average(aspeed))
                rstd = std(speeds)
                print ('%s-%s(bs %s) at %s/s std:%s (%ss)' % (function,getPrettySize(realsize),blocksize,getPrettySize(rspeed),getPrettySize(rstd),round(elapsed,2)))
                writeresult[filesize][function].append(rspeed/(1024*1024))
        
        print ('######################## %s' % (function))
        x = blocksizes
        y = writeresult[filesize]
        generateGraph(filesize,functions,x,y)

    return writeresult


def generateGraph(fileid,functions,x,y):
    

#    for blocksize in blocksizes:
        plt.ylabel('MB/s')
        plt.xlabel('blocksize in byte')
        for function in functions:
            plt.plot(x, y[function],'-o',label=function)
        
        plt.suptitle("Comparison hashing algorithm ( size: %sMB )" % fileid)
        plt.legend(loc='lower center', fancybox=True, shadow=True, ncol=4)
        plt.xticks( [4096,8192,16385,32768,65536,98304],['4k','8k','16k','32k','64k','96k'] )
        plt.grid(True)
        plt.savefig('/root/tmp/bench-%sMB.png' % fileid)
        plt.close()



def make_ticklabels_invisible(fig):
    for i, ax in enumerate(fig.axes):
        ax.text(0.5, 0.5, "ax%d" % (i+1), va="center", ha="center")
        for tl in ax.get_xticklabels() + ax.get_yticklabels():
            tl.set_visible(False)



# Main
filesizes = [1,10,50,100,500]
blocksizes = [128,256,512,1024,2048,4096,8192,16385,32768,65536,98304]
functions = ['md5','sha1','sha256','sha512']

# Write Data
writeTempAllData(filesizes)

# run Benchmark
results = benchReadOneTask(blocksizes,filesizes,functions,10)        
        
