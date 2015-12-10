import datetime

from gkcore.models.meta import Base
from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    Unicode,	 #<- will provide Unicode field
    UnicodeText, #<- will provide Unicode text field
DateTime	 #<- time abstraction field
    )

class organisation(Base):
	__tablename__ = 'organisation'
	orgcode = Column(Integer, primary_key=True)
	orgname = Column(UnicodeText, nullable=False)
	orgtype = Column(UnicodeText, nullable=False)
	orgcity = Column(UnicodeText)
	orgaddr = Column(UnicodeText)
	orgpincode = Column(Unicode(30))
	orgstate = Column(UnicodeText)
	orgcountry = Column(UnicodeText)
	orgtelno = Column(UnicodeText)
	orgfax = Column(UnicodeText)
	orgwebsite = Column(UnicodeText)
	orgemail = Column(UnicodeText)
	orgpan = Column(UnicodeText)
	orgmvat = Column(UnicodeText)
	orgstax = Column(UnicodeText)
	orgregno = Column(UnicodeText)
	orgregdate = Column(UnicodeText)
	orgfcrano = Column(UnicodeText)
	orgfcradate = Column(UnicodeText)
	roflag = Column(Integer)
	booksclosedflag  = Column(Integer)
	def __init__(self, orgtype, orgname, orgaddr, orgcity, orgpincode, orgstate, orgcountry, orgtelno, orgfax, orgwebsite, orgemail, orgpan, orgmvat, orgstax, orgregno, orgregdate, orgfcrano, orgfcradate, roflag,booksclosedflag):	
		self.orgtype = orgtype
		self.orgname = orgname
		self.orgaddr = orgaddr
		self.orgcity = orgcity
		self.orgpincode = orgpincode
		self.orgstate = orgstate
		self.orgcountry = orgcountry
		self.orgtelno = orgtelno
		self.orgfax = orgfax
		self.orgwebsite = orgwebsite
		self.orgemail = orgemail
		self.orgpan = orgpan
		self.orgmvat = orgmvat
		self.orgstax = orgstax
		self.orgregno = orgregno
		self.orgregdate = orgregdate
		self.orgfcrano = orgfcrano
		self.orgfcradate = orgfcradate
		self.roflag = roflag
		self.booksclosedflag = booksclosedflag
