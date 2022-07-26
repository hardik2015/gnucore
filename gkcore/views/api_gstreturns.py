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
  Free Software Foundation, Inc.,51 Franklin Street,
  Fifth Floor, Boston, MA 02110, United States


Contributors:
"AKhil KP" <akhilkpdasan@protonmail.com>
'Prajkta Patkar' <prajakta@dff.org.in>
"""

from datetime import datetime
from ast import literal_eval
from copy import deepcopy
from sqlalchemy.engine.base import Connection
from collections import defaultdict
from sqlalchemy.sql import select, and_
from pyramid.request import Request
from pyramid.view import view_defaults,  view_config
from gkcore.views.api_login import authCheck
from gkcore import eng, enumdict
from gkcore.models.gkdb import (invoice,
                                customerandsupplier,
                                state,
                                product,
                                drcr,
                                unitofmeasurement)
from ast import literal_eval

def taxable_value(inv, productcode, con, drcr=False):
    """
    Returns taxable value of product given invoice/drcr note and productcode
    If dr/cr is due to change in quantity(drcrmode=18) then taxable value is
    present in reductionval dict with productcode as key else dr/cr must be a
    change in ppu and new rate has to be retrieved
    """

    rate, qty = list(inv["contents"][productcode].items())[0]
    query = (select([product.c.gsflag])
             .where(product.c.productcode == productcode))
    gsflag = con.execute(query).fetchone()[0]
    if gsflag == 19:
        qty = 1

    if drcr:
        if inv["drcrmode"] == 18:
            return float(inv["reductionval"][productcode])
        else:
            rate = inv["reductionval"][productcode]

    taxable_value = float(rate) * float(qty)
    if not drcr:
        taxable_value -= float(inv["discount"][productcode])
    return taxable_value


def cess_amount(inv, productcode, con, drcr=False):
    """
    Returns cess amount of product given invoice/drcr note and productcode
    """
    if inv["cess"].get(productcode) == 0 or inv["cess"] == {}:
        return 0
    else:
        cess_rate = float(inv["cess"][productcode])

        t_value = taxable_value(inv, productcode, con, drcr=drcr)
        cess_amount = t_value * cess_rate / 100

        return float(cess_amount)

def state_name_code(con, statename=None, statecode=None):
    """
    Returns statecode if statename is given
    Returns statename if statecode is given
    """
    if statename:
        query = (select([state.c.statecode])
                 .where(state.c.statename == statename))
    else:
        query = (select([state.c.statename])
                 .where(state.c.statecode == statecode))
    result = con.execute(query).fetchone()[0]
    return result


def product_level(inv, con, drcr=False):
    """
    Invoices/drcr notes can contain multiple products with different tax rates
    this function adds taxable value and cess amount of all products with same
    rate `data` is a dictionary with tax_rate as key and value is a dictionary
    containing taxable_value and cess_amount

    If drcr flag is True then products will be in reductionval dict
    If drcr is change in quantity then reductionval dict will contain a key
    quantities. Quantities dict contains the new quantity but that will be
    handled by taxable_value function so we can remove it
    """

    data = {}
    if drcr:
        products = list(inv["reductionval"].keys())
        if inv["drcrmode"] == 18:
            products.remove("quantities")
    else:
        products = inv["contents"]

    for prod in products:
        rate = float(inv["tax"][prod])
        if data.get(rate, None):
            data[rate]["taxable_value"] += taxable_value(inv, prod, con, drcr)
            data[rate]["cess"] += cess_amount(inv, prod, con, drcr)
        else:
            data[rate] = {}
            data[rate]["taxable_value"] = taxable_value(inv, prod, con, drcr)
            data[rate]["cess"] = cess_amount(inv, prod, con, drcr)

    return data


def b2b_r1(invoices, con):
    """
    Collects and formats data about invoices made to other registered taxpayers
    """

    try:
        def b2b_filter(inv):
            ts_code = state_name_code(con, statename=inv["taxstate"])
            if inv["gstin"].get(str(ts_code)):
                return True
            else:
                return False

        invs = list(filter(b2b_filter, invoices))

        b2b = []
        for inv in invs:
            ts_code = state_name_code(con, statename=inv["taxstate"])

            row = defaultdict()
            row["gstin"] = inv["gstin"][str(ts_code)]
            row["receiver"] = inv["custname"]
            row["invoice_number"] = inv["invoiceno"]
            row["invoice_date"] = inv["invoicedate"].strftime("%d-%b-%y")
            row["invoice_value"] = "%.2f" % float(inv["invoicetotal"])
            row["place_of_supply"] = "%d-%s" % (ts_code, inv["taxstate"])
            row["applicable_tax_rate"] = ""
            row["invoice_type"] = "Regular"
            row["ecommerce_gstin"] = ""
            if inv["reversecharge"] == "0":
                row["reverse_charge"] = "N"
            else:
                row["reverse_charge"] == "Y"

            for rate, tax_cess in list(product_level(inv, con).items()):
                prod_row = deepcopy(row)
                prod_row["taxable_value"] = "%.2f" % tax_cess["taxable_value"]
                prod_row["rate"] = "%.2f" % rate
                prod_row["cess"] = "%.2f" % tax_cess["cess"]
                b2b.append(prod_row)

        return {"status": 0, "data": b2b}
    except:
        return {"status": 3}


def b2cl_r1(invoices, con):
    """
    Collects and formats data about invoices for taxable outward supplies to
    consumers where:
        a)Place of supply is outside the state where the supplier is registered
        b)The total invoice value is more than Rs 2,50,000
    """

    try:
        def b2cl_filter(inv):
            ts_code = state_name_code(con, statename=inv["taxstate"])

            if inv["gstin"].get(str(ts_code)):
                return False
            if inv["taxstate"] == inv["sourcestate"]:
                return False
            if inv["invoicetotal"] > 250000:
                return True
            return False

        invs = list(filter(b2cl_filter, invoices))

        b2cl = []
        for inv in invs:

            ts_code = state_name_code(con, statename=inv["taxstate"])

            row = {}
            row["invoice_number"] = inv["invoiceno"]
            row["invoice_date"] = inv["invoicedate"].strftime("%d-%b-%y")
            row["invoice_value"] = "%.2f" % float(inv["invoicetotal"])
            row["place_of_supply"] = "%d-%s" % (ts_code, inv["taxstate"])
            row["applicable_tax_rate"] = ""
            row["ecommerce_gstin"] = ""
            row["sale_from_bonded_wh"] = "N"

            for rate, tax_cess in list(product_level(inv, con).items()):
                prod_row = deepcopy(row)
                prod_row["taxable_value"] = "%.2f" % tax_cess["taxable_value"]
                prod_row["rate"] = "%.2f" % rate
                prod_row["cess"] = "%.2f" % tax_cess["cess"]
                b2cl.append(prod_row)

        return {"status": 0, "data": b2cl}
    except:
        return {"status": 3}


def b2cs_r1(invoices, con):
    """
    Collects and formats data about supplies made to consumers
    of the following nature:
        a)Intra-State: Any value
        b)Inter-State: Invoice value Rs 2.5 lakhs or less

    Note: Here entries are not made invoice wise instead entries with same
    place_of_supply and taxrate are consolidated
    """

    try:
        def b2cs_filter(inv):
            ts_code = state_name_code(con, statename=inv["taxstate"])
            if inv["gstin"].get(str(ts_code)):
                return False
            if inv["taxstate"] == inv["sourcestate"]:
                return True
            if inv["invoicetotal"] <= 250000:
                return True
            return False

        invs = list(filter(b2cs_filter, invoices))

        b2cs = []
        for inv in invs:

            ts_code = state_name_code(con, statename=inv["taxstate"])

            row = {}
            row["type"] = "OE"
            row["place_of_supply"] = "%d-%s" % (ts_code, inv["taxstate"])
            row["applicable_tax_rate"] = ""
            row["ecommerce_gstin"] = ""

            for prod in inv["contents"]:
                prod_row = deepcopy(row)
                prod_row["taxable_value"] = taxable_value(inv, prod, con)
                prod_row["rate"] = "%.2f" % float(inv["tax"][prod])
                cess = cess_amount(inv, prod, con)
                prod_row["cess"] = cess_amount(inv, prod, con) if cess != "" else 0

                for existing in b2cs:
                    if (existing["place_of_supply"] == prod_row["place_of_supply"]
                            and existing["rate"] == prod_row["rate"]):

                        existing["taxable_value"] += prod_row["taxable_value"]
                        existing["cess"] += prod_row["cess"]
                        break
                else:
                    b2cs.append(prod_row)

        for row in b2cs:
            row["taxable_value"] = "%.2f" % row["taxable_value"]
            if row["cess"] == 0:
                row["cess"] = "0.00"
            else:
                row["cess"] = "%.2f" % row["cess"]

        return {"status": 0, "data": b2cs}
    except:
        return {"status": 3}


def cdnr_r1(drcr_all, con):
    """
    Collects and formats data about Credit/Debit Notes issued
    to the registered taxpayers
    """

    try:
        def cdnr_filter(inv):
            ts_code = state_name_code(con, statename=inv["taxstate"])
            if inv["gstin"].get(str(ts_code)):
                return True
            else:
                return False

        drcrs = list(filter(cdnr_filter, drcr_all))

        cdnr = []
        for note in drcrs:

            ts_code = state_name_code(con, statename=note["taxstate"])

            row = {}
            row["gstin"] = note["gstin"][str(ts_code)]
            row["receiver"] = note["custname"]
            row["invoice_number"] = note["invoiceno"]
            row["invoice_date"] = note["invoicedate"].strftime("%d-%b-%y")
            row["voucher_number"] = note["drcrno"]
            row["voucher_date"] = note["drcrdate"].strftime("%d-%b-%y")
            if note["dctypeflag"] == 4:
                row["document_type"] = "D"
            else:
                row["document_type"] = "C"
            row["place_of_supply"] = "%d-%s" % (ts_code, note["taxstate"])
            row["refund_voucher_value"] = "%.2f" % float(note["totreduct"])
            row["applicable_tax_rate"] = ""
            if note["taxflag"] == 7:
                row["pregst"] = "N"
            else:
                row["pregst"] = "Y"
            for rate, tax_cess in list(product_level(note, con, drcr=True).items()):
                prod_row = deepcopy(row)
                prod_row["taxable_value"] = "%.2f" % tax_cess["taxable_value"]
                prod_row["rate"] = "%.2f" % rate
                prod_row["cess"] = "%.2f" % tax_cess["cess"]
                cdnr.append(prod_row)

        return {"status": 0, "data": cdnr}
    except:
        return {"status": 3}


def cdnur_r1(drcr_all, con):
    """
    Collects and formats data about Credit/Debit Notes issued to
    unregistered person for interstate supplies
    """

    try:
        cdnur = []

        def cdnur_filter(drcr):
            ts_code = state_name_code(con, statename=drcr["taxstate"])
            if drcr["gstin"].get(str(ts_code)):
                return False
            if drcr["taxstate"] == drcr["sourcestate"]:
                return False
            if drcr["invoicetotal"] <= 250000:
                return False
            return True

        drcrs = list(filter(cdnur_filter, drcr_all))

        for note in drcrs:

            ts_code = state_name_code(con, statename=note["taxstate"])

            row = {}
            # ur_type can be ExportWithPay(EXPWP) / ExportWithoutPay(EXPWOP) / B2CL
            row["ur_type"] = "B2CL"
            row["invoice_number"] = note["invoiceno"]
            row["invoice_date"] = note["invoicedate"].strftime("%d-%b-%y")
            row["voucher_number"] = note["drcrno"]
            row["voucher_date"] = note["drcrdate"].strftime("%d-%b-%y")
            if note["dctypeflag"] == 4:
                row["document_type"] = "D"
            else:
                row["document_type"] = "C"
            row["place_of_supply"] = "%d-%s" % (ts_code, note["taxstate"])
            row["supply_type"] = "Inter State"
            row["refund_voucher_value"] = "%.2f" % float(note["totreduct"])
            row["applicable_tax_rate"] = ""
            if note["taxflag"] == 7:
                row["pregst"] = "N"
            else:
                row["pregst"] = "Y"
            for rate, tax_cess in list(product_level(note, con, drcr=True).items()):
                prod_row = deepcopy(row)
                prod_row["taxable_value"] = "%.2f" % tax_cess["taxable_value"]
                prod_row["rate"] = "%.2f" % rate
                prod_row["cess"] = "%.2f" % tax_cess["cess"]
                cdnur.append(prod_row)

        return {"status": 0, "data": cdnur}
    except:
        return {"status": 3}

def hsn_r1(orgcode,start,end,con):
    
    """
Retrieve all products data including product code,product description , hsn code, UOM.
Loop through product code and retrive all sale invoice related data[ppu,tax,taxtype,sourceState,destinationState] for that particular product code.

Store this data in following formats:
{'SGSTamt': '40.50', 'uqc': u'PCS', 'qty': '11.00', 'prodctname': u'Madhura Sugar', 'IGSTamt': '9.90', 'hsnsac': u'45678', 'taxableamt': '505.00', 'totalvalue': '541.10', 'CESSamt': '10.10'},................, {'grand_Value': '6089.20', 'grand_CESSValue': '68.20', 'grand_CGSTValue': '158.00', 'hsnNo': 2, 'grand_ttl_TaxableValue': '6260.00', 'grand_IGSTValue': '69.80'}]
"""
    try:
        orgcode = orgcode
        start = start
        end = end
        Final = []

        prodData = con.execute(select([product.c.productcode,product.c.gscode,product.c.productdesc,product.c.gsflag,product.c.uomid]).where(product.c.orgcode==orgcode))
        prodData_result = prodData.fetchall()
        for products in prodData_result:
            prodHSN = {"hsnsac":products["gscode"],"prodctname":products["productdesc"]}
            invData = con.execute("select contents ->> '%s' as content ,sourcestate,taxstate,discount ->>'%s' as disc,cess ->> '%s' as cess,tax ->> '%s' as tax from invoice where contents ? '%s' and orgcode = '%d' and inoutflag = '%d'and taxflag = '%d' and icflag = '%d' and invoicedate >= '%s' and invoicedate <= '%s'"%(products["productcode"],products["productcode"],products["productcode"],products["productcode"],products["productcode"],int(orgcode),15,7,9,str(start),str(end)))
            invoice_Data = invData.fetchall()

            ttl_Value = 0.00
            ttl_TaxableValue = 0.00
            ttl_CGSTval =0.00
            ttl_IGSTval = 0.00
            ttl_CESSval = 0.00
            ttl_qty = 0.00

            if invoice_Data != None and len(invoice_Data) > 0:
                for inv in invoice_Data:  
                    taxable_Value = 0.00
                    cn = literal_eval(inv["content"])
                    ds = float(literal_eval(inv["disc"]))
                    ppu = float(list(cn.keys())[0])
                    tx = float(literal_eval(inv["tax"]))
                    cs = float(literal_eval(inv["cess"]))
                    # check condition for product and service
                    if products["gsflag"] == 7:
                        qty = float(cn["%.2f"%float(ppu)])
                        ttl_qty += qty
                        taxable_Value = (ppu * qty) - ds
                        um = con.execute(select([unitofmeasurement.c.unitname]).where(unitofmeasurement.c.uomid == int(products["uomid"])))
                        unitrow = um.fetchone()
                        prodHSN["uqc"] = unitrow["unitname"]
                    else:
                        taxable_Value = ppu - ds
                        prodHSN["uqc"] = ""
                    ttl_TaxableValue += taxable_Value

                    # calculate state level and center level GST
                    if inv["sourcestate"] == inv["taxstate"]:
                        cgst = tx/2.00
                        cgst_amt = (taxable_Value * (cgst/100.00))
                        ttl_CGSTval += cgst_amt
                    else:
                        igst_amt = (taxable_Value *(tx/100.00)) 
                        ttl_IGSTval += igst_amt

                    cess_amount = (taxable_Value *(cs/100.00))
                    ttl_CESSval += cess_amount

                    ttl_Value = float(taxable_Value) + float(2*(ttl_CGSTval)) + float(ttl_CESSval)

                prodHSN["qty"] = "%.2f"%float(ttl_qty)
                prodHSN["totalvalue"] =  "%.2f"%float(float(ttl_TaxableValue) + (2*ttl_CGSTval) + float(ttl_IGSTval) + float(ttl_CESSval))
                prodHSN["taxableamt"] = "%.2f"%float(ttl_TaxableValue)
                prodHSN["SGSTamt"] = "%.2f"%float(ttl_CGSTval)
                prodHSN["IGSTamt"] =  "%.2f"%float(ttl_IGSTval)
                prodHSN["CESSamt"] = "%.2f"%float(ttl_CESSval)
                Final.append(prodHSN)
       
        return {"status": 0, "data": Final}
    except:
        return {"status": 3}

     

@view_defaults(route_name='gstreturns')
class GstReturn(object):
    def __init__(self, request):
        self.request = Request
        self.request = request
        self.con = Connection

    @view_config(request_method='GET',
                 request_param="type=r1",
                 renderer='json')
    def r1(self):
        
        """
        Returns JSON with b2b, b2cl, b2cs, cdnr, cdnur data required
        to file GSTR1
        Note: In sheets b2b, b2cl, cdnr, cdnur entries are according to
        GST tax rate
        Example:
            If Invoice contains 3 products with taxrates 6%, 12%, 6%
            respectively taxable value of Product 1 and Product 3 will be
            combined into single entry (taxable value and cess amount of these
            products will be added)
            Product 2 will have a separate entry
        """
        
        token = self.request.headers.get("gktoken", None)
        print("GST return")
        if token == None:
            return {"gkstatus": enumdict["UnauthorisedAccess"]}

        authDetails = authCheck(token)
        if authDetails["auth"] == False:
            return {"gkstatus":  enumdict["UnauthorisedAccess"]}

        try:
            self.con = eng.connect()
            dataset = self.request.params
            start_period = datetime.strptime(dataset["start"], "%Y-%m-%d")
            end_period = datetime.strptime(dataset["end"], "%Y-%m-%d")
            orgcode = authDetails["orgcode"]

            # invoices
            query = (select([invoice,
                            customerandsupplier.c.gstin,
                            customerandsupplier.c.custname])
                     .where(
                         and_(
                             invoice.c.invoicedate.between(
                                 start_period.strftime("%Y-%m-%d"),
                                 end_period.strftime("%Y-%m-%d")
                             ),
                             invoice.c.inoutflag == 15,
                             invoice.c.taxflag == 7,
                             invoice.c.orgcode == orgcode,
                             invoice.c.custid == customerandsupplier.c.custid,
                         )
                     ))
            invoices = self.con.execute(query).fetchall()

            # debit/credit notes
            query1 = (select([drcr, invoice, customerandsupplier])
                     .select_from(
                        drcr.join(invoice).join(customerandsupplier)
                     )
                     .where(
                         and_(
                             drcr.c.drcrdate.between(
                                 start_period.strftime("%Y-%m-%d"),
                                 end_period.strftime("%Y-%m-%d")
                             ),
                             invoice.c.inoutflag == 15,
                             drcr.c.orgcode == orgcode,
                         )
                     ))

            drcrs_all = self.con.execute(query1).fetchall()

            gkdata = {}
            gkdata["b2b"] = b2b_r1(invoices, self.con).get("data", [])
            gkdata["b2cl"] = b2cl_r1(invoices, self.con).get("data", [])
            gkdata["b2cs"] = b2cs_r1(invoices, self.con).get("data", [])
            gkdata["cdnr"] = cdnr_r1(drcrs_all, self.con).get("data", [])
            gkdata["cdnur"] = cdnur_r1(drcrs_all, self.con).get("data", [])
            gkdata["hsn1"] = hsn_r1(orgcode,dataset["start"],dataset["end"], self.con).get("data", [])

            self.con.close()
            return {"gkresult": 0, "gkdata": gkdata}


        except:
            return {"status": 3}
