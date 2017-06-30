
"""
Copyright (C) 2013, 2014, 2015, 2016 Digital Freedom Foundation
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
"Ishan Masdekar " <imasdekar@dff.org.in>
"Navin Karkera" <navin@dff.org.in>
"""


from pyramid.view import view_defaults,  view_config
from gkcore.views.api_login import authCheck
from gkcore import eng, enumdict
from pyramid.request import Request
from gkcore.models import gkdb
from sqlalchemy.sql import select, distinct
from sqlalchemy import func, desc
import json
from sqlalchemy.engine.base import Connection
from sqlalchemy import and_
import jwt
import gkcore
from gkcore.models.meta import dbconnect
from Crypto.PublicKey import RSA
from gkcore.models.gkdb import metadata
from gkcore.models.meta import inventoryMigration,addFields
con= Connection

@view_defaults(route_name='organisations')
class api_organisation(object):
    def __init__(self,request):
        self.request = Request
        self.request = request
        self.con = Connection
        print "Organisation initialized"
    def gkUpgrade(self):
        """
        This function will be called only once while upgrading gnukhata.
        We check if the field stockdate is present.
        If it is not present it means that this is an upgrade.
        """
        self.con = eng.connect()
        try:
            self.con.execute(select(gkdb.organisation.c.gstin))
            self.con.execute(select([func.count(gkdb.invoice.c.consignee)]))
            self.con.execute(select([func.count(gkdb.customerandsupplier.c.gstin)]))
            self.con.execute(select([func.count(gkdb.product.c.gscode)]))
            self.con.execute(select([func.count(gkdb.state.c.stateid)]))
            self.con.execute(select([func.count(gkdb.rejectionnote.c.rnid)]))
            self.con.execute(select([func.count(gkdb.stock.c.stockdate)]))
            self.con.execute(select([func.count(gkdb.transfernote.c.fromgodown)]))
            self.con.execute(select([func.count(gkdb.customerandsupplier.c.advamt)]))
            self.con.execute(select([func.count(gkdb.transfernote.c.duedate)]))
            self.con.execute(select(gkdb.dcinv.c.invprods))
            self.con.execute(select(gkdb.organisation.c.logo))
            self.con.execute(select(gkdb.vouchers.c.instrumentno))
            self.con.execute(select(gkdb.organisation.c.invsflag))
            self.con.execute(select(gkdb.organisation.c.billflag))
            self.con.execute(select([func.count(gkdb.billwise.c.billid)]))
        except:
            self.con.execute("alter table delchal drop column issuerid")
            self.con.execute("ALTER TABLE delchal DROP CONSTRAINT delchal_custid_fkey, ADD CONSTRAINT delchal_custid_fkey FOREIGN KEY (custid) REFERENCES customerandsupplier(custid)")
            self.con.execute("ALTER TABLE invoice DROP CONSTRAINT invoice_custid_fkey, ADD CONSTRAINT invoice_custid_fkey FOREIGN KEY (custid) REFERENCES customerandsupplier(custid)")
            self.con.execute("alter table organisation add gstin text")
            self.con.execute("alter table product alter specs drop not null,alter uomid drop not null")
            self.con.execute("alter table invoice add consignee jsonb")
            self.con.execute("alter table customerandsupplier add gstin text")
            self.con.execute("alter table product add gsflag integer")
            self.con.execute("alter table product add gscode text")
            self.con.execute("alter table organisation add gstin text")
            self.con.execute("alter table product alter specs drop not null,alter uomid drop not null")
            self.con.execute("alter table invoice add consignee jsonb")
            self.con.execute("create table state(stateid serial, statecode integer,statename unicodetext,primary key (stateid))")
            self.con.execute("create table billwise(billid serial, vouchercode integer, invid integer, adjdate timestamp, adjamount numeric (12,2), orgcode integer, primary key (billid), foreign key (vouchercode) references vouchers(vouchercode), foreign key(invid) references invoice(invid), foreign key (orgcode) references organisation (orgcode))")
            self.con.execute("create table rejectionnote(rnid serial, rnno integer not null, rndate timestamp not null, inout integer not null, dcid integer, invid integer, issuerid integer, orgcode integer not null, primary key(rnid), foreign key (dcid) references delchal(dcid) ON DELETE CASCADE, foreign key (invid) references invoice(invid) ON DELETE CASCADE, foreign key (issuerid) references users(userid) ON DELETE CASCADE, foreign key (orgcode) references organisation(orgcode) ON DELETE CASCADE, unique(rnno, inout, orgcode))")
            self.con.execute("alter table organisation add invsflag integer default 1")
            self.con.execute("alter table organisation add billflag integer default 1")
            self.con.execute("alter table vouchers add instrumentno text")
            self.con.execute("alter table vouchers add branchname text")
            self.con.execute("alter table vouchers add bankname text")
            self.con.execute("alter table vouchers add instrumentdate timestamp")
            self.con.execute("alter table organisation add logo json")
            self.con.execute("alter table dcinv add invprods jsonb")
            self.con.execute("alter table transfernote add duedate timestamp")
            self.con.execute("alter table transfernote add grace integer")
            self.con.execute("alter table customerandsupplier add advamt numeric default 0.00")
            self.con.execute("alter table customerandsupplier add onaccamt numeric default 0.00")
            self.con.execute("alter table transfernote add fromgodown integer")
            self.con.execute("alter table transfernote add foreign key(fromgodown) references godown(goid)")
            self.con.execute("alter table transfernote drop column canceldate")
            self.con.execute("alter table transfernote drop column cancelflag")
            self.con.execute("alter table invoice add freeqty jsonb")
            self.con.execute("alter table invoice add amountpaid numeric default 0.00")
            self.con.execute("alter table stock add stockdate timestamp")
            self.con.execute("alter table delchal add attachment json")
            self.con.execute("alter table delchal add attachmentcount integer default 0")
            self.con.execute("alter table invoice add attachment json")
            self.con.execute("alter table invoice add attachmentcount integer default 0")
            self.con.execute("alter table purchaseorder add creditperiod text")
            self.con.execute("alter table purchaseorder add taxstate text")
            self.con.execute("alter table purchaseorder add togodown integer")
            self.con.execute("alter table purchaseorder drop column schedule")
            self.con.execute("alter table purchaseorder add schedule jsonb")
            self.con.execute("alter table purchaseorder drop column maxdate")
            self.con.execute("alter table purchaseorder drop column datedelivery")
            self.con.execute("alter table purchaseorder drop column deliveryplaceaddr")
            self.con.execute("alter table purchaseorder drop column tax")
            self.con.execute("alter table purchaseorder drop column productdetails")
            self.con.execute("alter table purchaseorder add foreign key(togodown) references godown(goid)")
            self.con.execute("create table usergodown(ugid serial, goid integer, userid integer, orgcode integer, primary key(ugid), foreign key (goid) references godown(goid),  foreign key (userid) references users(userid), foreign key (orgcode) references organisation(orgcode))")
            self.con.execute("create table log(logid serial, time timestamp, activity text, userid integer, orgcode integer,  primary key (logid), foreign key(userid) references users(userid), foreign key (orgcode) references organisation(orgcode))")
            #return 0
        finally:
            self.con.close()
            return 0

    @view_config(request_method='GET', renderer ='json')
    def getOrgs(self):
        try:
            self.gkUpgrade()
            self.con=eng.connect()
            result = self.con.execute(select([gkdb.organisation.c.orgname, gkdb.organisation.c.orgtype]).order_by(gkdb.organisation.c.orgname).distinct())
            orgs = []
            for row in result:
                orgs.append({"orgname":row["orgname"], "orgtype":row["orgtype"]})
                orgs.sort()
            self.con.close()
            return {"gkstatus":enumdict["Success"], "gkdata":orgs}
        except:
            self.con.close()
            return {"gkstatus":enumdict["ConnectionFailed"]}

    @view_config(request_method='GET', request_param='type=orgcodelist', renderer='json' , route_name="organisations")
    def getsubOrgs(self):
        try:
            self.con=eng.connect()
            result = self.con.execute(select([gkdb.organisation.c.orgname, gkdb.organisation.c.orgtype,gkdb.organisation.c.orgcode,gkdb.organisation.c.yearstart,gkdb.organisation.c.yearend]).order_by(gkdb.organisation.c.orgcode))
            orgs = []
            for row in result:
                orgs.append({"orgname":row["orgname"], "orgtype":row["orgtype"], "orgcode":row["orgcode"], "yearstart":str(row["yearstart"]), "yearend":str(row["yearend"]) })
                orgs.sort()
            self.con.close()
            return {"gkstatus":enumdict["Success"], "gkdata":orgs}
        except:
            self.con.close()
            return {"gkstatus":enumdict["ConnectionFailed"]}

    @view_config(route_name='orgyears', request_method='GET', renderer ='json')
    def getYears(self):
        try:
            self.con = eng.connect()
            result = self.con.execute(select([gkdb.organisation.c.yearstart, gkdb.organisation.c.yearend,gkdb.organisation.c.orgcode]).where(and_(gkdb.organisation.c.orgname==self.request.matchdict["orgname"], gkdb.organisation.c.orgtype == self.request.matchdict["orgtype"])).order_by(desc(gkdb.organisation.c.yearend)))
            years = []
            for row in result:
                years.append({"yearstart":str(row["yearstart"]), "yearend":str(row["yearend"]),"orgcode":row["orgcode"]})
            self.con.close()
            return {"gkstatus":enumdict["Success"],"gkdata":years}
        except:
            self.con.close()
            return {"gkstatus":enumdict["ConnectionFailed"]}

    @view_config(request_method='POST',renderer='json')
    def postOrg(self):

        try:
            self.con = eng.connect()
            dataset = self.request.json_body
            orgdata = dataset["orgdetails"]
            userdata = dataset["userdetails"]
            result = self.con.execute(select([gkdb.signature]))
            sign = result.fetchone()
            if sign == None:
                key = RSA.generate(2560)
                privatekey = key.exportKey('PEM')
                sig = {"secretcode":privatekey}
                gkcore.secret = privatekey
                result = self.con.execute(gkdb.signature.insert(),[sig])
            elif len(sign["secretcode"]) <= 20:
                result = con.execute(gkdb.signature.delete())
                if result.rowcount == 1:
                    key = RSA.generate(2560)
                    privatekey = key.exportKey('PEM')
                    sig = {"secretcode":privatekey}
                    gkcore.secret = privatekey
                    result = self.con.execute(gkdb.signature.insert(),[sig])
            try:
                self.con.execute(select([gkdb.organisation.c.invflag]))
            except:
                inventoryMigration(self.con,eng)
            try:
                con.execute(select([gkdb.delchal.c.modeoftransport,gkdb.delchal.c.noofpackages]))
                con.execute(select([gkdb.transfernote.c.recieveddate]))
            except:
                addFields(self.con,eng)

            result = self.con.execute(gkdb.organisation.insert(),[orgdata])
            if result.rowcount==1:
                code = self.con.execute(select([gkdb.organisation.c.orgcode]).where(and_(gkdb.organisation.c.orgname==orgdata["orgname"], gkdb.organisation.c.orgtype==orgdata["orgtype"], gkdb.organisation.c.yearstart==orgdata["yearstart"], gkdb.organisation.c.yearend==orgdata["yearend"])))
                orgcode = code.fetchone()
                try:
                    currentassets= {"groupname":"Current Assets","orgcode":orgcode["orgcode"]}
                    result = self.con.execute(gkdb.groupsubgroups.insert(),currentassets)
                    result = self.con.execute(select([gkdb.groupsubgroups.c.groupcode]).where(and_(gkdb.groupsubgroups.c.groupname=="Current Assets",gkdb.groupsubgroups.c.orgcode==orgcode["orgcode"])))
                    grpcode = result.fetchone()
                    result = self.con.execute(gkdb.groupsubgroups.insert(),[{"groupname":"Bank","orgcode":orgcode["orgcode"],"subgroupof":grpcode["groupcode"]},{"groupname":"Cash","orgcode":orgcode["orgcode"],"subgroupof":grpcode["groupcode"]},{"groupname":"Inventory","orgcode":orgcode["orgcode"],"subgroupof":grpcode["groupcode"]},{"groupname":"Loans & Advance","orgcode":orgcode["orgcode"],"subgroupof":grpcode["groupcode"]},{"groupname":"Sundry Debtors","orgcode":orgcode["orgcode"],"subgroupof":grpcode["groupcode"]} ])

                    currentliability= {"groupname":"Current Liabilities","orgcode":orgcode["orgcode"]}
                    result = self.con.execute(gkdb.groupsubgroups.insert(),currentliability)
                    result = self.con.execute(select([gkdb.groupsubgroups.c.groupcode]).where(and_(gkdb.groupsubgroups.c.groupname=="Current Liabilities",gkdb.groupsubgroups.c.orgcode==orgcode["orgcode"])))
                    grpcode = result.fetchone()
                    result = self.con.execute(gkdb.groupsubgroups.insert(),[{"groupname":"Provisions","orgcode":orgcode["orgcode"],"subgroupof":grpcode["groupcode"]},{"groupname":"Sundry Creditors for Expense","orgcode":orgcode["orgcode"],"subgroupof":grpcode["groupcode"]},{"groupname":"Sundry Creditors for Purchase","orgcode":orgcode["orgcode"],"subgroupof":grpcode["groupcode"]}])

                    directexpense= {"groupname":"Direct Expense","orgcode":orgcode["orgcode"]}
                    result = self.con.execute(gkdb.groupsubgroups.insert(),directexpense)

                    directincome= {"groupname":"Direct Income","orgcode":orgcode["orgcode"]}
                    result = self.con.execute(gkdb.groupsubgroups.insert(),directincome)

                    fixedassets= {"groupname":"Fixed Assets","orgcode":orgcode["orgcode"]}
                    result = self.con.execute(gkdb.groupsubgroups.insert(),fixedassets)
                    result = self.con.execute(select([gkdb.groupsubgroups.c.groupcode]).where(and_(gkdb.groupsubgroups.c.groupname=="Fixed Assets",gkdb.groupsubgroups.c.orgcode==orgcode["orgcode"])))
                    grpcode = result.fetchone()
                    result = self.con.execute(gkdb.groupsubgroups.insert(),[{"groupname":"Building","orgcode":orgcode["orgcode"],"subgroupof":grpcode["groupcode"]},{"groupname":"Furniture","orgcode":orgcode["orgcode"],"subgroupof":grpcode["groupcode"]},{"groupname":"Land","orgcode":orgcode["orgcode"],"subgroupof":grpcode["groupcode"]},{"groupname":"Plant & Machinery","orgcode":orgcode["orgcode"],"subgroupof":grpcode["groupcode"]} ])

                    indirectexpense= {"groupname":"Indirect Expense","orgcode":orgcode["orgcode"]}
                    result = self.con.execute(gkdb.groupsubgroups.insert(),indirectexpense)

                    indirectincome= {"groupname":"Indirect Income","orgcode":orgcode["orgcode"]}
                    result = self.con.execute(gkdb.groupsubgroups.insert(),indirectincome)

                    investment= {"groupname":"Investments","orgcode":orgcode["orgcode"]}
                    result = self.con.execute(gkdb.groupsubgroups.insert(),investment)
                    result = self.con.execute(select([gkdb.groupsubgroups.c.groupcode]).where(and_(gkdb.groupsubgroups.c.groupname=="Investments",gkdb.groupsubgroups.c.orgcode==orgcode["orgcode"])))
                    grpcode = result.fetchone()
                    result = self.con.execute(gkdb.groupsubgroups.insert(),[{"groupname":"Investment in Bank Deposits","orgcode":orgcode["orgcode"],"subgroupof":grpcode["groupcode"]},{"groupname":"Investment in Shares & Debentures","orgcode":orgcode["orgcode"],"subgroupof":grpcode["groupcode"]}, ])

                    loansasset= {"groupname":"Loans(Asset)","orgcode":orgcode["orgcode"]}
                    result = self.con.execute(gkdb.groupsubgroups.insert(),loansasset)

                    loansliab= {"groupname":"Loans(Liability)","orgcode":orgcode["orgcode"]}
                    result = self.con.execute(gkdb.groupsubgroups.insert(),loansliab)
                    result = self.con.execute(select([gkdb.groupsubgroups.c.groupcode]).where(and_(gkdb.groupsubgroups.c.groupname=="Loans(Liability)",gkdb.groupsubgroups.c.orgcode==orgcode["orgcode"])))
                    grpcode = result.fetchone()
                    result = self.con.execute(gkdb.groupsubgroups.insert(),[{"groupname":"Secured","orgcode":orgcode["orgcode"],"subgroupof":grpcode["groupcode"]},{"groupname":"Unsecured","orgcode":orgcode["orgcode"],"subgroupof":grpcode["groupcode"]} ])

                    reserves= {"groupname":"Reserves","orgcode":orgcode["orgcode"]}
                    result = self.con.execute(gkdb.groupsubgroups.insert(),reserves)

                    result = self.con.execute(select([gkdb.groupsubgroups.c.groupcode]).where(and_(gkdb.groupsubgroups.c.groupname=="Direct Income",gkdb.groupsubgroups.c.orgcode==orgcode["orgcode"])))
                    grpcode = result.fetchone()
                    if orgdata["orgtype"] == "Profit Making":
                        result = self.con.execute(gkdb.groupsubgroups.insert(),[{"groupname":"Capital","orgcode":orgcode["orgcode"]},{"groupname":"Miscellaneous Expenses(Asset)","orgcode":orgcode["orgcode"]}])

                        result = self.con.execute(gkdb.accounts.insert(),{"accountname":"Profit & Loss","groupcode":grpcode["groupcode"],"orgcode":orgcode["orgcode"]})

                    else:
                        result = self.con.execute(gkdb.groupsubgroups.insert(),{"groupname":"Corpus","orgcode":orgcode["orgcode"]})

                        result = self.con.execute(gkdb.accounts.insert(),{"accountname":"Income & Expenditure","groupcode":grpcode["groupcode"],"orgcode":orgcode["orgcode"]})

                    result = self.con.execute(select([gkdb.groupsubgroups.c.groupcode]).where(and_(gkdb.groupsubgroups.c.groupname=="Inventory",gkdb.groupsubgroups.c.orgcode==orgcode["orgcode"])))
                    grpcode = result.fetchone()
                    result = self.con.execute(gkdb.accounts.insert(),[{"accountname":"Closing Stock","groupcode":grpcode["groupcode"],"orgcode":orgcode["orgcode"]},{"accountname":"Stock at the Beginning","groupcode":grpcode["groupcode"],"orgcode":orgcode["orgcode"]}])

                    result = self.con.execute(select([gkdb.groupsubgroups.c.groupcode]).where(and_(gkdb.groupsubgroups.c.groupname=="Direct Expense",gkdb.groupsubgroups.c.orgcode==orgcode["orgcode"])))
                    grpcode = result.fetchone()
                    result = self.con.execute(gkdb.accounts.insert(),{"accountname":"Opening Stock","groupcode":grpcode["groupcode"],"orgcode":orgcode["orgcode"]})



                    userdata["orgcode"] = orgcode["orgcode"]
                    userdata["userrole"] = -1
                    result = self.con.execute(gkdb.users.insert().values(username = userdata["username"], userpassword=userdata["userpassword"], userrole = -1, userquestion = userdata["userquestion"], useranswer = userdata["useranswer"], orgcode=userdata["orgcode"]))
                    if result.rowcount==1:
                        result = self.con.execute(select([gkdb.users.c.userid]).where(and_(gkdb.users.c.username==userdata["username"], gkdb.users.c.userpassword== userdata["userpassword"], gkdb.users.c.orgcode==userdata["orgcode"])) )
                        if result.rowcount == 1:
                            record = result.fetchone()

                            token = jwt.encode({"orgcode":userdata["orgcode"],"userid":record["userid"]},gkcore.secret,algorithm='HS256')
                            self.con.close()
                            return {"gkstatus":enumdict["Success"],"token":token }
                        else:
                            self.con.close()
                            return {"gkstatus":enumdict["ConnectionFailed"]}
                    else:
                            self.con.close()
                            return {"gkstatus":enumdict["ConnectionFailed"]}
                except:
                    result = self.con.execute(gkdb.organisation.delete().where(gkdb.organisation.c.orgcode==orgcode["orgcode"]))
                    self.con.close()
                    return {"gkstatus":enumdict["ConnectionFailed"]}
            else:
                self.con.close()
                return {"gkstatus":enumdict["ConnectionFailed"]}
        except:
            self.con.close()
            return {"gkstatus":enumdict["ConnectionFailed"]}

    @view_config(route_name='organisation', request_method='GET',renderer='json')
    def getOrg(self):
        try:
            token = self.request.headers["gktoken"]
        except:
            return  {"gkstatus":  enumdict["UnauthorisedAccess"]}
        authDetails = authCheck(token)
        if authDetails["auth"]==False:
            return {"gkstatus":enumdict["UnauthorisedAccess"]}
        else:
            try:
                self.con = eng.connect()
                result = self.con.execute(select([gkdb.organisation]).where(gkdb.organisation.c.orgcode==authDetails["orgcode"]))
                row = result.fetchone()
                if(row["orgcity"]==None):
                    orgcity=""
                else:
                    orgcity=row["orgcity"]

                if(row["orgaddr"]==None):
                    orgaddr=""
                else:
                    orgaddr=row["orgaddr"]

                if(row["orgpincode"]==None):
                    orgpincode=""
                else:
                    orgpincode=row["orgpincode"]

                if(row["orgstate"]==None):
                    orgstate=""
                else:
                    orgstate=row["orgstate"]

                if(row["orgcountry"]==None):
                    orgcountry=""
                else:
                    orgcountry=row["orgcountry"]

                if(row["orgtelno"]==None):
                    orgtelno=""
                else:
                    orgtelno=row["orgtelno"]

                if(row["orgfax"]==None):
                    orgfax=""
                else:
                    orgfax=row["orgfax"]

                if(row["orgwebsite"]==None):
                    orgwebsite=""
                else:
                    orgwebsite=row["orgwebsite"]

                if(row["orgemail"]==None):
                    orgemail=""
                else:
                    orgemail=row["orgemail"]

                if(row["orgpan"]==None):
                    orgpan=""
                else:
                    orgpan=row["orgpan"]

                if(row["orgmvat"]==None):
                    orgmvat=""
                else:
                    orgmvat=row["orgmvat"]

                if(row["orgstax"]==None):
                    orgstax=""
                else:
                    orgstax=row["orgstax"]

                if(row["orgregno"]==None):
                    orgregno=""
                else:
                    orgregno=row["orgregno"]

                if(row["orgregdate"]==None):
                    orgregdate=""
                else:
                    orgregdate=row["orgregdate"]

                if(row["orgfcrano"]==None):
                    orgfcrano=""
                else:
                    orgfcrano=row["orgfcrano"]

                if(row["orgfcradate"]==None):
                    orgfcradate=""
                else:
                    orgfcradate=row["orgfcradate"]

                orgDetails={"orgname":row["orgname"], "orgtype":row["orgtype"], "yearstart":str(row["yearstart"]), "yearend":str(row["yearend"]),"orgcity":orgcity, "orgaddr":orgaddr, "orgpincode":orgpincode, "orgstate":orgstate, "orgcountry":orgcountry, "orgtelno":orgtelno, "orgfax":orgfax, "orgwebsite":orgwebsite, "orgemail":orgemail, "orgpan":orgpan, "orgmvat":orgmvat, "orgstax":orgstax, "orgregno":orgregno, "orgregdate":orgregdate, "orgfcrano":orgfcrano, "orgfcradate":orgfcradate, "roflag":row["roflag"], "booksclosedflag":row["booksclosedflag"],"invflag":row["invflag"],"billflag":row["billflag"],"invsflag":row["invsflag"]}
                self.con.close()
                return {"gkstatus":enumdict["Success"],"gkdata":orgDetails}
            except:
                self.con.close()
                return {"gkstatus":enumdict["ConnectionFailed"]}





    @view_config(request_method='PUT', renderer='json')
    def putOrg(self):
        token = self.request.headers['gktoken']
        authDetails = authCheck(token)
        if authDetails["auth"]==False:
            return {"gkstatus":enumdict["UnauthorisedAccess"]}
        else:
            try:
                self.con = eng.connect()
                user=self.con.execute(select([gkdb.users.c.userrole]).where(gkdb.users.c.userid == authDetails["userid"] ))
                userRole = user.fetchone()
                dataset = self.request.json_body
                if userRole[0]==-1:
                    result = self.con.execute(gkdb.organisation.update().where(gkdb.organisation.c.orgcode==authDetails["orgcode"]).values(dataset))
                    self.con.close()
                    return {"gkstatus":enumdict["Success"]}
                else:
                    {"gkstatus":  enumdict["BadPrivilege"]}
            except:
                self.con.close()
                return {"gkstatus":  enumdict["ConnectionFailed"]}

    @view_config(request_method='DELETE', renderer='json')
    def deleteOrg(self):
        token = self.request.headers['gktoken']
        authDetails = authCheck(token)
        if authDetails["auth"]==False:
            return {"gkstatus":enumdict["UnauthorisedAccess"]}
        else:
            try:
                self.con = eng.connect()
                user=self.con.execute(select([gkdb.users.c.userrole]).where(gkdb.users.c.userid == authDetails["userid"] ))
                userRole = user.fetchone()
                if userRole[0]==-1:
                    result = self.con.execute(gkdb.organisation.delete().where(gkdb.organisation.c.orgcode==authDetails["orgcode"]))
                    if result.rowcount == 1:
                        result = self.con.execute(select([func.count(gkdb.organisation.c.orgcode).label('ocount')]))
                        orgcount = result.fetchone()
                        if orgcount["ocount"]==0:
                            result = self.con.execute(gkdb.signature.delete())
                    self.con.close()
                    return {"gkstatus":enumdict["Success"]}
                else:
                    {"gkstatus":  enumdict["BadPrivilege"]}
            except:
                self.con.close()
                return {"gkstatus":  enumdict["ConnectionFailed"]}

    @view_config(request_method='GET',request_param="type=exists",renderer='json')
    def Orgexists(self):
        try:
            self.con = eng.connect()
            orgtype = self.request.params["orgtype"]
            orgname= self.request.params["orgname"]
            finstart = self.request.params["finstart"]
            finend = self.request.params["finend"]
            orgncount = self.con.execute(select([func.count(gkdb.organisation.c.orgcode).label('orgcode')]).where(and_(gkdb.organisation.c.orgname==orgname,gkdb.organisation.c.orgtype==orgtype, gkdb.organisation.c.yearstart==finstart,gkdb.organisation.c.yearend==finend)))
            org = orgncount.fetchone()
            if org["orgcode"] !=0:
                return {"gkstatus":enumdict["DuplicateEntry"]}
            else:
                return {"gkstatus":enumdict["Success"]}
        except:
            self.con.close()
            return {"gkstatus":  enumdict["ConnectionFailed"]}


    @view_config(request_param='orgcode', request_method='GET',renderer='json')
    def getOrgcode(self):
        try:
            token = self.request.headers["gktoken"]
        except:
            return  {"gkstatus":  enumdict["UnauthorisedAccess"]}
        authDetails = authCheck(token)
        if authDetails["auth"]==False:
            return {"gkstatus":enumdict["UnauthorisedAccess"]}
        else:
            return {"gkstatus":enumdict["Success"],"gkdata":authDetails["orgcode"]}


    @view_config(request_method='PUT', request_param="type=editorganisation", renderer='json')
    def editOrg(self):
        token = self.request.headers['gktoken']
        authDetails = authCheck(token)
        if authDetails["auth"]==False:
            return {"gkstatus":enumdict["UnauthorisedAccess"]}
        else:
            try:
                self.con =eng.connect()
                dataset = self.request.json_body
                result = self.con.execute(gkdb.organisation.update().where(gkdb.organisation.c.orgcode==dataset["orgcode"]).values(dataset))
                self.con.close()
                return {"gkstatus":enumdict["Success"]}
            except:
                self.con.close()
                return {"gkstatus":enumdict["ConnectionFailed"]}

    @view_config(request_method='PUT', request_param="type=getinventory", renderer='json')
    def getinventory(self):
        token = self.request.headers['gktoken']
        authDetails = authCheck(token)
        if authDetails["auth"]==False:
            return {"gkstatus":enumdict["UnauthorisedAccess"]}
        else:
            try:
                self.con = eng.connect()
                user=self.con.execute(select([gkdb.users.c.userrole]).where(gkdb.users.c.userid == authDetails["userid"] ))
                userRole = user.fetchone()
                dataset = self.request.json_body
                if userRole[0]==-1:
                    result = self.con.execute(gkdb.organisation.update().where(gkdb.organisation.c.orgcode==authDetails["orgcode"]).values(dataset))
                    self.con.close()
                    return {"gkstatus":enumdict["Success"]}
                else:
                    {"gkstatus":  enumdict["BadPrivilege"]}
            except:
                self.con.close()
                return {"gkstatus":enumdict["ConnectionFailed"]}

    @view_config(route_name='organisation', request_method='GET',request_param='attach=image', renderer='json')
    def getattachment(self):
        try:
            token = self.request.headers["gktoken"]
        except:
            return {"gkstatus": enumdict["UnauthorisedAccess"]}
        authDetails = authCheck(token)
        if authDetails['auth'] == False:
            return {"gkstatus":enumdict["UnauthorisedAccess"]}
        else:
            try:
                self.con = eng.connect()
                result = self.con.execute(select([gkdb.organisation.c.logo]).where(gkdb.organisation.c.orgcode==authDetails["orgcode"]))
                row=result.fetchone()
                return {"logo":row["logo"]}
            except:
                return {"gkstatus":enumdict["ConnectionFailed"]}
            finally:
                self.con.close()
