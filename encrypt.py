#!/usr/bin/env python3

import hashlib
import uuid
import sys

class crypt:
    def __init__(self):
        self.pyVs=sys.version_info.major #temporarily working cross version
        
    def getSha2_512(self, string, salt=0):
        """args: string to hash, optional salt (will create if not provided)
        returns: hashStr such as 'hash:salt', with len(hashStr)==161 """
        self.salt=salt if salt else uuid.uuid4().hex
        self.hashStr = hashlib.sha512(self.salt.encode()+string.encode()).hexdigest()+':'+self.salt
        return self.hashStr
    
    def checkSha2_512(self, string, hashStr):
        """args: string=str to check,
            hashStr= a string (in format 'hash:salt')
                OR a list of hashStrs,
                OR a 2 layer data structure of hashStrs (like db cursor) 
        returns: true if match else false """
        if (self.pyVs==2 and isinstance(hashStr, basestring)) or (self.pyVs==3 and isinstance(hashStr, str)):
            try:
                return hashStr if hashStr == self.getSha2_512(string, hashStr.split(':')[1]) else False
            except:
                return False
        else:
            for s in hashStr:
                if not(self.pyVs==2 and isinstance(hashStr, basestring)) and not(self.pyVs==3 and isinstance(hashStr, str)):
                    for ss in s:
                        try:
                            if ss==self.getSha2_512(string, ss.split(':')[1]):
                                return ss
                        except:
                            pass
                else:
                    try:
                        if s==self.getSha2_512(string, s.split(':')[1]):
                            return s
                    except:
                        pass
            return False

    def printAlgos(self):
        if self.pyVs ==2:
            print (hashlib.algorithms)
        else:
            print ("Currently available = "+ hashlib.algorithms_available)
            print("Guaranteed Available = "+hashlib.algorithms_guaranteed)
