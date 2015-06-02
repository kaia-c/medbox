#!/usr/bin/env python3

import encrypt
import sys
import pymysql
import datetime as dt
import math
import dbReset
import gpsCalc

WARNING_TOLERANCE=float('inf')
                    #=number of security warnings allowed in 1 hr.
                    #note - errors instantly change box mode, warnings
                    #can be set by admin to track lower priority concern accumulation
                    #set to float('inf') to not track warnings
DEV_MODE=True
BIN_COUNT=9
USE_2_LEVEL_AUTH=False


class DbMedbox():
        ###########################################################
    def __init__(self, lati, longi):
        """lati & longi values can be set to False, but need supplied
        before box put in active mode. They are the center point of range box
        is authorized to roam
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
        self.openAuth=False #True granted on checkInRFID(rfid) success
        self.lastRFID=None  #self.lastRFID stores rfid.id key from
                            #last verfied RFID after first swipe.
        self.isAdmin1=False #True on verified rfid as admin
        self.isAdmin2=False #True on usernm/passwd verification by admin
        global USE_2_LEVEL_AUTH
        self.useAdmin2=USE_2_LEVEL_AUTH
        self.isStocker=False#True on RFID swipe by stocker
        self.numReqstByBin={}#stores {int binPos:int user requested from bin}
        #stores {int binPos:bool verify count on next open?}
        global BIN_COUNT
        self.verifyByBin={i:False for i in range(BIN_COUNT)}
        self.mileRadius=1   #miles allowed to roam
        self.latCenter=lati #lat at center auth radius
        self.longCenter=longi
        self.latitude=None
        self.longitude=None
        self.kitNeeds={}    #stores {int binPos:list item props}
                            #where list item props =
                                #[type('drug'|'equipt'),
                                # itemName (for 'drug' in format
                                #'proprietaryName : genName'), int qty ]
                            #if item type == 'drug' appends fields:
                                #[route (ie 'SUBCUTANEOUS'),
                                # dosage (ie '40 mg/ml, .005 mg/ml')]
        self.setBoxId()
        if not lati or not longi:
            self.setCenterLoc(40,-105)
        else:
            self.setCenterLoc(lati, longi, True)
        self.checkInRange()
        

        
    ###############################################################    
    #################    private-ish functions  ###################
    ###############################################################
    def __connect(self):
        try:
            self.cnx=pymysql.connect(user="root", passwd="RRCCpi2DC", 
            host="127.0.0.1", db="medbox", port=3306)
        except:
            self.cnx=pymysql.connect(user="root", host="127.0.0.1",
                                 db="medbox", port=3306)
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
            c=encrypt.Crypt()
            a,s,b=cstr.split(':')
            ok1=c.checkSha2_512(pswd, a+':'+s)
            if ok1:
                ok2=c.checkSha2_512(user, b+':'+s)
                if ok2:
                    self.__complete()
                    return True
        self.__close()
        return False




    ###############################################################    
    ################ functions affecting all modes ################
    ###############################################################

    ###############################################################
    def checkInRFID(self,rfidIn):
        """
        use: FIRST after getting an RFID to set db status
        arg:     rfidIn=string from RFID to check
        returns:    bool auth for if mode allows open box for auth level
        """########################################################
        c=encrypt.Crypt()
        self.__connect()
        self.cursor.execute("SELECT data FROM rfid;")
        hashStr=c.checkSha2_512(rfidIn, self.cursor)
        if hashStr:
            self.cursor.execute("""SELECT id, auth
            FROM rfid WHERE data=%s LIMIT 1""",(hashStr))
            for i in self.cursor:
                if i[1] and i[1]>0 and self.mode==1:
                    self.lastRFID=i[0]
                    self.log("BOX: SUCCESS RFID VERIFIED", None, None, i[0])
                    self.openAuth=True
                    self.__complete()
                    if i[1]==2:
                        self.isAdmin1=True
                    return True
                elif self.mode==1:# && auth < 1
                    self.log("BOX: FAIL RFID VERIFY BAD AUTH", None, None, i[0])
                    self.__complete()
                    self.openAuth=False
                    return False
                elif self.mode==0 and (i[1]==0 or i[1]==2):
                    if i[1]==0:
                        self.isStocker=True
                        self.openAuth=True
                        self.log("BOX: SUCCESS RFID VERIFIED", None, None, i[0])
                        self.__complete()
                        return True
                    else: #i[1]==2, admin
                        self.isStocker=False
                        self.isAdmin1=True
                        self.openAuth=True
                        self.log("BOX: SUCCESS RFID VERIFIED", None, None, i[0])
                        self.__complete()
                        return True
                elif self.mode==0:#and not admin or stocker
                        self.isStocker=False
                        self.isAdmin1=False
                        self.openAuth=False
                        self.log("BOX: FAIL RFID VERIFY BAD AUTH", None, None, i[0])
                        self.__complete()
                        return False
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
        a=self.checkInRFID(rfid1)
        b=self.checkInRFID(rfid2)
        return (a and b)

        ###########################################################
    def getAuthByRFID(self,rfidIn=None):
        """Optional arg: str(rfidIn)| default=last rfid used with checkInRFID
        returns:    int auth for assoc with the rfid if found | False
        """########################################################
        r=False
        if not rfidIn:
            rfidIn=self.lastRFID
            if self.isAdmin1:
                r=2
            elif self.openAuth:
                r=self.mode
        if r:
            return r
        self.__connect()
        self.cursor.execute("SELECT data FROM rfid;")
        c=encrypt.Crypt()
        hashStr=c.checkSha2_512(rfidIn, self.cursor)
        if hashStr:
            self.cursor.execute("""SELECT auth
            FROM rfid WHERE data=%s LIMIT 1""",(hashStr))
            for i in self.cursor:
                r=i[0]
        self.__complete()
        return r

        ###########################################################
    def getNameByRfid(self,rfidIn=None):
        """Optional arg: str(rfidIn)| default=last rfid used with checkInRFID
        returns:    str workerName if name assoc with rfid found | False
        """########################################################
        c=encrypt.crypt()
        r=False
        if not rfidIn:
            rfidIn=self.lastRFID
        self.__connect()
        self.cursor.execute("SELECT data FROM rfid;")
        hashStr=c.checkSha2_512(rfidIn, self.cursor)
        if hashStr:
            self.cursor.execute("""SELECT w.name
            FROM rfid AS r JOIN worker AS w ON r.worker_id=w.id
            WHERE r.data=%s LIMIT 1""",(hashStr))
            for i in self.cursor:
                r=i[0]
        self.__complete()
        return r
        ###########################################################
    
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
        if not isAdmin2 and self.useAdmin2:
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
    def checkInRange(self, newLat=False, newLong=False):
        """use: regularly update latitude with info from rfid and
            check if in approved range
        returns:    1=in range
                    0=OUT OF RANGE UNDER 1/4 MILE - warning
                   -1=security alert
        TODO: it's still checking in a square. Make a circle.
        """########################################################
        gps=gpsCalc.GPS()
        if newLat and newLong:
            self.latitude=newLat
            self.longitude=newLong
        else:
            self.latitude, self.longitude=gps.getLoc()
        r=1
        dist=gps.getDistance(self.latitude, self.longitude, self.latCenter, self.longCenter)
        if dist>self.mileRadius:
            self.__connect()
            if dist>self.mileRadius+0.25:
                self.mode=-1
                self.cursor.execute("UPDATE box SET mode=%s", (self.mode))
                self.__complete()
                self.__connect()
                self.log("ALERT: BOX OUT OF RANGE OVER 1/4 MILE", None, None, None, -1)
                self.__complete()
                self.authOpen=False
                self.isAdmin1=False
                self.isAdmin2=False
                return -1
            else:
                self.log("WARNING: BOX OUT OF RANGE UNDER 1/4 MILE", None, None, None, -1)
                self.authOpen=False
                r=0
        return r

        ###########################################################
    def setCenterLoc(self, lat=False, longi=False):
        """Call to set/rest center point for cicle box allowed to roam
        Opt args: +- 90 decimal degrees latitude, +- 180 decimal degrees longitude
        Uses current location points if not provided.
        return: bool success
        """########################################################
        r=True
        if not lat or not longi:
            gps=gpsCalc.GPS()
            lat, longi=gps.getLoc()
        self.__connect()
        res1=self.cursor.execute("""UPDATE box SET latitude=%s WHERE id=%s;
    """,(lat, self.boxId))
        self.__complete()
        self.__connect()
        res2=self.cursor.execute("""UPDATE box SET longitude=%s WHERE id=%s;
    """,(longi, self.boxId))
        self.__complete()
        r=res1 and res1==res2
        self.longCenter=longi
        self.latCenter=lat
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
        Optional arg-a string for log message
        """########################################################
        if self.mode==-1:
            self.__connect()
            self.log(alert, None, None, None, -1)
            self.__complete()
            

    ###############################################################        
    ############# functions for mode 0 = inactive/restock #########
    ###############################################################

        ###########################################################
    def getKitNeeds(self,kitName):
        """use: call once on the start of refill/inactive mode
        arg: string kit name (test: "ANAPHYLAXIS")
        return: {int binPos:list item props}
        where list item props =[prod_id, prod_name, drug_detail, qty]
        """########################################################        
        global BIN_COUNT
        self.__connect()
        self.cursor.execute("""SELECT
        if(d.ndc IS NOT NULL,CONCAT("ndc_",d.ndc),CONCAT("upn_",e.upn)) AS prod_id,
        if(d.ndc IS NOT NULL, CONCAT(gen_name, ":", brand_name), e.name) AS prod_name,
        if(d.ndc IS NOT NULL, CONCAT(dosage, ":", route), "N/A") AS drug_detail,
        if(d.ndc IS NOT NULL, d.max_count, e.max_count) AS QTY
        FROM kit AS k
        LEFT JOIN drug AS d ON k.drug_ndc=d.ndc
        LEFT JOIN equipt AS e ON e.upn=k.equipt_upn
        ORDER BY score DESC LIMIT %s;
        """, (BIN_COUNT))
        p=0
        kit={}
        for i in self.cursor:
            kit[p]=[j for j in i]
            p+=1
        global DEV_MODE
        if DEV_MODE:
            print(kit)
        self.__complete()
        self.kitNeeds=kit
        self.full=False
        return kit

        ###########################################################
    def getUpdatedKitNeeds(self):
        """use: call if needed to update kit needs during refill mode
        return: {int binPos:list item props}
        where list item props =[prod_id, prod_name, drug_detail, qty]
        """########################################################
        return self.kitNeeds

        ###########################################################
    def insertItems(self, binPos, qty=1, drug_ndc=None, equipt_upn=None):
        """inserts a given qty of items where drug_ndc or equipt_upn already
        recorded in db
        Args: int binPos, int qty, either the drug_ndc or the product_upn
        return: bool success
        """########################################################
        ndc=False
        upn=False
        self.__connect()
        if drug_ndc:
            try:
                self.cursor.execute("""SELECT ndc FROM drug WHERE ndc=%s;
        """, (int(drug_ndc)))
                for i in self.cursor:
                    ndc=i[0]
            except:
                pass
        elif equipt_upn:
            self.cursor.execute("""SELECT upn FROM equipt WHERE upn=%s;
        """, (equipt_upn))
            for i in self.cursor:
                upn=i[0]
        res1=False
        res2=False
        if ndc:
            try:
                res1=self.cursor.execute("""UPDATE bin
                SET drug_ndc=%s WHERE pos=%s AND box_id=%s;
                """,(ndc, int(binPos), self.boxId))
                self.__complete()
                try:
                    self.__connect()
                    res2=self.cursor.execute("""UPDATE bin
                    SET count=%s WHERE pos=%s AND box_id=%s;
                    """,(qty, int(binPos), self.boxId))
                    self.__complete()
                except:
                    pass
            except:
                pass
        elif upn:
            try:
                res1=self.cursor.execute("""UPDATE bin
                SET equipt_upn=%s WHERE pos=%s AND box_id=%s;
                """,(upn, int(binPos), self.boxId))
                self.__complete()
                try:
                    self.__connect()
                    res2=self.cursor.execute("""UPDATE bin
                    SET count=%s WHERE pos=%s AND box_id=%s;
                    """,(qty, int(binPos), self.boxId))
                    self.__complete()
                except:
                    pass
            except:
                pass
        try:
            if self.kitNeeds[binPos][3]-qty <=0:
                self.kitNeeds[binPos]=False
            else:
                self.kitNeeds[binPos][3]=self.kitNeeds[binPos][3]-qty
        except:
            pass
        return True if res1 and res2 else False

        ###########################################################
    def insertItemsInKit(self, kit):
        """arg:  a kit as returned by getKitNeeds
        return bool success
        """########################################################
        res=False
        for p, l in kit.items():
            de, de_id=l[0].split("_")
            if de=="ndc":
                res=self.insertItems(p, l[3], de_id)
            else:
                res=self.insertItems(p, l[3], None, de_id)
        return res
            
        ###########################################################
    def checkFull(self):
        """returns bool if all items found in getKitNeeds have since
        been inserted
        """########################################################
        full=True
        for p, l in self.kitNeeds:
            if l:
                full=False
                break
        return full

    ###############################################################
    ############# functions for mode 1 = active operation #########
    ###############################################################

    ###############################################################
    def getStock(self):
        """returns:
        dict such as {int binPos:list of item properties}
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
        self.cursor.execute("""SELECT b.pos,
        IF(name IS NULL, 'drug', 'equipt') AS type,
        IF(name IS NULL,
            IF(brand_name=gen_name,
                brand_name,
                CONCAT(brand_name, ':', gen_name)
            ),
            CONCAT(e.name, ':', e.descript)
        ) AS name
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
    def getNames(self):
        """returns: dict {binPos:'drug_name'|'equipt_name'}
        """########################################################
        self.__connect()
        self.cursor.execute("""SELECT b.pos,
        IF(name IS NULL,
            IF(brand_name=gen_name,
                brand_name,
                CONCAT(brand_name, ':', gen_name)
            ),
            CONCAT(e.name, ':', e.descript)
        ) AS name
        FROM bin AS b
        LEFT JOIN drug AS d on b.drug_ndc=d.ndc
        LEFT JOIN equipt AS e on e.upn=b.equipt_upn
        WHERE box_id = %s;""", self.boxId)
        r={}
        for i in self.cursor:
            r[i[0]]=i[1]
        self.__complete()
        return r

        ###########################################################
    def getCounts(self):
        """returns: dict {binPos:int count of item in bin}
        """########################################################
        self.__connect()
        self.cursor.execute("""SELECT pos, count
        FROM bin WHERE box_id = %s;""", self.boxId)
        r={}
        for i in self.cursor:
            r[i[0]]=i[1]
        self.__complete()
        return r

        ###########################################################
    def getItemIds(self):
        """Return: a dict {binPos: drug_ndc|'equipt_upn'}
        """########################################################
        self.__connect()
        self.cursor.execute("""SELECT b.pos,
        IF(drug_ndc IS NULL, equipt_upn, drug_ndc) AS item_id
        FROM bin
        WHERE box_id = %s;""", self.boxId)
        r={}
        for i in self.cursor:
            r[i[0]]=i[1]
        self.__complete()
        return r

        ###########################################################
    def getBinPosList(self):
        """Return: a list of all binPos's in box
        """########################################################
        self.__connect()
        self.cursor.execute("SELECT b.pos FROM bin WHERE box_id = %s;", self.boxId)
        r=[i[0] for i in self.cursor]
        self.__complete()
        return r
        
        ###########################################################                  
    def getEmptyBins(self, stock):
        """arg: dict such as {int binId:list of item properties}
                as returned by self.getStock()
        return:
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
    def isBoxEmpty(self, stock):
        """arg: dict such as {int binId:list of item properties}
                as returned by self.getStock()
        return: bool isEmpty or -1 on fail
        """########################################################
        try:
            return [k for k in stock.keys() if stock[k][2]==0]==[k for k in stock.keys()]
        except:
            return -1
        ###########################################################
    def getCountInBin(self, binPos):
        """arg: int binPos
        return: bool isEmpty or -1 on fail
        """########################################################
        self.__connect()
        r=-1
        try:
            self.cursor.execute("""SELECT count FROM bin
            WHERE pos=1 AND box_id=1 LIMIT 1;""", (int(binPos), self.boxId))
            for i in self.cursor:
                r=(self.cursor[0] >0)
            self.__complete()
        except:
            pass
        return r
        

        ###########################################################
    def activeBoxOpened(self, numReqstByBin):
        """use: in mode 1 (active) whenever box opened
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
    def loginAdmin(self,user=None,pswd=None):
        """Use: call after user provides 2nd step auth offered on rfid swipe by admin
        Returns:   -1=security alert,
                    0=Fail
                    1=success
        """########################################################
        self.__connect()
        if self.isAdmin1==True:
            global USE_2_LEVEL_AUTH
            if USE_2_LEVEL_AUTH:
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
            else:
                self.mode=2
                self.__connect()
                self.cursor.execute("UPDATE box SET mode=%s", (self.mode))
                self.__complete()
                return 1
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
        if (self.isAdmin2==True or not self.useAdmin2) and self.isAdmin1==True:
            if self.mode==2:
                c=encrypt.Crypt()
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
        if (self.isAdmin2==True or not self.useAdmin2) and self.isAdmin1:
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
        if (self.isAdmin2==True or not self.useAdmin2) and self.isAdmin1:
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
        if (self.isAdmin2==True or not self.useAdmin2) and self.isAdmin1==True:
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
        



    #TODO!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        
    def addWorker(self, name, employerId, employeeId):
        pass
        
    def addRFID(self, num):
        pass
        
    def assignWorkerRFID(self, workerId):
        pass

        ###########################################################
    def changeAuthByRFID(self, rfidIn, auth):
        """args: rfid strings, desired new auth level
         returns bool success
        """########################################################
        res=False
        self.__connect()
        self.cursor.execute("SELECT data FROM rfid;")
        c=encrypt.Crypt()
        hashStr=c.checkSha2_512(rfidIn, self.cursor)
        if hashStr:
            res=self.cursor.execute("""UPDATE rfid
            SET auth=%s WHERE data=%s""",(auth, hashStr))
        self.__complete()
        return res

        ###########################################################
    def resetBox(self):
        ###########################################################
        newDB=dbReset.CreateDB()
        newDB.reset()
        self.__init__(self.latitude, self.longitude)

        ###########################################################    
    def getDumpFile(self):
        """Creates dump.text, a tab deliniated file which can be parsed
        from master db to get box data for its' tables:  logbox and worker.
        Table data seperated blank line
        """########################################################
        self.__connect()
        self.cursor.execute("""SELECT box_id, id AS log_id, tm, latitude, longitude,
        code, event, mode, rfid_id, drug_ndc, equipt_upn
        FROM logbox WHERE box_id=%s;""", (self.boxId))
        with open ("dumpfile.txt", "w") as df:
            for i in self.cursor:
                [df.write(str(i[j])+"\t") for j in range(len(i)-1)]
                df.write(str(i[-1])+"\n")
            df.write("\n")
            self.cursor.execute("""SELECT r.id AS rfid_id, worker_id,
            employee_id, employer_id, name, auth
            FROM rfid AS r JOIN worker AS w ON r.worker_id=w.id;""")
            for i in self.cursor:
                df.write(str(self.boxId)+"\t")
                [df.write(str(i[j])+"\t") for j in range(len(i)-1)]
                df.write(str(i[-1])+"\n")
        self.__complete()

        ###########################################################
    def parseDump(self):
        """TEST FUNCTION: This will be removed,
        it would be located in the master db to parse the dumpfile.txt 
        it receives into list of sql statements to execute
        """########################################################
        with open ("dumpfile.txt", "r") as df:
            file=df.read()
        try:
            lines=file.split('\n')
            fields=[i.split('\t') for i in lines]
        except:
            return False
        table="logbox"
        sql=[]
        for i in fields:
            if len(i[0])> 0:
                sql.append("INSERT INTO "+table+" VALUES ("+",".join(["'"+j+"'" for j in i])+");")
            else:
                table="worker"
        return sql
            
                    
################################################################################
#test=DbMedbox(False, False)
"""
test.mode=1
print("\nMODE="+str(test.mode))
print("medtech rfid="+str(test.checkInRFID('6A004A16C0')))#your str
print("medtech rfid="+str(test.checkInRFID('0F0303723B')))#your str
print("stocker rfid="+str(test.checkInRFID('0F03036E8D')))
print("admin rfid="+str(test.checkInRFID('770096EE82')))
test.mode=0
print("\nMODE="+str(test.mode))
print("medtech rfid="+str(test.checkInRFID('6A004A16C0')))#your str
print("medtech rfid="+str(test.checkInRFID('0F0303723B')))#your str
print("stocker rfid="+str(test.checkInRFID('0F03036E8D')))
print("admin rfid="+str(test.checkInRFID('770096EE82')))
"""


#test.getDumpFile()
#print(test.parseDump())

#print(test.checkInRange())
