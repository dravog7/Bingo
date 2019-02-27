from tornado.websocket import WebSocketHandler
import json
import random

class playerHandler(WebSocketHandler):
    grps={}
    names=[]
    def open(self):
        self.currgrp=""
        self.name=""
        self.board=[] #add 25 for striked out nums

    def on_close(self):
        if(self.currgrp!=""):
            self.exitGrp()
        print(self.name,"exited")
        playerHandler.names.remove(self.name)
    def on_message(self,msg):
        msg=json.loads(msg)
        if(msg['type']=="grp"):
            self.changeGrp(msg['name'])
        elif(msg['type']=="newgrp"):
            self.newGrp(msg['name'])
        elif(msg['type']=="name"):
            self.changeName(msg['name'])
        elif(msg['type']=="checkname"):
            self.checkName(msg['name'])
        elif(msg['type']=="checkgrp"):
            self.checkGrp(msg['name'])
        elif(msg['type']=="listgrp"):
            self.listGrp()
        elif(msg['type']=="start"):
            playerHandler.grps[self.currgrp].startGame(self)
        elif(msg['type']=="setboard"):
            self.setBoard(msg.board)
        elif(msg['type']=="call"):
            if(playerHandler.grps[self.currgrp].callNum(self,msg['num'])):
                self.board[msg['x']][msg['y']]+=25
        elif(msg['type']=="win"):
            self.checkWin()
        elif(msg['type']=="leave"):
            self.exitGrp()
        elif(msg['type']=="self"):
            self.info()
        elif(msg['type']=="listname"):
            self.listName()

    def changeGrp(self,name):
        if(name in playerHandler.grps):
            self.currgrp=name
            if(playerHandler.grps[name].addMe(self)):
                self.write_message(json.dumps({"type":"bill","op":"changeGrp"}))
                return True
        return False
    
    def exitGrp(self):
        if(self in playerHandler.grps[self.currgrp].members):
            playerHandler.grps[self.currgrp].removeMe(self)
            self.currgrp=""
            self.write_message(json.dumps({"type":"bill","op":"exitGrp"}))
        else:
            return False
    
    def newGrp(self,name):
        if not(name in playerHandler.grps):
            grp=group(name,self)
            playerHandler.grps[name]=grp
            self.currgrp=grp.name
            self.write_message(json.dumps({"type":"bill","op":"newGrp"}))
        else:
            return False
    
    def changeName(self,name):
        if not(name in playerHandler.names):
            self.name=name
            playerHandler.names.append(name)
            print("changed name to",name)
            self.write_message(json.dumps({"type":"bill","op":"changeName"}))
        else:
            return False

    def checkName(self,name):
        msg={"type":"checkName","name":name,"result":True}
        if(name in playerHandler.names):
            msg["result"]=False
        self.write_message(json.dumps(msg))

    def checkGrp(self,name):
        msg={"type":"checkGrp","name":name,"result":True}
        if(name in playerHandler.grps):
            msg["result"]=False
        self.write_message(json.dumps(msg))

    def listGrp(self):
        msg={"type":"listGrp","data":list(playerHandler.grps.keys())}
        self.write_message(json.dumps(msg))

    def listName(self):
        msg={"type":"listName","data":list(playerHandler.names)}
        self.write_message(json.dumps(msg))

    def checkWin(self):
        nums=playerHandler.grps[self.currgrp].numberscalled
        for i in range(5):
            for j in range(5):
                currnum=self.board[i][j]-25
                if not((currnum>0)and(currnum in nums)):
                    return False
        playerHandler.grps[self.currgrp].Won(self)

    def setBoard(self,board):
        for i in range(5):
            for j in range(5):
                if((board[i][j]<=0)or(board[i][j]>=26)):
                    return False
        self.board=board
        self.write_message(json.dumps({"type":"bill","op":"setBoard"}))
    
    def info(self):
        msg={"type":"info"}
        msg['currgrp']=self.currgrp
        msg['name']=self.name
        msg['board']=self.board
        self.write_message(json.dumps(msg))

class group:
    max=6
    def __init__(self,name,first):
        self.name=name
        self.members=[first]
        self.toplay=0
        self.numberscalled=[]
        self.winner=""
        self.started=False
    
    def addMe(self,member):
        if(not self.started)and(len(self.members)<group.max)and(not(member in self.members)):
            self.members.append(member)
            return True
        return False
    
    def removeMe(self,member):
        if(member in self.members):
            index=self.members.index(member)
            self.members.remove(member)
            self.broadcast({"type":"leave","name":member.name})
            if(self.toplay==index):
                self.toplayChange(normal=False)

    
    def callNum(self,member,num):
        if (not(num in self.numberscalled))and(self.members.index(member)==self.toplay):
            self.numberscalled.append(num)
            self.broadcast({"type":"call","name":member.name,"num":num})
            self.toplayChange()
            return True
        else:
            member.write({"type":"error"})
        return False

    def toplayChange(self,normal=True):
        if(normal):
            self.toplay=(self.toplay+1)%(len(self.members))
        else:
            self.toplay=(self.toplay)%(len(self.members))
        self.broadcast({"type":"toplay","name":self.members[self.toplay].name})
    
    def startGame(self,member):
        if(self.members[0]==member): #if owner
            self.started=True
            self.broadcast({"type":"start"})
            self.toplay=random.randint(0,len(self.members))-1
            self.toplayChange()

    def broadcast(self,msg):
        for i in self.members:
            i.write_message(json.dumps(msg))
    
    def broadcastGrpChange(self):
        msg={"type":"grpmod"}
        msg['data']=self.__dict__
        msg['data']['members']=[x.name for x in msg['data']['members']]
        self.broadcast(msg)

    def Won(self,member):
        msg={"type":"winner","name":member.name}
        if(member in self.members):
            self.winner=member.name
            self.broadcast(msg)