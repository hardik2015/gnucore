
"""
Copyright (C) 2014 2015 2016 Digital Freedom Foundation
  This file is part of GNUKhata:A modular,robust and Free Accounting System.

  GNUKhata is Free Software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as
  published by the Free Software Foundation; either version 3 of
  the License, or (at your option) any later version.and old.stockflag = 's'

  GNUKhata is distributed in the hope that it will be useful, but
  WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public
  License along with GNUKhata (COPYING); if not, write to the
  Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
  Boston, MA  02110-1301  USA59 Temple Place, Suite 330,


Contributor: 
"Krishnakant Mane" <kk@gmail.com>
"Ishan Masdekar " <imasdekar@dff.org.in>
"Navin Karkera" <navin@dff.org.in>

"""


from gkcore import eng, enumdict
from gkcore.views.api_login import authCheck
from gkcore.models.gkdb import accounts, vouchers, groupsubgroups 
from sqlalchemy.sql import select
import json 
from sqlalchemy.engine.base import Connection
from sqlalchemy import and_, exc 
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_defaults,  view_config
from sqlalchemy.ext.baked import Result
from datetime import datetime
con = Connection
con = eng.connect()

"""
purpose:
This class is the resource to generate reports,
Such as Trial Balance, Ledger, Cash flowe, Balance sheet etc.

connection rules:
con is used for executing sql expression language based queries,
while eng is used for raw sql execution.
routing mechanism:
@view_defaults is used for setting the default route for crud on the given resource class.
if specific route is to be attached to a certain method, or for giving get, post, put, delete methods to default route, the view_config decorator is used.
For other predicates view_config is generally used.
This class has single route with only get as method.
Depending on the request_param, different methods will be called on the route given in view_default.
  
"""

@view_defaults(route_name='report' , request_method='GET')
class api_reports(object):
	def __init__(self,request):
		self.request = Request
		self.request = request

	#calculateBalance is a private method so we won't expose it as REST method.
	def calculateBalance(self,orgCode,accountName,financialStart,calculateFrom,calculateTo):
		"""
		purpose:
		This is a private method which will return
		*groupname for the provided account
		*opening balance for the range
		*opening balance type
		*closing balance for the selected range
		*closing balance type
		*Total Dr for the range
		* total Cr for the range.
		Input parameters are:
		*Orgcode
		*accountname
		*financialfrom
		*calculatefrom
		*calculateto
		
		first we will get the groupname for the provided account.
		note that the given account may be associated with a subgroup for which we must get the group.
		Then we get the opening balance and if it is not 0 then decide if it is a Dr or Cr balance based on the group.
		Then the Total Dr and Cr is calculated.
		If the calculate from is ahead of financial start, then the entire process is repeated.
		This function is called by all reports in this resource.
		we will be initializing all function level variables here.
		"""
		groupName = ""
		openingBalance = 0.00
		balanceBrought = 0.00
		currentBalance = 0.00
		ttlCrBalance = 0.00
		ttlDrBalance = 0.00
		openingBalanceType = ""
		ttlDrUptoFrom = 0.00
		ttlCrUptoFrom = 0.00
		balType = ""
		{"balbrought":balanceBrought,"curbal":currentBalance,"totalcrbal":ttlCrBalance,"totaldrbal":ttlDrBalance,"baltype":balType,"openbaltype":openingBalanceType,"grpname":groupName}
		groupData = eng.execute("select groupname from groupsubgroups where groupcode = (select subgroupof from groupsubgroups where groupcode=(select groupcode from accounts where accountname ="+accountName+"and orgcode = orgCode ))")
		groupRecord = groupData.fetchone()
		groupName = groupRecord["groupname"]
		#now similarly we will get the opening balance for this account.
		obData = con.execute(select([accountName.c.openingbalance]).where(and_(accounts.c.accountname == accountName, accounts.c.orgcode == orgCode)) )
		ob = obData.fetchone()
		oepningBalance = ob["openingbalance"]
		financialYearStartDate = datetime.strptime(financialStart,"%Y-%m-%d")
		calculateFromDate = datetime.strptime(calculateFrom,"%Y-%m-%d")
		calculateToDate = datetime.strptime(calculateTo,"%Y-%m-%d")
		if financialYearStartDate == calculateFromDate:
			if openingBalance == 0:
				balanceBrought = 0
			if openingBalance < 0 and (groupName == 'Current Assets' or groupName == 'Fixed Assets'or groupName == 'Investments' or groupName == 'Loans(Asset)' or groupName == 'Miscellaneous Expenses(Asset)'):
				balanceBrought = abs(openingBalance)
				openingBalanceType = "Cr"
				balType = "Cr"

			if openingBalance > 0 and (groupName == 'Current Assets' or groupName == 'Fixed Assets'or groupName == 'Investments' or groupName == 'Loans(Asset)' or groupName == 'Miscellaneous Expenses(Asset)'):
				balanceBrought = openingBalance
				openingBalanceType = "Dr"
				balType = "Dr"

			if openingBalance < 0 and (groupName == 'Corpus' or groupName == 'Capital'or groupName == 'Current Liabilities' or groupName == 'Loans(Liability)' or groupName == 'Reserves'):
				balanceBrought = abs(openingBalance)
				openingBalanceType = "Dr"
				balType = "Dr"

			if openingBalance > 0 and (groupName == 'Corpus' or groupName == 'Capital'or groupName == 'Current Liabilities' or groupName == 'Loans(Liability)' or groupName == 'Reserves'):
				balanceBrought = openingBalance
				openingBalanceType = "Cr"
				balType = "Cr"
		else:
			#account code to be retrieved from account name
			accountCodeData = con.execute(select([accounts.c.accountcode]).where(and_(accounts.c.accountname == accountName, accounts.c.orgcode == orgCode)))
			accountRow = accountCodeData.fetchone()
			accountcode = accountRow["accountcode"]
			tdrfrm = eng.execute("select sum(cast(drs->>'%d' as float)) as total from vouchers where delflag = false and voucherdate >='%s' and voucherdate < '%s'"%(accountcode,financialStart,calculateFrom))
			tcrfrm = eng.execute("select sum(cast(crs->>'%d' as float)) as total from vouchers where delflag = false and voucherdate >='%s' and voucherdate < '%s'"%(accountcode,financialStart,calculateFrom))
			tdrRow = tdrfrm.fetchone()
			tcrRow= tcrfrm.fetchone()
			ttlCrUptoFrom = tcrRow['total']
			ttlDrUptoFrom = tdrRow['total']
			if ttlCrUptoFrom == None:
				ttlCrUptoFrom = 0.00
			if ttlDrUptoFrom == None:
				ttlDrUptoFrom = 0.00
			
			if openingBalance == 0:
				balanceBrought = 0.00
			if openingBalance < 0 and (groupName == 'Current Assets' or groupName == 'Fixed Assets'or groupName == 'Investments' or groupName == 'Loans(Asset)' or groupName == 'Miscellaneous Expenses(Asset)'):
				ttlCrUptoFrom = ttlCrUptoFrom +abs(openingBalance)
			if openingBalance > 0 and (groupName == 'Current Assets' or groupName == 'Fixed Assets'or groupName == 'Investments' or groupName == 'Loans(Asset)' or groupName == 'Miscellaneous Expenses(Asset)'):
				ttlDrUptoFrom = ttlDrUptoFrom +openingBalance
			if openingBalance < 0 and (groupName == 'Corpus' or groupName == 'Capital'or groupName == 'Current Liabilities' or groupName == 'Loans(Liability)' or groupName == 'Reserves'):
				ttlDrUptoFrom = ttlDrUptoFrom+ abs(openingBalance)
			if openingBalance > 0 and (groupName == 'Corpus' or groupName == 'Capital'or groupName == 'Current Liabilities' or groupName == 'Loans(Liability)' or groupName == 'Reserves'):
				ttlCrUptoFrom = ttlCrUptoFrom + openingBalance
			if ttlDrUptoFrom >	ttlCrUptoFrom:
				balanceBrought = ttlDrUptoFrom - ttlCrUptoFrom
				balType = "Dr"
				openingBalanceType = "Dr"				
			if ttlCrUptoFrom >	ttlDrUptoFrom:
				balanceBrought = ttlCrUptoFrom - ttlDrUptoFrom
				balType = "Cr"
				openingBalanceType = "Cr"
		accountCodeData = con.execute(select([accounts.c.accountcode]).where(and_(accounts.c.accountname == accountName, accounts.c.orgcode == orgCode)))
		accountRow = accountCodeData.fetchone()
		accountcode = accountRow["accountcode"]
		tdrfrm = eng.execute("select sum(cast(drs->>'%d' as float)) as total from vouchers where delflag = false and voucherdate >='%s' and voucherdate < '%s'"%(accountcode,financialStart,calculateFrom))
		tcrfrm = eng.execute("select sum(cast(crs->>'%d' as float)) as total from vouchers where delflag = false and voucherdate >='%s' and voucherdate < '%s'"%(accountcode,financialStart,calculateFrom))
		tdrRow = tdrfrm.fetchone()
		tcrRow= tcrfrm.fetchone()
		ttlDrBalance = tdrRow['total']
		ttlCrBalance = tcrRow['total']
		if ttlCrBalance == None:
			ttlCrBalance = 0.00
		if ttlDrBalance == None:
			ttlDrBalance = 0.00
		if balType =="Dr":
			ttlDrBalance = ttlDrBalance + balanceBrought
		if balType =="Cr":
			ttlCrBalance = ttlCrBalance + balanceBrought
		if ttlDrBalance > ttlCrBalance :
			currentBalance = ttlDrBalance - ttlCrBalance
			balType = "Dr"
		if ttlCrBalance > ttlDrBalance :
			currentBalance = ttlCrBalance - ttlDrBalance
			balType = "Cr"
		return {"balbrought":balanceBrought,"curbal":currentBalance,"totalcrbal":ttlCrBalance,"totaldrbal":ttlDrBalance,"baltype":balType,"openbaltype":openingBalanceType,"grpname":groupName}
	@view_config(request_param='trialbalance')
	def trialBalance(self):
		
		""" 
		There are 3 types of trial balance:
		1 is net
		2 is gross
		3 is extended
	"""
		try:
			token = self.request.headers["gktoken"]
		except:
			return  {"gkstatus":  enumdict["UnauthorisedAccess"]}
		authDetails = authCheck(token)
		if authDetails["auth"]==False:
			return {"gkstatus":enumdict["UnauthorisedAccess"]}
		else:
			try:
				if int(self.request.params["tbtype"])  == 1:
					accountCodeData = con.execute(select([accounts.c.accountcode]).where(accounts.c.orgcode==authDetails["orgcode"] ) )
					accountCodeRecords = accountCodeData.fetchall()
					

			except:
				return {"gkstatus":enumdict["ConnectionFailed"]}	