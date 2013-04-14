'''
Created on 14 Apr 2013

@author: pete
'''

import polib
import re
import os
import os.path
import json
import Error

class Index():
    def __init__(self, config):
        self.config = config
        self.wordIndex = self.config.wordIndex
        self.transIndex = self.config.transIndex
        self.packSize = self.config.packSize

    def fullIndex(self, source):
        self.source = source
        if not os.path.exists(self.source):
            raise Error.ROIIndexError(Error.SourceDirectoryNotExist)

        if not os.listdir(self.transIndex) == []:
            raise Error.ROIIndexError(Error.TransIndexNotEmpty)
        if not os.listdir(self.wordIndex) == []:
            raise Error.ROIIndexError(Error.WordIndexNotEmpty)
        
        for project in os.listdir(self.source):
            self.indexProject(project)
        
    def indexProject(self, project):
        self.windex = {}
        self.id_database = {}
        self.indexmeta = {}
        self.index = 0

        pos = ['en_GB.po','de.po','fr.po','as.po','az.po','be.po','cs.po','dz.po','ja.po']
        
        for pod in pos:
    
            #self.indexProjectLanguage(pod, project)
            self.indexmeta[pod] = {}
            self.windex[pod] = {}

            if not os.path.exists(self.transIndex+"/"+project+"/"+pod):
                os.makedirs(self.transIndex+"/"+project+"/"+pod)
            print pod
            print self.source+"/"+project+"/"+pod
            po = polib.pofile(self.source+"/"+project+"/"+pod)
            pattern = re.compile('[^a-zA-Z0-9 ]+')
            for entry in po.translated_entries():
                # entry.msgid, entry.msgstr
                sanitised = pattern.sub(' ', entry.msgstr)
                words=pattern.sub('', sanitised).split(" ")

                key = ",".join(map(lambda x:",".join(x), entry.occurrences))

                if pod == "en_GB.po":
                    self.id_database[key] = [self.index, entry.msgid]

                for word in words:
                    if len(word)>1:
                        wlower = word.lower()
                        pair = wlower[0:2]
                        
                        if not self.windex[pod].has_key(wlower[0:2]):
                            self.windex[pod][wlower[0:2]] = {wlower:{project:[]}}
                        else:
                            if not self.windex[pod][wlower[0:2]].has_key(wlower):
                                self.windex[pod][wlower[0:2]][wlower] = {project:[]}
                        try:
                            self.windex[pod][wlower[0:2]][wlower][project].append(self.id_database[key][0])
                        except KeyError:
                            continue

                try:
                    ourindex = str(self.id_database[key][0])
                    self.indexmeta[pod][int(ourindex)] = entry.msgstr
                except KeyError:
                    continue

                self.index += 1
    
        for pod in self.indexmeta:
            for p in range(0, len(self.indexmeta[pod]), self.packSize):
                f = open(self.transIndex+"/"+project+"/"+pod+"/"+str(p),"w")
                todump = {}
                for a in range(p, p+self.packSize):
                    try:
                        todump[a] = self.indexmeta[pod][a]
                    except KeyError:
                        if p<len(self.indexmeta[pod]):
                            continue
                        else:
                            break
                json.dump(todump, f)
                f.close()
    
        for pod in self.windex:
            for pair in self.windex[pod]:
                odir = self.wordIndex+"/"+pod+"/"+pair
                if not os.path.exists(odir):
                    os.makedirs(odir)
    
                if os.path.exists(self.wordIndex+"/"+pod+"/"+pair+"/"+pair):
                    f = open(self.wordIndex+"/"+pod+"/"+pair+"/"+pair)
                    old_windex = json.load(f)
                    f.close()
    
                    for word in self.windex[pod][pair]:
                        if old_windex.has_key(word):
                            old_windex[word][project] = self.windex[pod][pair][word][project]
                        else:
                            old_windex[word] = self.windex[pod][pair][word]
                    
                    f = open(self.wordIndex+"/"+pod+"/"+pair+"/"+pair, "w")
                    json.dump(old_windex, f)
                    f.close()
                else:
                    f = open(odir+"/"+pair, "w")
                    json.dump(self.windex[pod][pair], f)
                    f.close()