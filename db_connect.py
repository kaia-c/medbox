#!/usr/bin/env python3

import encrypt
import sys
import pymysql
import datetime as dt
import math

WARNING_TOLERANCE=5 #=number of security warnings allowed in 1 hr.
                    #note - errors instantly change box mode, warnings
                    #can be set by admin to track lower priority concern accumulation
DEV_MODE=True
BIN_COUNT=2


class dbMedbox():
        ###########################################################
    def __init__(self, lati, longi):
        """lati & longi values can be set to False, but need supplied
        before box put in active mode (by admin or stocker who then can't open).
        Usage: Create a new dbMedbox instance once in program."""
        ###########################################################
        self.boxId=0
        self.pyVs=sys.version_info.major #remove once known 
        self.mode=0         #0=inactive/restock,
                            #1=active,
                            #2=admin (all other functions plus additional auth)
                            #-1=security alert
        self.nextMode=0
        self.open=False
        self.openAuth=False #True granted on checkRFID(rfid) success
        self.lastRFID=None  #self.lastRFID stores rfid.id key from
                            #last verfied RFID after first swipe.
        self.isAdmin1=False #True on verified rfid as admin
        self.isAdmin2=False #True on usernm/passwd verification by admin
        self.isStocker=False#True on RFID swipe by stocker
        self.numReqstByBin={}#stores {int binPos:int user requested from bin}
        #stores {int binPos:bool verify count on next open?}
        global BIN_COUNT
        self.verifyByBin={i:False for i in range(BIN_COUNT)}
        self.mileRadius=1   #miles allowed to roam
        self.latitude=lati if lati else None  #current lat
        self.longitude=longi if longi else None #current long
        self.latCenter=None #lat at center auth radius
        self.longCenter=None
        self.latDegInSM=0   #stores calc of miles in degree latitude by current latitude
        self.longDegInSM=0  #stores calc of miles in degree longitude by current latitude
        self.kitNeeds={}    #stores {int binPos:list item props}
                            #where list item props =
                                #[type('drug'|'equipt'),
                                # itemName (for 'drug' in format
                                #'proprietaryName : genName'), int qty ]
                            #if item type == 'drug' appends fields:
                                #[route (ie 'SUBCUTANEOUS'),
                                # dosage (ie '40 mg/ml, .005 mg/ml')]
        self.full=False
        self.setBoxId()
        if not lati or not longi:
            self.setDegrees(37,100)
        else:
            self.setDegrees(lati, longi, True)

        
    ###############################################################    
    #################    private-ish functions  ###################
    ###############################################################
    def __connect(self):
        self.cnx=pymysql.connect(user="root", passwd="RRCCpi2DC", 
            host="127.0.0.1", db="medbox", port=3306)
        self.cursor=self.cnx.cursor()

    def __complete(self):
        try:
            self.cnx.commit()
            self.cursor.close()
        except:
            pass
        self.cnx.close()

    def setBoxId(self):
        self.__connect()
        #each db in the box unit will only hold 1 box id, through which it can
        #sync with a master db not help on unit.
        self.cursor.execute("""SELECT id FROM box LIMIT 1;""")
        self.boxId=int([i[0] for i in self.cursor][0])
        self.__complete()


    def log(self, eventStr, drug_ndc=None, equipt_upn=None, rfid_id=None, code=0):
        now=dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if eventStr[0:14]=="BOX: FAIL OPEN":
            res=self.cursor.execute("""INSERT INTO logbox
            (tm, latitude, longitude, box_id, event, rfid_id, mode, code)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s);
            """, (now, self.latitude, self.longitude, self.boxId, eventStr, rfid_id, self.mode, -1))            
        elif eventStr[0:3]=="DEC":
            res=self.cursor.execute("""INSERT INTO logbox
            (tm, latitude, longitude, box_id, event, rfid_id, mode, drug_ndc,
            equipt_upn, code)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
            """,(now, self.latitude, self.longitude, self.boxId, eventStr, self.lastRFID,
            self.mode, drug_ndc, equipt_upn, code))
        elif not drug_ndc and not equipt_upn and not rfid_id:
            res=self.cursor.execute("""INSERT INTO logbox
            (tm, latitude, longitude, box_id, event, rfid_id)
            VALUES (%s,%s,%s,%s,%s,%s);
            """, (now, self.latitude, self.longitude, self.boxId, eventStr, self.lastRFID))            
        self.cnx.commit()

    def tryLogin(self, user, pswd):
        if self.isAdmin1==True:
            self.__connect()
            self.cursor.execute("""SELECT data FROM other
            WHERE rfid_id=%s LIMIT 1;""",(self.lastRFID))
            cstr=[i[0] for i in self.cursor][0]
            c=encrypt.crypt()
            a,s,b=cstr.split(':')
            ok1=c.checkSha2_512(pswd, a+':'+s)
            if ok1:
                ok2=c.checkSha2_512(user, b+':'+s)
                if ok2:
                    self.__complete()
                    return True
        self.__close()
        return False

        ###########################################################
    def setDegrees(self, lat, longi, reset=False):
        """Call ONCE with new lat * long given after creating
        medboxDB object IF lat / long given as False in constructor
        """########################################################
        r=True
        self.__connect()
        self.cursor.execute("""SELECT latitude, longitude FROM box WHERE id=%s
                            LIMIT 1;""",(self.boxId))
        curLat=False
        curLong=False
        for i in self.cursor:
            curLat=i[0]
            curLong=i[1]
        if (curLat and curLong) and not reset:
            global DEV_MODE
            if DEV_MODE:
                print("lat:"+curLat+";long:"+curLong)
            lat=curLat
            long=curLong
            res1=self.cursor.execute("""UPDATE box SET latitude=%s WHERE id=%s;
    """,(lat, self.boxId))
            self.cursor.__complete()
            self.cursor.__connect()
            res2=self.cursor.execute("""UPDATE box SET longitude=%s WHERE id=%s;
    """,(long, self.boxId))
            self.cursor.__complete()
            r=res1 and res1==res2
        if not self.latitude:
            self.latitude=lat
        if not self.longitude:
            self.longitude=long
        self.longCenter=longi
        self.latCenter=lat
        metersInMile=0.000621371
        m1=111131.92
        m2=-559.82
        m3=1.178
        m4=-0.0023;
        p1=111412.84;
        p2=-93.5;
        p3=0.118;
        self.latDegInSM=(m1+(m2*math.cos(2*lat))+(m3*math.cos(4*lat))+(m4+math.cos(6*lat)))*metersInMile
        self.longDegInSM=((p1*math.cos(lat))+(p2*math.cos(3*lat))+(p3*math.cos(5*lat)))*metersInMile
        return r



    ###############################################################    
    ################ functions affecting all modes ################
    ###############################################################

    def checkRFID(self,rfidIn):
        """Arg:     rfidIn=string from RFID to check
        returns:    a dict like {int(rfid.id):str(worker.name)} if rfidIn found
                    and has proper auth, else False
        """########################################################
        c=encrypt.crypt()
        self.__connect()
        self.cursor.execute("SELECT data FROM rfid;")
        hashStr=c.checkSha2_512(rfidIn, self.cursor)
        if hashStr:
            self.cursor.execute("""SELECT r.id, w.name, r.auth
            FROM rfid AS r JOIN worker AS w ON r.worker_id=w.id
            WHERE r.data=%s LIMIT 1""",(hashStr))
            for i in self.cursor:
                if i[2] and i[2]>0 and self.mode==1:
                    self.lastRFID=i[0]
                    self.log("BOX: SUCESS RFID VERIFIED")
                    self.openAuth=True
                    self.__complete()
                    if i[2]==2:
                        self.isAdmin1=True
                    return {int(i[0]):i[1]}
                elif self.mode==1:# && auth < 1
                    self.log("BOX: FAIL RFID VERIFY BAD AUTH", None, None, i[0])
                    self.__complete()
                    self.openAuth=False
                    return False
                elif self.mode==0 and (i[2]==0 or i[2]==2):
                    if i[2]==0:
                        return {int(i[0]):i[1]}
                    else:
                        self.isStocker=True
                        #TODO!!!!!!!!!!!!!!!!!!!!!!!!!
                        #if still needs filled...
                else:#fail secure
                    self.log("BOX: FAIL RFID VERIFY", None, None, i[0])
                    self.__complete()
                    self.openAuth=False
                    return False
        self.log("BOX: FAIL RFID VERIFY UNKNOWN AUTH "+rfidIn)#not found
        self.__complete()
        self.openAuth=False
        return False

        ###########################################################
    def doubleCheck(self, rfid1, rfid2):
        """Args: 2 rfid strings
        return bool if both passed auth for mode
        """########################################################
        a=self.checkRFID(rfid1)
        b=self.checkRFID(rfid2)
        return (a and b)
    
        ###########################################################
    def boxClosed(self, mode=1):
        """Use: call when box closed.
        Opt arg: mode to go to. Default 1, active.
            Options -1 security alert, 0 inactive/restock, 2 admin
        return bool success
        """########################################################
        self.__connect()
        self.log("BOX: CLOSED")
        self.open=False
        self.__connect()
        res=self.cursor.execute("UPDATE box SET open=0;")
        self.__complete()
        res2=1
        if not isAdmin2:
            self.openAuth=False
            self.numReqstByBin={}
            self.isAdmin1=False
            if mode != self.mode:
                self.mode=mode
                self.__connect()
                res2=self.cursor.execute("UPDATE box SET mode=%s", (self.mode))
                self.__complete()
            numReqstByBin={}
        return True if res and res2 else False
        
        ###########################################################        
    def checkMode(self, expected=1):
        """Use: call regularly to check mode for security
        Optional arg: expected mode, default 1 (active).
        Also accepts -1(security alert) or 0(inactive/restock)
        returns: bool indicating if mode matched excepted.
        """########################################################
        if self.mode !=expected:
            return False
        hrAgo=dt.datetime.now()-dt.timedelta(hours=1)
        self.__connect()
        self.cursor.execute("""SELECT COUNT(id) AS warning_count
        FROM logbox WHERE code=-1 AND tm>%s;
        """,(hrAgo.strftime('%Y-%m-%d %H:%M:%S')))
        warnings=[i for i in self.cursor][0][0]
        global WARNING_TOLERANCE
        if warnings > WARNING_TOLERANCE:
            self.mode=-1
            self.cursor.execute("UPDATE box SET mode=%s", (self.mode))
            self.__complete()
        if self.mode !=expected:
            return False
        return True

        ###########################################################
    def checkInRadius(self, newLat, newLong):
        """use: regularly update latitude with info from rfid and
            check if in approved range
        returns:    1=in range
                    0=OUT OF RANGE UNDER 1/4 MILE - warning
                   -1=security alert
        """########################################################
        self.latitude=newLat
        self.longitude=newLong
        latRange=self.latCenter*self.latDegInSM
        longRange=self.longCenter*self.longDegInSM
        r=1
        if newLat > self.latCenter+latRange or newLat < self.latCenter-latRange:
            self.__connect()
            if newLat-(self.latCenter+latRange) > self.latDegInSM/4 or (self.latCenter+latRange)-newLat > self.latDegInSM/4:
                self.mode=-1
                self.cursor.execute("UPDATE box SET mode=%s", (self.mode))
                self.__complete()
                self.__connect()
                self.log("ALERT: BOX OUT OF RANGE OVER 1/4 MILE", None, None, None, -1)
                self.complete()
                self.authOpen=False
                self.isAdmin1=False
                self.isAdmin2=False
                return -1
            else:
                self.log("WARNING: BOX OUT OF RANGE UNDER 1/4 MILE", None, None, None, -1)
                self.authOpen=False
                r=0
        if newLong > self.longCenter+longRange or newLong < self.longCenter-longRange:
            self.__connect()
            if newLong-(self.longCenter+longRange) > self.longDegInSM/4 or (self.longCenter+longRange)-newLong > self.longDegInSM/4:
                self.mode=-1
                self.cursor.execute("UPDATE box SET mode=%s", (self.mode))
                self.__complete()
                self.__connect()
                self.log("ALERT: BOX OUT OF RANGE OVER 1/4 MILE", None, None, None, -1)
                self.complete()
                self.authOpen=False
                self.isAdmin1=False
                self.isAdmin2=False
                return -1
            else:
                self.log("WARNING: BOX OUT OF RANGE UNDER 1/4 MILE", None, None, None, -1)
                self.authOpen=False
                return 0
        return r

        ###########################################################
    def changeMode(self, mode):
        """Use: by admin to change box mode from loged in panel
        or by stocking worker if changing from inactive to active only
        Returns:   -1=security alert,
                    1=success
        """########################################################
        if self.isAdmin2 and self.isAdmin1:
            self.nextMode=mode
            self.__connect()
            self.cursor.execute("UPDATE box SET mode=%s", (self.mode))
            self.__complete()
            self.__connect()
            self.log("MODE: CHANGE TO "+str(self.mode))
            return 1
        elif isStocker and self.mode==0 and mode==1:
            self.__connect()
            self.cursor.execute("UPDATE box SET mode=%s", (self.mode))
            self.__complete()
            self.log("MODE: CHANGE TO "+str(self.mode))
            return 1            
        else:
            self.mode=-1
            self.__connect()
            self.cursor.execute("UPDATE box SET mode=%s", (self.mode))
            self.__complete()
            self.__connect()
            self.log("ALERT: UNAUTHORIZED MODE CHANGE ATTEMPT", None, None, None, -1)
            return -1
        
        ###########################################################
    def updateQty(self, pos, qty):
        """Use: After determing user has auth - no checking in this
        Args: int bin pos, int new qty
        returns bool success
        """########################################################
        try:
            self.__connect()
            self.cursor.execute("""
            SELECT IF(e.max_count, e.max_count, d.max_count) AS max_count
            FROM bin AS b LEFT JOIN drug AS d ON b.drug_ndc=d.ndc
            LEFT JOIN equipt AS e ON e.upn=b.equipt_upn
            WHERE pos=%s AND box_id=%s;
            """,(int(qty), int(pos), self.boxId))
            maxNum=[i[0] for i in self.cursor][0]
            if qty <= maxNum:
                res=self.cursor.execute("""UPDATE bin SET count=%s
                WHERE pos=%s AND box_id=%s;
                """,(int(qty), int(pos), self.boxId))
                if res and res>0:
                    return True                
        except:
            pass
        return False
                                

    ###############################################################
    ############# functions for mode -1= alert status #############            
    ###############################################################
        
    def logAlert(alert="ALERT: STATUS UPDATE"):
        """Use: call on time delay to update location in logs if on alert status
        Optional arg-a string for log message"""
        if self.mode==-1:
            self.__connect()
            self.log(alert, None, None, None, -1)
            self.__complete()
            

    ###############################################################        
    ############# functions for mode 0 = inactive/restock #########
    ###############################################################

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!TODO!!!!!!!!!!!!!!!!!!!!!!!!!
            
    def getKitNeeds(self,kitName):
        #self.kitNeeds={}
        #stores {int binPos:list item props}
        #where list item props =[type('drug'|'equipt'),itemName
        #(for 'drug' in format 'proprietaryName : genName'), int qty ]
        #if item type == 'drug' appends fields:
        #[route (ie 'SUBCUTANEOUS'), dosage (ie '40 mg/ml, .005 mg/ml')]
        global BIN_COUNT
        """SELECT * FROM kit AS k
LEFT JOIN drug AS d ON k.drug_ndc=d.ndc
LEFT JOIN equipt AS e ON e.upn=k.equipt_upn
ORDER BY score DESC LIMIT %s;"""
        pass

    def insertItems(self, binPos, qty, drug_ndc, equipt_upn=None):
        pass

    def checkFull(self):
        pass

    ###############################################################
    ############# functions for mode 1 = active operation #########
    ###############################################################

    ###############################################################
    def getStock(self):
        """returns:
        dict such as {int binId:list of item properties}
        where list of item properties for all items includes:
        [
            type('drug'|'equipt'),
            itemName (for 'drug' in format 'proprietaryName : genName'),
            int count in stock
        ]
        if item type == 'drug' list of item properties appends fields:
        [
            route adminsitered (ie 'SUBCUTANEOUS'),
            dosage (ie '40 mg/ml, .005 mg/ml')
        ]
        """########################################################
        self.__connect()
        self.cursor.execute("""SELECT b.id,
        IF(name IS NULL, 'drug', 'equipt') AS type,
        IF(name IS NULL, CONCAT(brand_name, ' : ', gen_name), name) AS name,
        count, route, dosage
        FROM bin AS b
        LEFT JOIN drug AS d on b.drug_ndc=d.ndc
        LEFT JOIN equipt AS e on e.upn=b.equipt_upn
        WHERE box_id = %s;""", self.boxId)
        r={}
        for i in self.cursor:
            binId=i[0]
            tmp=[]
            for j in range(1,len(i)):
                if i[j]!=None:
                    tmp.append(i[j])
            r[binId]=tmp
        self.__complete()
        return r

        ###########################################################                  
    def getEmptyBins(self, stock):
        """arg: dict such as {int binId:list of item properties}
                as returned by self.getStock()
        returns:
        dict off all bins whose item count ==0,
        such as {int binId:list of item properties}
        where list of item properties for all items includes:
        [
            type('drug'|'equipt'),
            itemName (for 'drug' in format 'proprietaryName : genName'),
            int count in stock
        ]
        if item type == 'drug' list of item properties appends fields:
        [
            route adminsitered (ie 'SUBCUTANEOUS'),
            dosage (ie '40 mg/ml, .005 mg/ml')
        ]
        """########################################################
        return {k:stock[k] for k in stock.keys() if stock[k][2]==0}

        ###########################################################
    def isEmpty(self, stock):
        """arg: dict such as {int binId:list of item properties}
                as returned by self.getStock()
        returns: bool isEmpty
        """########################################################
        return [k for k in stock.keys() if stock[k][2]==0]==[k for k in stock.keys()]
    

        ###########################################################
    def activeBoxOpened(self, numReqstByBin):
        """use in mode 1 active
        arg: a dict {int binPos:int number requested from bin}
        """########################################################
        self.__connect()
        self.numReqstByBin=numReqstByBin
        self.log("BOX: OPENED")
        self.open=True
        self.__connect()
        res=self.cursor.execute("UPDATE box SET open=1;")
        self.__complete()
        #security alert if bin opened while box not auth'd to be open
        self.__connect()
        if self.mode<1:
            self.mode=-1
            self.cursor.execute("UPDATE box SET mode=%s", (self.mode))
            self.__complete()
            self.__connect()
            self.log("ALERT: BOX OPEN WHILE NOT IN ACTIVE MODE", None, none, None, -1)
        self.__connect()
        if not self.openAuth:
            self.mode=-1
            self.cursor.execute("UPDATE box SET mode=%s", (self.mode))
            self.__complete()
            self.__connect()
            self.log("ALERT: BOX OPEN WHILE NOT AUTHORIZED", None, none, None, -1)
        self.__complete()


    
        ###########################################################
    def openBinActive(self,pos, subtract=1):
        """Use: call openBinActive when register bin opening
        Arg: int pos of bin in box, optional int to subtract default 1
        return:-1=SECURITY WARNING function called while not in active mode or authorized to openAuth
                0=ERROR decrementing
                1=SUCCESS decrementing, CONTINUE
                2=SUCCESS decrementing, END - box now empty
                3=SUCCESS  decrementing, CONTINUE, and THERE'S A SECOND
                    RETURN VALUE - NUMBER IN BIN (AFTER USER REMOVED THEIRS)
                    TO VERIFY WITH USER ie
                    code, numLeftInBin = db.openBinActive(1)         
        """########################################################
        self.__connect()
        #security alert if bin opened while box not auth'd to be open
        if self.mode < 1:
            self.mode=-1
            self.cursor.execute("UPDATE box SET mode=%s", (self.mode))
            self.__complete()
            self.__connect()
            self.log("ALERT: BIN OPEN TO TAKE ITEM NOT ACTIVE MODE",None,None,None,-1)
        self.__connect()
        if not self.openAuth:
            self.mode=-1
            self.cursor.execute("UPDATE box SET mode=%s", (self.mode))
            self.__complete()
            self.__connect()
            self.log("ALERT: BIN OPEN WHILE NOT AUTHORIZED",None,None,None,-1)
        if not self.open:
            self.mode=-1
            self.cursor.execute("UPDATE box SET mode=%s", (self.mode))
            self.__complete()
            self.__connect()
            self.log("ALERT: BIN OPEN WHILE BOX REGISTERED CLOSED",None,None,None,-1)
        #security warning if unrequested bin opened or bin opened more then once on auth
        try:
            num=self.numReqstByBin[pos]
            if num >0:
                subtract=num
            else:
                self.__connect()
                self.log("DEC WARNING: BIN "+str(pos)+" OPENED MULT TIMES",None,None,None,-1)
        except:
            self.__connect()
            self.log("DEC WARNING: UNREQUESTED BIN "+str(pos)+" OPENED",None,None,None,-1)
            
        try:
            self.__complete()
            self.__connect()
        except:
            pass
        #record changes:
        self.verifyByBin[pos]=True
        self.cursor.execute("""SELECT count, drug_ndc, equipt_upn FROM bin
        WHERE pos=%s AND box_id=%s LIMIT 1;""",(pos, self.boxId))
        res=[i for i in self.cursor][0]
        lastQty=res[0]
        if lastQty<1:
            self.log("DEC ERROR: OUT OF ITEM", res[1], res[2], None, 1)
            self.__complete()
            return 0 if self.mode==1 and self.openAuth else -1
        if lastQty-subtract<0:
            self.log("DEC ERROR: REDUCED REQEST "+str(subtract)+
                     " TO AVAIL "+str(lastQty), res[1], res[2], None, 1)
            subtract=lastQty
            self.__connect()
        rowsChanged=self.cursor.execute("""UPDATE bin SET count=%s
        WHERE pos=%s AND box_id=%s;""",(lastQty-subtract, pos, self.boxId))
        if not rowsChanged:
            self.log("DEC ERROR: UNSPEC", res[1], res[2], None, 1)
            self.__complete()
            return 0 if self.mode==1 and self.openAuth else -1
        self.log("DEC SUCCESS", res[1], res[2])
        if lastQty == 1:
            stock=self.getStock()
            empty=self.getEmptyBins(stock)
            if len(stock)==len(empty):#all bins now empty
                self.mode=0
                try:
                    self.__connect()
                except:
                    pass
                self.cursor.execute("UPDATE box SET mode=%s", (self.mode))
                self.__complete()
                self.__connect()
                self.log("BOX: EMPTY")
                self.__complete()
                if self.mode>0 and self.openAuth:
                    if self.verifyByBin[pos]:
                        return 3, lastQty-subtract
                    return 2
                else:
                    return -1
        try:
                self.__complete()
        except:
            pass
        return 1 if self.mode==1 and self.openAuth else -1

        ###########################################################
    def getBinQty(self, pos):
        """Arg: int pos of bin to check
        Return int quantity box sees in bin
        """########################################################
        self.__connect()
        self.cursor.execute("SELECT count FROM bin WHERE pos=%s",(pos))
        qty= [i[0] for i in self.cursor][0]
        self.__complete()
        return qty

    ###############################################################
    ############# functions for mode 2 = admin tasks ##############
    ###############################################################

        ###########################################################
    def loginAdmin(self,user,pswd):
        """Use: call after user provides 2nd step auth offered on rfid swipe by admin
        Returns:   -1=security alert,
                    0=Fail
                    1=success
        """########################################################
        self.__connect()
        if self.isAdmin1==True:
            if(self.tryLogin(user,pswd)):
                self.isAdmin2==True
                self.lastMode=self.mode
                self.mode=2
                self.__connect()
                self.cursor.execute("UPDATE box SET mode=%s", (self.mode))
                self.__complete()
                return 1
            else:
                self.log("WARNING: BAD LOGIN ATTEMPT", None, None, None, -1)
                if not self.checkMode(2):
                    self.log("ALERT: BAD LOGIN ATTEMPTS EXCEEDED", None, None, None, -1)
                    return -1
                return 0
        self.mode=-1
        self.log("ALERT: UNAUTHORIZED LOGIN ATTEMPT", None, None, None, -1)
        self.__connect()
        self.cursor.execute("UPDATE box SET mode=%s", (self.mode))
        self.__complete()
        return -1

        ###########################################################
    def logout(self, mode=100):
        """Use: logout admin.
        Optional Arg: mode, provide if not already called in set mode,
        or will be set to last mode before admin mode
        """########################################################
        self.mode=self.nextMode if mode==100 else mode
        self.openAuth=False
        self.isAdmin1=False
        self.isAdmin2=False
        self.numReqstByBin={}
        self.verifyByBin={}

        ###########################################################
    def changeLogin(user, pswd):
        """Use: by fully loged in admin to change credentials to
            username & password already passing requirments
        returns:  -1=security alert
                   0=warning, no changes made
                   1=success, changed
                   2=failure (like dup info used by other employee)
        """########################################################
        if self.isAdmin2==True and self.isAdmin1==True:
            if self.mode==2:
                c=encrypt.crypt()
                str1=c.getSha2_512(pswd)
                str2=c.getSha2_512(user, str1.split(':')[1])
                creds=str1+":"+str2.split(':')[0]
                self.__connect()
                res=self.cursor.execute("""UPDATE other SET data=%s WHERE rfid_id=%s;
                """, (creds, self.lastRFID))
                self.__complete()
                if res:
                    self.__connect()
                    self.log("ADMIN: CRED CHANGED SUCESS")
                    return 1
                self.__connect()
                self.log("ADMIN: CRED CHANGED FAILED", None, None, None, 1)
                return 2
            self.__connect()
            self.log("WARNING: ADMIN CRED CHANGE REQUEST IN WRONG MODE", None, None, None, -1)
            return 0
        self.__connect()
        self.log("ALERT: UNAUTHORIZED ADMIN CRED CHANGE ATTEMPT", None, None, None, -1)
        self.mode=-1
        self.__connect()
        self.cursor.execute("UPDATE box SET mode=%s", (self.mode))
        self.__complete()
        return -1

        
    def changeWarningTolerance(self, numWarningsAllowed):
        """Use: by admin RFID login, in admin mode
        Returns:   -1=security alert,
                    0=not admin mode/no change
                    1=success
        """
        if self.isAdmin2 and self.isAdmin1:
            if self.mode==2:
                global WARNING_TOLERANCE
                WARNING_TOLERANCE=numWarningsAllowed
                self.log("WARNING_TOLERANCE SET: TO "+str(WARNING_TOLERANCE))
                return 1
            self.log("WARNING: WARNING_TOLERANCE CHANGE ATTEMPT IN WRONG MODE", None, None, None, -1)
            return 0
        self.log("ALERT: UNAUTHORIZED WARNING_TOLERANCE CHANGE ATTEMPT", None, None, None, -1)
        self.mode=-1
        self.__connect()
        self.cursor.execute("UPDATE box SET mode=%s", (self.mode))
        self.__complete()        
        return -1
            

    def changeMileRadius(self, miles):
        """Use: by admin RFID login, in admin mode
        Returns:   -1=security alert,
                    0=not admin mode/no change
                    1=success
        """
        self.__connect()
        if self.isAdmin2 and self.isAdmin1:
            if self.mode==2:
                self.mileRadius=miles
                self.log("RADIUS SET: TO "+str(self.mileRadius))
                return 1
            self.log("WARNING: RADIUS CHANGE ATTEMPT IN WRONG MODE", None, None, None, -1)
            return 0
        else:
            self.log("ALERT: UNAUTHORIZED RADIUS CHANGE ATTEMPT", None, None, None, -1)
            self.mode=-1
            self.__connect()
            self.cursor.execute("UPDATE box SET mode=%s", (self.mode))
            self.__complete() 
            return -1

    def getBoxLog(self):
        """Use: by admin RFID login, in admin mode
        Returns:   -1=security alert,
                    0=not admin mode/fail
                    log = list of tuples of data from logs as:
                    [(int id, int code, str event, datetime tm, int rfid_id,
                    int drug_ndc, str equipt_upn, int mode, float latitude,
                    float longitude),(...)]
        """
        if self.isAdmin2==True and self.isAdmin1==True:
            if self.mode==2:
                self.__connect()
                self.cursor.execute("""SELECT id, code, event, tm, rfid_id, drug_ndc,
                equipt_upn, mode, latitude, longitude FROM logbox WHERE box_id=%s;
                """, (self.boxId))
                logs=[i for i in self.cursor]
                self.__complete()
                self.log("LOGS: REVIEWED")
                return log
            self.log("WARNING: ATTEMPT TO GET LOGS IN WRONG MODE", None, None, None, -1)
            return 0
        else:
            self.log("ALERT: UNAUTHORIZED ATTEMPT TO GET LOGS", None, None, None, -1)
            self.mode=-1
            self.cursor.execute("UPDATE box SET mode=%s", (self.mode))
            self.__complete()
            return -1

    #todo - check auth first

    def assignBoxId(self, boxId):
        self.boxId=boxId
        self.__connect()
        self.cursor.execute("SELECT id FROM box LIMIT 1;")
        currentId=int([i[0] for i in self.cursor][0])
        if currentId:
            if currentId==boxId:
                self.boxId=boxId
                return 1
            else:
                res=self.cursor.execute("UPDATE box SET id=%s;",(boxId))
                self.__complete()
                if res:
                    self.boxId=boxId
                    return 1
                return 0
        res=self.cursor.execute("""INSERT INTO box
    (id, mode, open, latitude, longitude) VALUES (%s,%s,%s,%s,%s);
    """,(boxId, self.mode, self.open, self.latitude, self.longitude))
        self.__complete()
        if res:
            self.boxId=boxId
            return 1
        return 0
        

    def changeCenterPoint(self, lat, longi):
        res=self.setDegrees(lat, longi, True)


    #TODO!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        
    def addWorker(self, name, employerId, employeeId):
        pass
        
    def addRFID(self, num):
        pass
        
    def assignWorkerRFID(self, workerId):
        pass

    def changeAuth(self, num, auth):
        pass

    def resetBox(self):
        self.__init__(self.latitude, self.longitude)
    


            
################################################################################


