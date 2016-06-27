
"""
Copyright (C) 2013, 2014, 2015, 2016 Digital Freedom Foundation
  This file is part of GNUKhata:A modular,robust and Free Accounting System.

  GNUKhata is Free Software; you can redistribute it and/or modify
  it under the terms of the GNU Affero General Public License as
  published by the Free Software Foundation; either version 3 of
  the License, or (at your option) any later version.and old.stockflag = 's'

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


from gkcore import eng, enumdict
from gkcore.models import gkdb
from sqlalchemy.sql import select
import json
from sqlalchemy.engine.base import Connection
from sqlalchemy import and_, exc
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_defaults,  view_config
import jwt
import gkcore
from gkcore.views.api_login import authCheck




def getUserRole(userid):
	try:
		con = Connection
		con = eng.connect()
		uid=userid
		user=con.execute(select([gkdb.users.c.userrole]).where(gkdb.users.c.userid == uid ))
		row = user.fetchone()
		User = {"userrole":row["userrole"]}
		con.close();
		return {"gkstatus": gkcore.enumdict["Success"], "gkresult":User}
	except:
		return {"gkstatus":gkcore.enumdict["ConnectionFailed"] }

@view_defaults(route_name='users')
class api_user(object):
	def __init__(self,request):
		self.request = Request
		self.request = request
		self.con = Connection

	@view_config(request_method='POST',renderer='json')
	def addUser(self):
		try:
			token = self.request.headers["gktoken"]
		except:
			return  {"gkstatus":  gkcore.enumdict["UnauthorisedAccess"]}
		print authCheck(token)
		authDetails = authCheck(token)
		if authDetails["auth"] == False:
			return  {"gkstatus":  enumdict["UnauthorisedAccess"]}
		else:
			try:
				self.con = eng.connect()
				user=self.con.execute(select([gkdb.users.c.userrole]).where(gkdb.users.c.userid == authDetails["userid"] ))
				userRole = user.fetchone()
				dataset = self.request.json_body
				if userRole[0]==-1 or (userRole[0]==0 and dataset["userrole"]==1):
					print dataset
					dataset["orgcode"] = authDetails["orgcode"]
					result = self.con.execute(gkdb.users.insert(),[dataset])
					return {"gkstatus":enumdict["Success"]}
				else:
					return {"gkstatus":  enumdict["BadPrivilege"]}
			except exc.IntegrityError:
				return {"gkstatus":enumdict["DuplicateEntry"]}
			except:
				return {"gkstatus":gkcore.enumdict["ConnectionFailed"] }
			finally:
				self.con.close()
	@view_config(route_name='user', request_method='GET',renderer='json')
	def getUser(self):
		try:
			token = self.request.headers["gktoken"]
		except:
			return  {"gkstatus":  enumdict["UnauthorisedAccess"]}
		print authCheck(token)
		authDetails = authCheck(token)
		if authDetails["auth"] == False:
			return  {"gkstatus":  enumdict["UnauthorisedAccess"]}
		else:
			try:
				self.con = eng.connect()
				result = self.con.execute(select([gkdb.users]).where(gkdb.users.c.userid == authDetails["userid"] ))
				row = result.fetchone()
				User = {"userid":row["userid"], "username":row["username"], "userrole":row["userrole"], "userquestion":row["userquestion"], "useranswer":row["useranswer"], "userpassword":row["userpassword"]}
				print User
				return {"gkstatus": gkcore.enumdict["Success"], "gkresult":User}
			except:
				return {"gkstatus":gkcore.enumdict["ConnectionFailed"] }
			finally:
				self.con.close()
	@view_config(request_method='PUT', renderer='json')
	def editUser(self):
		try:
			token = self.request.headers["gktoken"]
		except:
			return  {"gkstatus":  gkcore.enumdict["UnauthorisedAccess"]}
		print authCheck(token)
		authDetails = authCheck(token)
		if authDetails["auth"] == False:
			return  {"gkstatus":  enumdict["UnauthorisedAccess"]}
		else:
			try:
				self.con = eng.connect()
				user=self.con.execute(select([gkdb.users.c.userrole]).where(gkdb.users.c.userid == authDetails["userid"] ))
				userRole = user.fetchone()
				dataset = self.request.json_body
				if userRole[0]==-1 or authDetails["userid"]==dataset["userid"]:
					result = self.con.execute(gkdb.users.update().where(gkdb.users.c.userid==dataset["userid"]).values(dataset))
					print result.rowcount
					return {"gkstatus":enumdict["Success"]}
				else:
					return {"gkstatus":  enumdict["BadPrivilege"]}
			except:
				return {"gkstatus":gkcore.enumdict["ConnectionFailed"] }
			finally:
				self.con.close()
	@view_config(request_method='GET', renderer ='json')
	def getAllUsers(self):
		try:
			token = self.request.headers["gktoken"]
		except:
			return  {"gkstatus":  gkcore.enumdict["UnauthorisedAccess"]}
		print authCheck(token)
		authDetails = authCheck(token)
		if authDetails["auth"] == False:
			return  {"gkstatus":  gkcore.enumdict["UnauthorisedAccess"]}
		else:
			try:
				self.con = eng.connect()
				#there is only one possibility for a catch which is failed connection to db.
				result = self.con.execute(select([gkdb.users.c.username,gkdb.users.c.userid,gkdb.users.c.userrole]).where(gkdb.users.c.orgcode==authDetails["orgcode"]).order_by(gkdb.users.c.username))
				users = []
				for row in result:
					users.append({"userid":row["userid"], "username":row["username"], "userrole":row["userrole"]})
				return {"gkstatus": gkcore.enumdict["Success"], "gkresult":users }
			except:
				return {"gkstatus":gkcore.enumdict["ConnectionFailed"] }
			finally:
				self.con.close()

	@view_config(request_method='DELETE', renderer ='json')
	def deleteuser(self):
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
				user=self.con.execute(select([gkdb.users.c.userrole]).where(gkdb.users.c.userid == authDetails["userid"] ))
				userRole = user.fetchone()
				dataset = self.request.json_body
				if userRole[0]==-1:
					result = self.con.execute(gkdb.users.delete().where(gkdb.users.c.userid==dataset["userid"]))
					return {"gkstatus":enumdict["Success"]}
				else:
					return {"gkstatus":  enumdict["BadPrivilege"]}
			except exc.IntegrityError:
				return {"gkstatus":enumdict["ActionDisallowed"]}
			except:
				return {"gkstatus":enumdict["ConnectionFailed"] }
			finally:
				self.con.close()
	@view_config(route_name='forgotpassword', request_method='GET',renderer='json')
	def getquestion(self):
		try:
				self.con = eng.connect()
				orgcode = self.request.params["orgcode"]
				username = self.request.params["username"]
				result = self.con.execute(select([gkdb.users]).where(and_(gkdb.users.c.username==username, gkdb.users.c.orgcode==orgcode)))
				if result.rowcount > 0:
					row = result.fetchone()
					User = {"userquestion":row["userquestion"], "userid":row["userid"]}
					return {"gkstatus": gkcore.enumdict["Success"], "gkresult": User}
				else:
					return {"gkstatus":enumdict["BadPrivilege"]}
		except:
			return  {"gkstatus":  enumdict["ConnectionFailed"]}
		finally:
			self.con.close()
	@view_config(route_name='forgotpassword', request_method='GET', request_param='type=securityanswer', renderer='json')
	def verifyanswer(self):
		try:
				self.con = eng.connect()
				userid = self.request.params["userid"]
				useranswer = self.request.params["useranswer"]
				result = self.con.execute(select([gkdb.users]).where(gkdb.users.c.userid==userid))
				row = result.fetchone()
				if useranswer==row["useranswer"]:
					return {"gkstatus":enumdict["Success"]}
				else:
					return {"gkstatus":enumdict["BadPrivilege"]}
		except:
			return  {"gkstatus":  enumdict["ConnectionFailed"]}
		finally:
			self.con.close()
	@view_config(route_name='forgotpassword', request_method='PUT', renderer='json')
	def verifypassword(self):
		try:
				self.con = eng.connect()
				dataset = self.request.json_body
				user = self.con.execute(select([gkdb.users]).where(and_(gkdb.users.c.userid==dataset["userid"], gkdb.users.c.useranswer==dataset["useranswer"])))
				if user.rowcount > 0:
					result = self.con.execute(gkdb.users.update().where(gkdb.users.c.userid==dataset["userid"]).values(dataset))
					return {"gkstatus":enumdict["Success"]}
				else:
					return {"gkstatus":enumdict["BadPrivilege"]}
		except:
			return  {"gkstatus":enumdict["ConnectionFailed"]}
		finally:
			self.con.close()
