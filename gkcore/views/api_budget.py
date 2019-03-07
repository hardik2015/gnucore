"""
Copyright (C) 2013, 2014, 2015, 2016 Digital Freedom Foundation
Copyright (C) 2017, 2018 Digital Freedom Foundation & Accion Labs Pvt. Ltd.
  This file is part of GNUKhata:A modular,robust and Free Accounting System.

  GNUKhata is Free Software; you can redistribute it and/or modify
  it under the terms of the GNU Affero General Public License as
  published by the Free Software Foundation; either version 3 of
  the License, or (at your option) any later version.

  GNUKhata is distributed in the hope that it will be useful, but
  WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU Affero General Public License for more details.

  You should have received a copy of the GNU Affero General Public
  License along with GNUKhata (COPYING); if not, write to the
  Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
  Boston, MA  02110-1301  USA59 Temple Place, Suite 330,

  Contributors:
  "Krishnakant Mane" <kk@gmail.com>
   "Karan Kamdar" <kamdar.karan@gmail.com>
   "Prajkta Patkar" <prajkta@riseup.com>
   "Abhijith Balan" <abhijith@dff.org.in>
   "rohan khairnar" <rohankhairnar@gmail.com>
  
  This API is written for budgeting module. With this API budget add,edit,delete,list of budget and budget report calculation can be done.
  This api is related to "BUDGET TABLE".   
  """

from gkcore import eng, enumdict
from gkcore.models.gkdb import invoice, budget, accounts, groupsubgroups, users
from sqlalchemy.sql import select
import json
from sqlalchemy.engine.base import Connection
from sqlalchemy import and_, exc, desc
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_defaults,  view_config
from datetime import datetime,date,timedelta
import jwt
import gkcore
from gkcore.views.api_login import authCheck
from gkcore.views.api_user import getUserRole
from gkcore.models import gkdb
from gkcore.views.api_reports import calculateBalance, calculateBalance2

@view_defaults(route_name='budget')
class api_budget(object):
    def __init__(self,request):
        self.request = Request
        self.request = request
        self.con = Connection
    @view_config(request_method='POST',renderer='json')
    def addBudget(self):
        try:
            token = self.request.headers["gktoken"]
        except:
            return  {"gkstatus":  gkcore.enumdict["UnauthorisedAccess"]}
        authDetails = authCheck(token)
        if authDetails["auth"] == False:
            return  {"gkstatus":  enumdict["UnauthorisedAccess"]}
        else:
            try:
                self.con = eng.connect()
                role = self.con.execute(select([users.c.userrole]).where(users.c.userid == authDetails["userid"]))
                userrole = role.fetchone()
                if(userrole[0] == -1 or userrole[0] == 0):
                    budgetdataset = self.request.json_body
                    budgetdataset["orgcode"] = authDetails["orgcode"]
                    result = self.con.execute(budget.insert(),[budgetdataset])
                    return {"gkstatus":enumdict["Success"]}
                else:
                    return {"gkstatus":gkcore.enumdict["ActionDisallowed"] }
            except exc.IntegrityError:
               return {"gkstatus":enumdict["DuplicateEntry"]}
            except:
                return {"gkstatus":gkcore.enumdict["ConnectionFailed"] }
            finally:
                self.con.close()

    @view_config(request_method='GET', request_param='bud=all',renderer='json')
    def getlistofbudgets(self):
        """ To get all budgets list """
        try:
            token = self.request.headers["gktoken"]
        except:
            return  {"gkstatus":  gkcore.enumdict["UnauthorisedAccess"]}
        authDetails = authCheck(token)
        if authDetails["auth"] == False:
            return  {"gkstatus":  enumdict["UnauthorisedAccess"]} 
        else:
            try:
                self.con = eng.connect()
                btype = self.request.params["btype"]
                if "goid" in authDetails:
                    result = self.con.execute(select([budget.c.budid,budget.c.budname,budget.c.budtype,budget.c.contents,budget.c.startdate,budget.c.enddate]).where(and_(budget.c.budtype==btype,budget.c.orgcode==authDetails["orgcode"], budget.c.goid == authDetails["goid"])))
                else:
                    result = self.con.execute(select([budget.c.budid,budget.c.budname,budget.c.budtype,budget.c.contents,budget.c.startdate,budget.c.enddate]).where(and_(budget.c.budtype==btype,budget.c.orgcode==authDetails["orgcode"])))
                list = result.fetchall()
                budlist=[]
                for l in list:
                    budlist.append({"budid":l["budid"], "budname":l["budname"],"startdate":datetime.strftime(l["startdate"],'%d-%m-%Y'),"enddate":datetime.strftime(l["enddate"],'%d-%m-%Y'),"btype":l["budtype"]})
                
                return {"gkstatus": gkcore.enumdict["Success"], "gkresult":budlist }
            except:
                return {"gkstatus":gkcore.enumdict["ConnectionFailed"] }
            finally:
                self.con.close()

    @view_config(request_method='GET', request_param='bud=details',renderer='json')
    def getbudgetdetails(self):
        """ To get single budget details as per budget id 'budid' """
        try:
            token = self.request.headers["gktoken"]
        except:
            return  {"gkstatus":  gkcore.enumdict["UnauthorisedAccess"]}
        authDetails = authCheck(token)
        if authDetails["auth"] == False:
            return  {"gkstatus":  enumdict["UnauthorisedAccess"]} 
        else:
            try:
                self.con = eng.connect()
                if "goid" in authDetails:
                    result = self.con.execute(select([budget.c.budid,budget.c.budname,budget.c.budtype,budget.c.contents,budget.c.startdate,budget.c.enddate,budget.c.gaflag]).where(and_(budget.c.orgcode==authDetails["orgcode"],budget.c.budid== self.request.params["budid"], budget.c.goid == authDetails["goid"])))
                else:
                    result = self.con.execute(select([budget.c.budid,budget.c.budname,budget.c.budtype,budget.c.contents,budget.c.startdate,budget.c.enddate,budget.c.gaflag]).where(and_(budget.c.orgcode==authDetails["orgcode"],budget.c.budid== self.request.params["budid"])))
                list = result.fetchone()
                budlist={"budid":list["budid"], "budname":list["budname"],"startdate":datetime.strftime(list["startdate"],'%d-%m-%Y'),"enddate":datetime.strftime(list["enddate"],'%d-%m-%Y'),"btype":list["budtype"],"contents":list["contents"],"gaflag":list["gaflag"]}

                return {"gkstatus": gkcore.enumdict["Success"], "gkresult":budlist }
            except:
                return {"gkstatus":gkcore.enumdict["ConnectionFailed"] }
            finally:
                self.con.close()

    @view_config(request_method='GET', request_param='type=addtab',renderer='json')
    def getbalatbeginning(self):
        """ For clossing balances of all acounts.It  will fetch all acounts balance from financial startdate to the previous date of budget startdate with their accountcode.
        It will take financial start and budget start date as input.
        for budget type 3 which is cash. It will fetch all accounts which comes under the bank and cash subgroup.
        If the financial start date is same as budget start date then it will consider opening balances of accounts as clossing balance.
        For expense budget type will be 5 :
        In expense it will consider only that accounts which comes under the Direct and Indirect Expense group.
        
        """
        try:
            token = self.request.headers["gktoken"]
        except:
            return  {"gkstatus":  gkcore.enumdict["UnauthorisedAccess"]}
        authDetails = authCheck(token)
        if authDetails["auth"] == False:
            return  {"gkstatus":  enumdict["UnauthorisedAccess"]} 
        else:
            try:
                self.con = eng.connect()
                uptodate = self.request.params["uptodate"]
                financialStart = self.request.params["financialstart"]
                btype = self.request.params["btype"]
                if btype == '5':
                    directExp = self.con.execute("select accountcode,accountname from accounts where orgcode = %d and (groupcode in (select groupcode from groupsubgroups where orgcode=%d and (groupname = 'Direct Expense' or subgroupof in (select groupcode from groupsubgroups where orgcode= %d and (groupname='Direct Expense')))))"%(authDetails["orgcode"],authDetails["orgcode"],authDetails["orgcode"]))
                    accounts = directExp.fetchall()
                    DirectExpense=[]
                    totalBalAtBegin=0
                    if(uptodate != financialStart):
                        calculateToDate = datetime.strptime(uptodate,"%Y-%m-%d")
                        prevday = (calculateToDate - timedelta(days=1))
                        prevday = str(prevday)[0:10]
                        for account in accounts:
                            if "goid" in authDetails:
                                data = self.con.execute("select drs from vouchers where voucherdate >= '%s'  and voucherdate <= '%s' and (drs ? '%s') and goid = '%d' order by voucherdate DESC,vouchercode ;"%(str(financialStart), prevday,account["accountcode"], authDetails["goid"]))
                            else:
                                data = self.con.execute("select drs from vouchers where voucherdate >= '%s'  and voucherdate <= '%s' and (drs ? '%s') order by voucherdate DESC,vouchercode ;"%(str(financialStart), prevday,account["accountcode"]))
                            data = data.fetchall()
                            accountbal=0
                            for transaction in data:
                                accountbal += float(transaction["drs"][str(account["accountcode"])])
                            totalBalAtBegin = totalBalAtBegin + accountbal
                            DirectExpense.append({"accountname":account["accountname"],"accountcode":account["accountcode"],"accountbal":"%.2f"%float(accountbal)})
                    else:
                        for account in accounts:
                            DirectExpense.append({"accountname":account["accountname"],"accountcode":account["accountcode"],"accountbal":"%.2f"%float(0)})
                    
                    indirectExp = self.con.execute("select accountcode,accountname from accounts where orgcode = %d and (groupcode in (select groupcode from groupsubgroups where orgcode=%d and (groupname = 'Indirect Expense' or subgroupof in (select groupcode from groupsubgroups where orgcode= %d and (groupname='Indirect Expense')))))"%(authDetails["orgcode"],authDetails["orgcode"],authDetails["orgcode"]))
                    accounts = indirectExp.fetchall()
                    IndirectExpense=[]
                    if(uptodate != financialStart):
                        calculateToDate = datetime.strptime(uptodate,"%Y-%m-%d")
                        prevday = (calculateToDate - timedelta(days=1))
                        prevday = str(prevday)[0:10]
                        for account in accounts:
                            if "goid" in authDetails:
                                data = self.con.execute("select drs from vouchers where voucherdate >= '%s'  and voucherdate <= '%s' and (drs ? '%s') and goid = '%d' order by voucherdate DESC,vouchercode ;"%(str(financialStart), prevday,account["accountcode"], authDetails["goid"]))
                            else:
                                data = self.con.execute("select drs from vouchers where voucherdate >= '%s'  and voucherdate <= '%s' and (drs ? '%s') order by voucherdate DESC,vouchercode ;"%(str(financialStart), prevday,account["accountcode"]))
                            data = data.fetchall()
                            accountbal=0
                            for transaction in data:
                                accountbal += float(transaction["drs"][str(account["accountcode"])])
                            totalBalAtBegin = totalBalAtBegin + accountbal
                            IndirectExpense.append({"accountname":account["accountname"],"accountcode":account["accountcode"],"accountbal":"%.2f"%float(accountbal)})
                    else:
                        for account in accounts:
                            IndirectExpense.append({"accountname":account["accountname"],"accountcode":account["accountcode"],"accountbal":"%.2f"%float(0)})
                        
                    total = {"totalbal":"%.2f"%float(totalBalAtBegin),"DirectExpense":DirectExpense,"IndirectExpense":IndirectExpense}
                    return {"gkstatus": gkcore.enumdict["Success"], "gkresult":total }
                if btype == '3':
                    result = self.con.execute("select accountcode, openingbal, accountname from accounts where orgcode = %d and groupcode in (select groupcode from groupsubgroups where orgcode = %d and groupname in ('Cash')) order by accountname"%(authDetails["orgcode"],authDetails["orgcode"]))
                    cashaccounts = result.fetchall()
                    result = self.con.execute("select accountcode, openingbal, accountname from accounts where orgcode = %d and groupcode in (select groupcode from groupsubgroups where orgcode = %d and groupname in ('Bank')) order by accountname"%(authDetails["orgcode"],authDetails["orgcode"]))
                    bankaccounts = result.fetchall()
                    accountdata=[]
                    totalBalAtBegin=0
                    if(uptodate != financialStart):
                        calculateToDate = datetime.strptime(uptodate,"%Y-%m-%d")
                        prevday = (calculateToDate - timedelta(days=1))
                        prevday = str(prevday)[0:10]
                        cashaccountdata=[]
                        for bal in cashaccounts:
                            if "goid" in authDetails:
                                calbaldata = calculateBalance2(self.con,bal["accountcode"],str(financialStart), str(financialStart), prevday, authDetails["goid"])
                            else:
                                calbaldata = calculateBalance(self.con,bal["accountcode"],str(financialStart), str(financialStart), prevday)
                            accountbal = 0
                            if (calbaldata["baltype"] == 'Cr'):
                                totalBalAtBegin = totalBalAtBegin - calbaldata["curbal"]
                                accountbal = -calbaldata["curbal"]
                            if (calbaldata["baltype"] == 'Dr'):
                                totalBalAtBegin = totalBalAtBegin + calbaldata["curbal"]
                                accountbal = calbaldata["curbal"]
                            cashaccountdata.append({"accountname":bal["accountname"],"accountbal":"%.2f"%float(accountbal)})
                        bankaccountdata=[]
                        for bal in bankaccounts:
                            if "goid" in authDetails:
                                calbaldata = calculateBalance2(self.con,bal["accountcode"],str(financialStart), str(financialStart), prevday, authDetails["goid"])
                            else:
                                calbaldata = calculateBalance(self.con,bal["accountcode"],str(financialStart), str(financialStart), prevday)
                            accountbal = 0
                            if (calbaldata["baltype"] == 'Cr'):
                                totalBalAtBegin = totalBalAtBegin - calbaldata["curbal"]
                                accountbal = -calbaldata["curbal"]
                            if (calbaldata["baltype"] == 'Dr'):
                                totalBalAtBegin = totalBalAtBegin + calbaldata["curbal"]
                                accountbal = calbaldata["curbal"]
                            bankaccountdata.append({"accountname":bal["accountname"],"accountbal":"%.2f"%float(accountbal)})
                        data={"balatbegin":"%.2f"%float(totalBalAtBegin),"cashaccountdata":cashaccountdata,"bankaccountdata":bankaccountdata}
                        return {"gkstatus": gkcore.enumdict["Success"], "gkresult":data }
                    else:
                        prevday = uptodate
                        cashaccountdata=[]
                        for bal in cashaccounts:
                            if "goid" in authDetails:
                                calbaldata = calculateBalance2(self.con,bal["accountcode"],str(financialStart), str(financialStart), prevday, authDetails["goid"])
                            else:
                                calbaldata = calculateBalance(self.con,bal["accountcode"],str(financialStart), str(financialStart), prevday)
                            accountbal = 0
                            if (calbaldata["openbaltype"] == 'Cr'):
                                totalBalAtBegin = totalBalAtBegin - calbaldata["balbrought"]
                                accountbal = -calbaldata["balbrought"]
                            if (calbaldata["openbaltype"] == 'Dr'):
                                totalBalAtBegin = totalBalAtBegin + calbaldata["balbrought"]
                                accountbal = calbaldata["balbrought"]
                            cashaccountdata.append({"accountname":bal["accountname"],"accountbal":"%.2f"%float(accountbal)})
                        bankaccountdata=[]
                        for bal in bankaccounts:
                            if "goid" in authDetails:
                                calbaldata = calculateBalance2(self.con,bal["accountcode"],str(financialStart), str(financialStart), prevday, authDetails["goid"])
                            else:
                                calbaldata = calculateBalance(self.con,bal["accountcode"],str(financialStart), str(financialStart), prevday)
                            accountbal = 0
                            if (calbaldata["openbaltype"] == 'Cr'):
                                totalBalAtBegin = totalBalAtBegin - calbaldata["balbrought"]
                                accountbal = -calbaldata["balbrought"]
                            if (calbaldata["openbaltype"] == 'Dr'):
                                totalBalAtBegin = totalBalAtBegin + calbaldata["balbrought"]
                                accountbal = calbaldata["balbrought"]
                            bankaccountdata.append({"accountname":bal["accountname"],"accountbal":"%.2f"%float(accountbal)})
                        data={"balatbegin":"%.2f"%float(totalBalAtBegin),"cashaccountdata":cashaccountdata,"bankaccountdata":bankaccountdata}
                        return {"gkstatus": gkcore.enumdict["Success"], "gkresult":data }
                if btype == '19':
                    directExpense = self.con.execute("select accountcode,accountname from accounts where orgcode = %d and (groupcode in (select groupcode from groupsubgroups where orgcode=%d and (groupname = 'Direct Expense' or subgroupof in (select groupcode from groupsubgroups where orgcode= %d and (groupname='Direct Expense')))))"%(authDetails["orgcode"],authDetails["orgcode"],authDetails["orgcode"]))                    
                    expense = directExpense.fetchall();
                    directIncome = self.con.execute("select accountcode, accountname from accounts where orgcode = %d and (groupcode in (select groupcode from groupsubgroups where orgcode=%d and (groupname = 'Direct Income' or subgroupof in (select groupcode from groupsubgroups where orgcode= %d and (groupname ='Direct Income')))))"%(authDetails["orgcode"],authDetails["orgcode"],authDetails["orgcode"]))
                    income = directIncome.fetchall();
                    expense=[]
                    totalBalAtBegin=0
                    if(uptodate != financialStart):
                        calculateToDate = datetime.strptime(uptodate,"%Y-%m-%d")
                        prevday = (calculateToDate - timedelta(days=1))
                        prevday = str(prevday)[0:10]
                        for account in accounts:
                            if "goid" in authDetails:
                                data = self.con.execute("select drs from vouchers where voucherdate >= '%s'  and voucherdate <= '%s' and (drs ? '%s') and goid = '%d' order by voucherdate DESC,vouchercode ;"%(str(financialStart), prevday,account["accountcode"], authDetails["goid"]))
                            else:
                                data = self.con.execute("select drs from vouchers where voucherdate >= '%s'  and voucherdate <= '%s' and (drs ? '%s') order by voucherdate DESC,vouchercode ;"%(str(financialStart), prevday,account["accountcode"]))
                            data = data.fetchall()
                            accountbal=0
                            for transaction in data:
                                accountbal += float(transaction["drs"][str(account["accountcode"])])
                            totalBalAtBegin = totalBalAtBegin + accountbal
                            expense.append({"accountname":account["accountname"],"accountcode":account["accountcode"],"accountbal":"%.2f"%float(accountbal)})
                    else:
                        for account in accounts:
                            expense.append({"accountname":account["accountname"],"accountcode":account["accountcode"],"accountbal":"%.2f"%float(0)})

                    income=[]
                    totalBalAtBegin=0
                    if(uptodate != financialStart):
                        calculateToDate = datetime.strptime(uptodate,"%Y-%m-%d")
                        prevday = (calculateToDate - timedelta(days=1))
                        prevday = str(prevday)[0:10]
                        for account in accounts:
                            if "goid" in authDetails:
                                data = self.con.execute("select crs from vouchers where voucherdate >= '%s'  and voucherdate <= '%s' and (crs ? '%s') and goid = '%d' order by voucherdate DESC,vouchercode ;"%(str(financialStart), prevday,account["accountcode"], authDetails["goid"]))
                            else:
                                data = self.con.execute("select crs from vouchers where voucherdate >= '%s'  and voucherdate <= '%s' and (crs ? '%s') order by voucherdate DESC,vouchercode ;"%(str(financialStart), prevday,account["accountcode"]))
                            data = data.fetchall()
                            accountbal=0
                            for transaction in data:
                                accountbal += float(transaction["crs"][str(account["accountcode"])])
                            totalBalAtBegin = totalBalAtBegin + accountbal
                            income.append({"accountname":account["accountname"],"accountcode":account["accountcode"],"accountbal":"%.2f"%float(accountbal)})
                    else:
                        for account in accounts:
                            income.append({"accountname":account["accountname"],"accountcode":account["accountcode"],"accountbal":"%.2f"%float(0)})
                    total = {"totalbal":"%.2f"%float(totalBalAtBegin),"expense":expense,"income":income}
                    return {"gkstatus": gkcore.enumdict["Success"], "gkresult":total }
            except:
                return {"gkstatus":gkcore.enumdict["ConnectionFailed"] }
            finally:
                self.con.close()

    @view_config(request_method='PUT', renderer='json')
    def editbudgets(self):
        try:
            token = self.request.headers["gktoken"]
        except:
            return  {"gkstatus":  gkcore.enumdict["UnauthorisedAccess"]}
        authDetails = authCheck(token)
        if authDetails["auth"] == False:
            return  {"gkstatus":  enumdict["UnauthorisedAccess"]}
        else:
            try:
                self.con = eng.connect()
                role = self.con.execute(select([users.c.userrole]).where(users.c.userid == authDetails["userid"]))
                userrole = role.fetchone()
                if(userrole[0] == -1 or userrole[0] == 0):
                    dataset = self.request.json_body
                    result = self.con.execute(budget.update().where(budget.c.budid==dataset["budid"]).values(dataset))
                    return {"gkstatus":enumdict["Success"]}
                else:
                    return {"gkstatus":gkcore.enumdict["ActionDisallowed"] }
            except:
                return {"gkstatus":gkcore.enumdict["ConnectionFailed"] }
            finally:
                self.con.close()

    @view_config(request_method='DELETE', renderer='json')
    def deletebudget(self):
        try:
            token = self.request.headers["gktoken"]
        except:
            return  {"gkstatus":  gkcore.enumdict["UnauthorisedAccess"]}
        authDetails = authCheck(token)
        if authDetails["auth"] == False:
            return  {"gkstatus":  enumdict["UnauthorisedAccess"]}
        else:
            try:
                dataset = self.request.json_body
                self.con = eng.connect()
                role = self.con.execute(select([users.c.userrole]).where(users.c.userid==authDetails["userid"]))
                userrole=role.fetchone()
                if(userrole[0] == -1 or userrole[0] == 0):
                    result = self.con.execute(budget.delete().where(budget.c.budid==dataset["budid"]))
                    return {"gkstatus":enumdict["Success"]}
                else:
                    return {"gkstatus":gkcore.enumdict["ActionDisallowed"] }
            except exc.IntegrityError:
                return {"gkstatus":enumdict["ActionDisallowed"]}
            except:
                return {"gkstatus":enumdict["ConnectionFailed"] }
            finally:
                self.con.close()
    
    @view_config(request_method='GET',request_param='type=cashReport', renderer='json')
    def budgetReport(self):
        """
        Purpose:
        To calculate complete budget for given time period.
        Input from webapp: financialstartdate,budgetperiod,budgetid
        fetch all field data from budget table with budget Id. 
        only in cash budget the contents(JSON field) field containes "flowin" and "flowout" data.
        flowin : incoming cash budget and flowout : outgoing cash budget.
        for cash budget only that accounts which are under cash and bank subgroups are take in to consideration.
        after fetching all accounts for loop is done to calculate balance with calculatebalance function written above.
        calculatebalance fun. will gives (per account totalCr and Dr, balance remaining with its type(Cr/Dr),
        account opening balance with type )
        Calculations for cash budget:
        budget balance = (total opening balance + cash inflow) - cash ouflow
        variance(cash inflow) = inflow - total Dr
        variance(cash outflow) = outflow - total Cr
        variance(balance) = budget balance - total balance
        """
        try:
            token = self.request.headers["gktoken"]
        except:
            return  {"gkstatus":  gkcore.enumdict["UnauthorisedAccess"]}
        authDetails = authCheck(token)
        if authDetails["auth"] == False:
            return  {"gkstatus":  enumdict["UnauthorisedAccess"]}
        else:
            try:
                self.con = eng.connect()
                financialStart = self.request.params["financialstart"]
                result = self.con.execute(select([budget.c.goid,budget.c.contents,budget.c.startdate,budget.c.enddate]).where(and_(budget.c.orgcode==authDetails["orgcode"],budget.c.budid== self.request.params["budid"])))
                list = result.fetchone()
                startdate = str(list["startdate"])[0:10]
                enddate = str(list["enddate"])[0:10]
                budgetIn = list["contents"]["inflow"]
                budgetOut = list["contents"]["outflow"]
                cbAccountsData = self.con.execute("select accountcode, openingbal, accountname from accounts where orgcode = %d and groupcode in (select groupcode from groupsubgroups where orgcode = %d and groupname in ('Bank','Cash')) order by accountname"%(authDetails["orgcode"],authDetails["orgcode"]))
                cbAccounts = cbAccountsData.fetchall()
                # to calculate opening balance. If budget start date and financial start date are same then the opening balance for 
                # budget will becomes accounts opening balance. Else opening balance for budget will get by calculating all crs and drs up to previous date of 
                # budget start date, means add of total accounts remaining balance.
                totalopeningbal = 0
                if(startdate != financialStart):
                    d = startdate
                    calculateToDate = datetime.strptime(d,"%Y-%m-%d")
                    prevday = (calculateToDate - timedelta(days=1))
                    prevday = str(prevday)[0:10]
                    for bal in cbAccounts:
                        if (list["goid"] != None):
                            calculate = calculateBalance(self.con,bal["accountcode"],str(self.request.params["financialstart"]), self.request.params["financialstart"], prevday,list["goid"])
                        else:
                            calculate = calculateBalance(self.con,bal["accountcode"],str(self.request.params["financialstart"]), self.request.params["financialstart"], prevday)
                        if (calculate["baltype"] == 'Cr'):
                            totalopeningbal = totalopeningbal - calculate["curbal"]
                        if (calculate["baltype"] == 'Dr'):
                            totalopeningbal = totalopeningbal + calculate["curbal"]
                else:
                    prevday = startdate
                    for bal in cbAccounts:
                        if (list["goid"] != None):
                            calculate = calculateBalance(self.con,bal["accountcode"],str(self.request.params["financialstart"]), self.request.params["financialstart"], prevday,list["goid"])
                        else:
                            calculate = calculateBalance(self.con,bal["accountcode"],str(self.request.params["financialstart"]), self.request.params["financialstart"], prevday)
                        if (calculate["openbaltype"] == 'Cr'):
                            totalopeningbal = totalopeningbal - calculate["balbrought"]
                        if (calculate["openbaltype"] == 'Dr'):
                            totalopeningbal = totalopeningbal + calculate["balbrought"]
                calbaldata=[]
                totalCr = 0
                totalDr = 0
                totalCurbal = 0
                accData =[]
                
                for bal in cbAccounts:
                    accountcode = str(bal["accountcode"])
                    # goid is branch id . if branchid in budget then should calculate balance only for that branch.
                    if (list["goid"] != None):
                        calbaldata = calculateBalance2(self.con,accountcode, financialStart, startdate, enddate, list["goid"])
                        transactionsRecords = self.con.execute("select drs,crs from vouchers where voucherdate >= '%s'  and voucherdate <= '%s' and (drs ? '%s' or crs ? '%s') and goid = '%d' order by voucherdate DESC,vouchercode ;"%(startdate, enddate,accountcode,accountcode, list["goid"]))
                    else:
                        calbaldata = calculateBalance(self.con,accountcode, financialStart, startdate, enddate)
                        transactionsRecords = self.con.execute("select drs,crs from vouchers where voucherdate >= '%s'  and voucherdate <= '%s' and (drs ? '%s' or crs ? '%s') order by voucherdate DESC,vouchercode ;"%(startdate, enddate,accountcode,accountcode))
                    transactions = transactionsRecords.fetchall()
                    accCr = 0
                    accDr = 0
                    accBal = 0
                    for transaction in transactions:
                        if transaction["drs"].has_key(str(accountcode)):
                            accDr += float(transaction["drs"][accountcode])
                            totalDr += float(transaction["drs"][accountcode])
                        if transaction["crs"].has_key(accountcode):
                            accCr += float(transaction["crs"][accountcode])
                            totalCr += float(transaction["crs"][accountcode])
                    if (calbaldata["baltype"] == 'Cr'):
                        totalCurbal = totalCurbal - calbaldata["curbal"]
                        accBal = -calbaldata["curbal"]
                    if (calbaldata["baltype"] == 'Dr'):
                        totalCurbal = totalCurbal + calbaldata["curbal"]
                        accBal = calbaldata["curbal"]
                    accData.append({"accountname":bal["accountname"],"accCr":"%.2f"%float(accCr),"accDr":"%.2f"%float(accDr),"accBal":"%.2f"%float(accBal)})
                budgetBal = float(totalopeningbal) + float(budgetIn) - float(budgetOut)
                # Variance calculation
                varCr = float(budgetOut) - float(totalCr)
                varDr = float(budgetIn) - float(totalDr)
                varBal = float(budgetBal) - float(totalCurbal)
                total = {"totalCr":"%.2f"%float(totalCr),"totalDr":"%.2f"%float(totalDr),"budgetclosingbal":"%.2f"%float(totalCurbal),"totalopeningbal":"%.2f"%float(totalopeningbal),"budgetIn":"%.2f"%float(budgetIn),"budgetOut":"%.2f"%float(budgetOut),"budgetBal":"%.2f"%float(budgetBal),"varCr":"%.2f"%float(varCr),"varDr":"%.2f"%float(varDr),"varBal":"%.2f"%float(varBal),"accData":accData}
                return{"gkstatus": gkcore.enumdict["Success"], "gkresult":total}
            except:
                return {"gkstatus":enumdict["ConnectionFailed"] }
            finally:
                self.con.close()
    @view_config(request_method='GET',request_param='type=expenseReport', renderer='json')
    def expenseReport(self):
        """Purpose:
                To calculate report for expense budget. It takes budgetid(budid) and fanancialstart as input.
            In this only that accounts will consider which comes under the Direct and Indirect expense group.
            Here contents field of budget table will have json type data. In which key will be accountcode and their value will be budget amount.
            Firstly will fetch budget details from budget table as per budget id.
            Here we need previuos date of start date of budget to get the previously expense of each accounts.
            For getting accounts balance we will considr only Dr from vouchers because expense is nominal accounts so it means debit all losses and expense.
            By fetching balance for each accounts we will takes vouchers for budget periods. So that we will get actual expense balance of each account for that period.
            To calculate variance reduce actual balance from budget amount. 
            Budgeted balance is previous balance plus budget amount.
            Actual balance is actual balance of budget period and previos balance.
        """
        try:
            token = self.request.headers["gktoken"]
        except:
            return  {"gkstatus":  gkcore.enumdict["UnauthorisedAccess"]}
        authDetails = authCheck(token)
        if authDetails["auth"] == False:
            return  {"gkstatus":  enumdict["UnauthorisedAccess"]}
        else:
            try:
                self.con = eng.connect()
                financialStart = self.request.params["financialstart"]
                result = self.con.execute(select([budget.c.goid,budget.c.contents,budget.c.startdate,budget.c.enddate]).where(and_(budget.c.orgcode==authDetails["orgcode"],budget.c.budid== self.request.params["budid"])))
                budgetdata = result.fetchone()
                startdate = str(budgetdata["startdate"])[0:10]
                enddate = str(budgetdata["enddate"])[0:10]
                accounts = budgetdata["contents"]
                accountdata=[]
                totalbudget = 0
                totalactual = 0
                totalvariance = 0
                totalbudgetedbal = 0
                totalactualbal = 0
                totalpreviousbal = 0 
                if(startdate != financialStart):
                    calculateToDate = datetime.strptime(startdate,"%Y-%m-%d")
                    prevday = (calculateToDate - timedelta(days=1))
                    prevday = str(prevday)[0:10]
                    for key in accounts:
                        budgetamount = "%.2f"%float(accounts[key])
                        accountname = self.con.execute("select accountname from accounts where accountcode = %d"%(int(key)))
                        accountname = accountname.fetchone()
                        if (budgetdata["goid"] != None):
                            previousAccData = self.con.execute("select drs from vouchers where voucherdate >= '%s'  and voucherdate <= '%s' and (drs ? '%s') and goid = '%d' order by voucherdate DESC,vouchercode ;"%(str(financialStart), prevday,key, budgetdata["goid"]))
                            actualAccData = self.con.execute("select drs from vouchers where voucherdate >= '%s'  and voucherdate <= '%s' and (drs ? '%s') and goid = '%d' order by voucherdate DESC,vouchercode ;"%(startdate, enddate,key, budgetdata["goid"]))
                        else:
                            previousAccData = self.con.execute("select drs from vouchers where voucherdate >= '%s'  and voucherdate <= '%s' and (drs ? '%s') order by voucherdate DESC,vouchercode ;"%(str(financialStart), prevday,key))
                            actualAccData = self.con.execute("select drs from vouchers where voucherdate >= '%s'  and voucherdate <= '%s' and (drs ? '%s') order by voucherdate DESC,vouchercode ;"%(startdate, enddate,key))
                        actualAccData = actualAccData.fetchall()
                        actualAmount = 0
                        for transaction in actualAccData:
                            actualAmount += float(transaction["drs"][key])
                        previousAccData = previousAccData.fetchall()
                        accountbal = 0
                        for transaction in previousAccData:
                            accountbal += float(transaction["drs"][key])
                        budgetedBal = float(accountbal) + float(budgetamount)
                        accVariance = float(budgetamount) - float(actualAmount)
                        actualBal = float(accountbal) + float(actualAmount)

                        totalbudget += float(budgetamount)
                        totalactual += float(actualAmount)
                        totalvariance += float(accVariance)
                        totalbudgetedbal += float(budgetedBal)
                        totalactualbal += float(actualBal)
                        totalpreviousbal += float(accountbal)
                        accountdata.append({"actualamount":"%.2f"%float(actualAmount),"accountname":accountname[0],"accountcode":key,"previousbal":"%.2f"%float(accountbal),"budgetamount":"%.2f"%float(budgetamount),"budgetedbal":"%.2f"%float(budgetedBal),"accvariance":"%.2f"%float(accVariance),"actualbal":"%.2f"%float(actualBal)})
                    total={"totalpreviousbal":"%.2f"%float(totalpreviousbal),"totalbudget":"%.2f"%float(totalbudget),"totalactual":"%.2f"%float(totalactual),"totalvariance":"%.2f"%float(totalvariance),"totalbudgetedbal":"%.2f"%float(totalbudgetedbal),"totalactualbal":"%.2f"%float(totalactualbal),"accountdata":accountdata}
                """ Here the start date of budget is smae as financial start date then the previous expense will be zero.
                """
                if(startdate == financialStart):
                    for key in accounts:
                        budgetamount = "%.2f"%float(accounts[key])
                        accountname = self.con.execute("select accountname from accounts where accountcode = %d"%(int(key)))
                        accountname = accountname.fetchone()
                        if (budgetdata["goid"] != None):
                            actualAccData = self.con.execute("select drs from vouchers where voucherdate >= '%s'  and voucherdate <= '%s' and (drs ? '%s') and goid = '%d' order by voucherdate DESC,vouchercode ;"%(startdate, enddate,key, budgetdata["goid"]))
                        else:
                            actualAccData = self.con.execute("select drs from vouchers where voucherdate >= '%s'  and voucherdate <= '%s' and (drs ? '%s') order by voucherdate DESC,vouchercode ;"%(startdate, enddate,key))
                        actualAccData = actualAccData.fetchall()
                        accountbal = 0
                        actualAmount = 0
                        for transaction in actualAccData:
                            actualAmount += float(transaction["drs"][key])
                        budgetedBal = float(accountbal) + float(budgetamount)
                        accVariance = float(budgetamount) - float(actualAmount)
                        actualBal = float(accountbal) + float(actualAmount)
                        accountdata.append({"actualamount":actualAmount,"accountname":accountname[0],"accountcode":key,"previousbal":"%.2f"%float(accountbal),"budgetamount":"%.2f"%float(budgetamount),"budgetedbal":"%.2f"%float(budgetedBal),"accvariance":"%.2f"%float(accVariance),"actualbal":"%.2f"%float(actualBal)})
                        
                        totalbudget += float(budgetamount)
                        totalactual += float(actualAmount)
                        totalvariance += float(accVariance)
                        totalbudgetedbal += float(budgetedBal)
                        totalactualbal += float(actualBal)
                    total={"totalpreviousbal":"%.2f"%float(totalpreviousbal),"totalbudget":"%.2f"%float(totalbudget),"totalactual":"%.2f"%float(totalactual),"totalvariance":"%.2f"%float(totalvariance),"totalbudgetedbal":"%.2f"%float(totalbudgetedbal),"totalactualbal":"%.2f"%float(totalactualbal),"accountdata":accountdata}
                return{"gkstatus": gkcore.enumdict["Success"], "gkresult":total}
            except:
                return {"gkstatus":enumdict["ConnectionFailed"] }
            finally:
                self.con.close()
    
    @view_config(request_method='GET',request_param='type=salesReport', renderer='json')
    def salesReport(self):
        """ 
        """
        try:
            token = self.request.headers["gktoken"]
        except:
            return  {"gkstatus":  gkcore.enumdict["UnauthorisedAccess"]}
        authDetails = authCheck(token)
        if authDetails["auth"] == False:
            return  {"gkstatus":  enumdict["UnauthorisedAccess"]}
        else:
            try:
                self.con = eng.connect()
                financialStart = self.request.params["financialstart"]
                result = self.con.execute(select([budget.c.goid,budget.c.contents,budget.c.startdate,budget.c.enddate]).where(and_(budget.c.orgcode==authDetails["orgcode"],budget.c.budid== self.request.params["budid"])))
                budgetdata = result.fetchone()
                startdate = str(budgetdata["startdate"])[0:10]
                enddate = str(budgetdata["enddate"])[0:10]
                accounts = budgetdata["contents"]
                accountdata=[]
                