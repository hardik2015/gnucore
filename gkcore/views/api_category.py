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
"Vaibhav Kurhe" <vaibhav.kurhe@gmail.com>
"""
#imports contain sqlalchemy modules,
#enumdict containing status messages,
#eng for executing raw sql,
#gkdb from models for all the alchemy expressed tables.
#view_default for setting default route
#view_config for per method configurations predicates etc.
from gkcore import eng, enumdict
from gkcore.views.api_login import authCheck
from gkcore.models import gkdb
from sqlalchemy.sql import select
import json
from sqlalchemy.engine.base import Connection
from sqlalchemy import and_, exc,alias, or_, func
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_defaults,  view_config
from sqlalchemy.ext.baked import Result
from sqlalchemy.sql.expression import null
from gkcore.models.meta import dbconnect
"""
purpose:
This class is the resource to create, update, read and delete categories and subcategories
connection rules:
con is used for executing sql expression language based queries,
while eng is used for raw sql execution.
routing mechanism:
@view_defaults is used for setting the default route for crud on the given resource class.
if specific route is to be attached to a certain method, or for giving get, post, put, delete methods to default route, the view_config decorator is used.
For other predicates view_config is generally used.
"""
"""
default route to be attached to this resource.
refer to the __init__.py of main gkcore package for details on routing url
"""

@view_defaults(route_name='categories')
class category(object):
	#constructor will initialise request.
	def __init__(self,request):
		self.request = Request
		self.request = request
		self.con = Connection
		print "category initialized"

	@view_config(request_method='POST',renderer='json')
	def addCategory(self):
		try:
			token = self.request.headers["gktoken"]
		except:
			return  {"gkstatus":  gkcore.enumdict["UnauthorisedAccess"]}
		authDetails = authCheck(token)
		if authDetails["auth"]==False:
			return {"gkstatus":enumdict["UnauthorisedAccess"]}
		else:
			try:
				self.con = eng.connect()
				dataset = self.request.json_body
				dataset["orgcode"] = authDetails["orgcode"]
				result = self.con.execute(gkdb.categorysubcategories.insert(),[dataset])
				if result.rowcount==1:
					result = self.con.execute(select([gkdb.categorysubcategories.c.categorycode]).where(and_(gkdb.categorysubcategories.c.orgcode==authDetails["orgcode"], gkdb.categorysubcategories.c.categoryname==dataset["categoryname"])))
					row = result.fetchone()
					return {"gkstatus":enumdict["Success"],"gkresult":row["categorycode"]}
				else:
					return {"gkstatus":enumdict["ConnectionFailed"]}
			except:
				return {"gkstatus":enumdict["ConnectionFailed"]}
			finally:
				self.con.close()

	@view_config(request_method='GET', renderer ='json')
	def getAllCategories(self):
		try:
			token = self.request.headers["gktoken"]
		except:
			return  {"gkstatus": enumdict["UnauthorisedAccess"]}
		authDetails = authCheck(token)
		if authDetails["auth"]==False:
			return {"gkstatus":enumdict["UnauthorisedAccess"]}
		else:
			try:
				self.con = eng.connect()
				result = self.con.execute(select([gkdb.categorysubcategories.c.categoryname,gkdb.categorysubcategories.c.categorycode,gkdb.categorysubcategories.c.subcategoryof]).where(gkdb.categorysubcategories.c.orgcode==authDetails["orgcode"]).order_by(gkdb.categorysubcategories.c.categoryname))
				categories = []
				for row in result:
					countResult = self.con.execute(select([func.count(gkdb.categorysubcategories.c.categorycode).label('subcount') ]).where(gkdb.categorysubcategories.c.subcategoryof== row["categorycode"]))
					countrow = countResult.fetchone()
					subcount = countrow["subcount"]
					categories.append({"categoryname":row["categoryname"], "categorycode":row["categorycode"],"subcategoryof":row["subcategoryof"],"subcount":subcount})
				return {"gkstatus": enumdict["Success"], "gkresult":categories}
			except:
				return {"gkstatus":enumdict["ConnectionFailed"] }
			finally:
				self.con.close()

	@view_config(request_method='GET',request_param="type=topcategories",renderer='json')
	def getTopCategories(self):
		try:
			token = self.request.headers["gktoken"]
		except:
			return  {"gkstatus": enumdict["UnauthorisedAccess"]}
		authDetails = authCheck(token)
		if authDetails["auth"]==False:
			return {"gkstatus":enumdict["UnauthorisedAccess"]}
		else:
			try:
				self.con = eng.connect()
				result = self.con.execute(select([gkdb.categorysubcategories.c.categoryname,gkdb.categorysubcategories.c.categorycode]).where(and_(gkdb.categorysubcategories.c.orgcode == authDetails["orgcode"],gkdb.categorysubcategories.c.subcategoryof  == null())).order_by(gkdb.categorysubcategories.c.categoryname))
				topcategories = []
				for row in result:
					countResult = self.con.execute(select([func.count(gkdb.categorysubcategories.c.categorycode).label('subcount') ]).where(gkdb.categorysubcategories.c.subcategoryof== row["categorycode"]))
					countrow = countResult.fetchone()
					subcount = countrow["subcount"]
					topcategories.append({"categoryname":row["categoryname"], "categorycode":row["categorycode"],"subcount":subcount})
				return{"gkstatus":enumdict["Success"],"gkresult":topcategories}
			except:
				return {"gkstatus":enumdict["ConnectionFailed"] }
			finally:
				self.con.close()


	@view_config(request_method='GET',request_param="type=parent",renderer='json')
	def getParent(self):
		try:
			token = self.request.headers["gktoken"]
		except:
			return  {"gkstatus": enumdict["UnauthorisedAccess"]}
		authDetails = authCheck(token)
		if authDetails["auth"]==False:
			return {"gkstatus":enumdict["UnauthorisedAccess"]}
		else:
			try:
				self.con = eng.connect()
				subcategoryof = self.request.params['subcategoryof']
				result = self.con.execute(select([gkdb.categorysubcategories]).where(gkdb.categorysubcategories.c.categorycode  == subcategoryof) )
				row = result.fetchone()
				parentcategory = {"categorycode":row["categorycode"],"categoryname":row["categoryname"],"subcategoryof":row["subcategoryof"]}
				return{"gkstatus":enumdict["Success"],"gkresult":parentcategory}
			except:
				return {"gkstatus":enumdict["ConnectionFailed"] }
			finally:
				self.con.close()


	@view_config(request_method='GET',request_param="type=children",renderer='json')
	def getChildren(self):
		try:
			token = self.request.headers["gktoken"]
		except:
			return  {"gkstatus": enumdict["UnauthorisedAccess"]}
		authDetails = authCheck(token)
		if authDetails["auth"]==False:
			return {"gkstatus":enumdict["UnauthorisedAccess"]}
		else:
			try:
				self.con = eng.connect()
				categorycode = self.request.params['categorycode']
				result = self.con.execute(select([gkdb.categorysubcategories]).where(gkdb.categorysubcategories.c.subcategoryof == categorycode) )
				categories = []
				for row in result:
					countResult = self.con.execute(select([func.count(gkdb.categorysubcategories.c.categorycode).label('subcount') ]).where(gkdb.categorysubcategories.c.subcategoryof== row["categorycode"]))
					countrow = countResult.fetchone()
					subcount = countrow["subcount"]
					categories.append({"categoryname":row["categoryname"], "categorycode":row["categorycode"],"subcategoryof":row["subcategoryof"],"subcount":subcount})
				return {"gkstatus": enumdict["Success"], "gkresult":categories}

			except exc.IntegrityError:
				self.con.close()
				return {"gkstatus":enumdict["DuplicateEntry"]}
			except:
				return {"gkstatus":enumdict["ConnectionFailed"] }
			finally:
				self.con.close()

	@view_config(request_method='GET',request_param="type=single",renderer='json')
	def getCategory(self):
		try:
			token = self.request.headers["gktoken"]
		except:
			return  {"gkstatus": enumdict["UnauthorisedAccess"]}
		authDetails = authCheck(token)
		if authDetails["auth"]==False:
			return {"gkstatus":enumdict["UnauthorisedAccess"]}
		else:
			try:
				self.con = eng.connect()
				category_code = self.request.params['categorycode']
				result = self.con.execute(select([gkdb.categorysubcategories]).where(gkdb.categorysubcategories.c.categorycode  == category_code) )
				row = result.fetchone()
				category = {"categorycode":row["categorycode"],"categoryname":row["categoryname"],"subcategoryof":row["subcategoryof"],"tax":row["tax"]}
				return{"gkstatus":enumdict["Success"],"gkresult":category}
			except:
				return {"gkstatus":enumdict["ConnectionFailed"] }
			finally:
				self.con.close()

	@view_config(request_method='PUT', renderer='json')
	def editCategory(self):
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
				dataset = self.request.json_body
				result = self.con.execute(gkdb.categorysubcategories.update().where(gkdb.categorysubcategories.c.categorycode==dataset["categorycode"]).values(dataset))
				return {"gkstatus":enumdict["Success"]}
			except:
				return {"gkstatus":enumdict["ConnectionFailed"]}
			finally:
				self.con.close()

	@view_config(request_method='DELETE', renderer ='json')
	def deleteCategory(self):
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
				dataset = self.request.json_body
				result = self.con.execute(gkdb.categorysubcategories.delete().where(gkdb.categorysubcategories.c.categorycode==dataset["categorycode"]))
				return {"gkstatus":enumdict["Success"]}
			except exc.IntegrityError:
				return {"gkstatus":enumdict["ActionDisallowed"]}
			except:
				return {"gkstatus":enumdict["ConnectionFailed"] }
			finally:
				self.con.close()
