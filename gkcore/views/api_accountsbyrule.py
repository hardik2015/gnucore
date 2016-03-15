


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
from gkcore.models.gkdb import accounts, groupsubgroups
from sqlalchemy.sql import select
import json 
from sqlalchemy.engine.base import Connection
from sqlalchemy import and_
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_defaults,  view_config
from sqlalchemy.ext.baked import Result

con = Connection
con = eng.connect()


@view_defaults(route_name='accountsbyrule',request_method='GET' )
class api_accountsbyrule(object):
	def __init__(self,request):
		self.request = Request
		self.request = request

	@view_config(request_param="type=contra", renderer='json')
	def contra(self):
		try:
			token = self.request.headers["gktoken"]
		except:
			return {"gkstatus": enumdict["UnauthorisedAccess"]}
		authDetails = authCheck(token)
		if authDetails["auth"] == False:
			return {"gkstatus": enumdict["UnauthorisedAccess"]}
		else:
			try:
				contraAccs = eng.execute("select accountname , accountcode from accounts where groupcode in (select groupcode from groupsubgroups where groupname in ('Bank','Cash')and orgcode = %d) and orgcode = %d"%(authDetails["orgcode"],authDetails["orgcode"]))
				contraList = []
				for contraRow in contraAccs:
					contraList.append({"accountname":contraRow["accountname"], "accountcode":contraRow["accountcode"]})
				return{"gkstatus":enumdict["Success"],"gkresult": contraList}
			except:
				return {"gkstatus":enumdict["ConnectionFailed"]}
			
	@view_config(request_param="type=journal", renderer='json')
	def journal(self):
		try:
			token = self.request.headers["gktoken"]
		except:
			return {"gkstatus": enumdict["UnauthorisedAccess"]}
		authDetails = authCheck(token)
		if authDetails["auth"] == False:
			return {"gkstatus": enumdict["UnauthorisedAccess"]}
		else:
			try:
				journalAccs = eng.execute("select accountname , accountcode from accounts where groupcode not in (select groupcode from groupsubgroups where groupname in ('Bank','Cash')and orgcode = %d) and orgcode = %d"%(authDetails["orgcode"],authDetails["orgcode"]))
				journalList = []
				for contraRow in journalAccs:
					journalList.append({"accountname":contraRow["accountname"], "accountcode":contraRow["accountcode"]})
				return{"gkstatus":enumdict["Success"],"gkresult": journalList}
			except:
				return {"gkstatus":enumdict["ConnectionFailed"]}
			
	@view_config(request_param="type=payment", renderer='json')
	def payment(self):
		try:
			token = self.request.headers["gktoken"]
		except:
			return {"gkstatus": enumdict["UnauthorisedAccess"]}
		authDetails = authCheck(token)
		if authDetails["auth"] == False:
			return {"gkstatus": enumdict["UnauthorisedAccess"]}
		else:
			try:
				if self.request.params['side']=="Dr":
					try:	
						accs = eng.execute("select accountname , accountcode from accounts where orgcode = %d and accountname not in ('Opening Stock','Closing Stock','Stock at the Beginning','Profit & Loss','Income & Expenditure') and groupcode not in (select groupcode from groupsubgroups where groupname in ('Bank','Cash') and orgcode = %d)"%(authDetails["orgcode"],authDetails["orgcode"]))
						list = []
						for row in accs:
							list.append({"accountname":row["accountname"], "accountcode":row["accountcode"]})
						return{"gkstatus":enumdict["Success"],"gkresult": list}
					except:
						return {"gkstatus":enumdict["ConnectionFailed"]}
				if self.request.params['side']=="Cr":
					try:	
						accs = eng.execute("select accountname , accountcode from accounts where groupcode in (select groupcode from groupsubgroups where groupname in ('Bank','Cash')and orgcode = %d) and orgcode = %d"%(authDetails["orgcode"],authDetails["orgcode"]))
						list = []
						for row in accs:
							list.append({"accountname":row["accountname"], "accountcode":row["accountcode"]})
						return{"gkstatus":enumdict["Success"],"gkresult": list}
					except:
						return {"gkstatus":enumdict["ConnectionFailed"]}	
			except:
					return {"gkstatus":enumdict["ConnectionFailed"]}
	@view_config(request_param="type=receipt", renderer='json')
	def receipt(self):
		try:
			token = self.request.headers["gktoken"]
		except:
			return {"gkstatus": enumdict["UnauthorisedAccess"]}
		authDetails = authCheck(token)
		if authDetails["auth"] == False:
			return {"gkstatus": enumdict["UnauthorisedAccess"]}
		else:
			try:
				if self.request.params['side']=="Cr":
					try:	
						accs = eng.execute("select accountname , accountcode from accounts where orgcode = %d and accountname not in ('Opening Stock','Closing Stock','Stock at the Beginning','Profit & Loss','Income & Expenditure') and groupcode not in (select groupcode from groupsubgroups where groupname in ('Bank','Cash') and orgcode = %d)"%(authDetails["orgcode"],authDetails["orgcode"]))
						list = []
						for row in accs:
							list.append({"accountname":row["accountname"], "accountcode":row["accountcode"]})
						return{"gkstatus":enumdict["Success"],"gkresult": list}
					except:
						return {"gkstatus":enumdict["ConnectionFailed"]}
				if self.request.params['side']=="Dr":
					try:	
						accs = eng.execute("select accountname , accountcode from accounts where groupcode in (select groupcode from groupsubgroups where groupname in ('Bank','Cash')and orgcode = %d) and orgcode = %d"%(authDetails["orgcode"],authDetails["orgcode"]))
						list = []
						for row in accs:
							list.append({"accountname":row["accountname"], "accountcode":row["accountcode"]})
						return{"gkstatus":enumdict["Success"],"gkresult": list}
					except:
						return {"gkstatus":enumdict["ConnectionFailed"]}
			except:
					return {"gkstatus":enumdict["ConnectionFailed"]}	