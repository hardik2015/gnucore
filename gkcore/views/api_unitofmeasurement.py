
"""
Copyright (C) 2013, 2014, 2015, 2016 Digital Freedom Foundation
Copyright (C) 2017, 2018, 2019, 2020 Digital Freedom Foundation & Accion Labs Pvt. Ltd.
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


from gkcore import eng, enumdict
from gkcore.models import gkdb
from sqlalchemy.sql import select
import json
from sqlalchemy.engine.base import Connection
from sqlalchemy import and_, exc, desc,func
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_defaults,  view_config
import gkcore
from gkcore.views.api_login import authCheck



@view_defaults(route_name='unitofmeasurement')
class api_unitOfMeasurement(object):
    def __init__(self,request):
        self.request = Request
        self.request = request
        self.con = Connection

    @view_config(request_method='POST',renderer='json')
    def addUnitOfMeasurement(self):
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
                dataset = self.request.json_body
                result = self.con.execute(gkdb.unitofmeasurement.insert(),[dataset])
                return {"gkstatus":enumdict["Success"]}
            except exc.IntegrityError:
                return {"gkstatus":enumdict["DuplicateEntry"]}
            except:
                return {"gkstatus":gkcore.enumdict["ConnectionFailed"] }
            finally:
                self.con.close()
    """
    This function is for the condition that the units of measurement which
    are associated with products can not be deleted.
    """         
    @view_config(request_param="qty=single", request_method='GET',renderer='json')
    def getUnitOfMeasurement(self):
        try:
            token = self.request.headers["gktoken"]
        except:
            return  {"gkstatus":  enumdict["UnauthorisedAccess"]}
        authDetails = authCheck(token)
        if authDetails["auth"] == False:
            return  {"gkstatus":  enumdict["UnauthorisedAccess"]}
        else:
            try:
                self.con = eng.connect()
                dataset = self.request.params
                result = self.con.execute(select([gkdb.unitofmeasurement]).where(gkdb.unitofmeasurement.c.uomid == dataset["uomid"]))
                row = result.fetchone()
                unitofmeasurement = {"uomid":row["uomid"], "unitname":row["unitname"], "conversionrate":"%.2f"%float(row["conversionrate"]), "subunitof":row["subunitof"], "description":row['description'], "sysunit":row['sysunit']}
                countresult = self.con.execute(select([func.count(gkdb.product.c.uomid).label('subcount')]).where(gkdb.product.c.uomid==row["uomid"]))
                countrow = countresult.fetchone()
                subcount= countrow["subcount"]
                if subcount > 0:
                    unitofmeasurement["flag"]="True"
                else:
                    unitofmeasurement["flag"]="False"
                return {"gkstatus": gkcore.enumdict["Success"], "gkresult":unitofmeasurement}
            except:
                return {"gkstatus":gkcore.enumdict["ConnectionFailed"] }
            finally:
                self.con.close()

    @view_config(request_method='PUT', renderer='json')
    def editunitofmeasurement(self):
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
                dataset = self.request.json_body
                result = self.con.execute(gkdb.unitofmeasurement.update().where(gkdb.unitofmeasurement.c.uomid==dataset["uomid"]).values(dataset))
                return {"gkstatus":enumdict["Success"]}
            except:
                return {"gkstatus":gkcore.enumdict["ConnectionFailed"] }
            finally:
                self.con.close()
    @view_config(request_param="qty=all", request_method='GET', renderer ='json')
    def getAllunitofmeasurements(self):
        try:
            token = self.request.headers["gktoken"]
        except:
            return  {"gkstatus":  gkcore.enumdict["UnauthorisedAccess"]}
        authDetails = authCheck(token)
        if authDetails["auth"] == False:
            return  {"gkstatus":  gkcore.enumdict["UnauthorisedAccess"]}
        else:
            try:
                self.con = eng.connect()
                #there is only one possibility for a catch which is failed connection to db.
                result = self.con.execute(select([gkdb.unitofmeasurement.c.unitname,gkdb.unitofmeasurement.c.uomid, gkdb.unitofmeasurement.c.description, gkdb.unitofmeasurement.c.subunitof, gkdb.unitofmeasurement.c.sysunit]).order_by(gkdb.unitofmeasurement.c.unitname))
                unitofmeasurements = []
                for row in result:
                    unitofmeasurements.append({"uomid":row["uomid"],"unitname":row["unitname"],"description":row['description'],"subunitof":row['subunitof'], "sysunit": row['sysunit']})
                return {"gkstatus": gkcore.enumdict["Success"], "gkresult":unitofmeasurements }
            except:
                return {"gkstatus":gkcore.enumdict["ConnectionFailed"] }
            finally:
                self.con.close()


    @view_config(request_method='DELETE', renderer ='json')
    def deleteunitofmeasurement(self):
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
                result = self.con.execute(gkdb.unitofmeasurement.delete().where(gkdb.unitofmeasurement.c.uomid==dataset["uomid"]))
                return {"gkstatus":enumdict["Success"]}
            except exc.IntegrityError:
                return {"gkstatus":enumdict["ActionDisallowed"]}
            except:
                return {"gkstatus":enumdict["ConnectionFailed"] }
            finally:
                self.con.close()
