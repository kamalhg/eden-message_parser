# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

""" Message Parsing API

    API to parse messages:
        - currently Email only.

    Message Parsing subroutines are defined here.
    These subroutines define different sets of parsing rules.
    Imported by private/templates/<template>
    where <template> is the "default" template by default.

    @author: Ashwyn Sharma <ashwyn1092[at]gmail.com>
    
    @copyright: 2012 (c) Sahana Software Foundation
    @license: MIT

    Permission is hereby granted, free of charge, to any person
    obtaining a copy of this software and associated documentation
    files (the "Software"), to deal in the Software without
    restriction, including without limitation the rights to use,
    copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the
    Software is furnished to do so, subject to the following
    conditions:

    The above copyright notice and this permission notice shall be
    included in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
    OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
    NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
    HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
    WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
    OTHER DEALINGS IN THE SOFTWARE.

"""

__all__ = ["S3Parsing"]

import string

from gluon import current

#from s3utils import soundex

import sys
application = current.request.application
module_name = 'applications.%s.modules.s3.s3utils'%application
__import__(module_name)
mymodule = sys.modules[module_name]
soundex = mymodule.soundex
                
# =============================================================================
class S3Parsing(object):
    """
       Message Parsing Framework.
    """
  
    # -------------------------------------------------------------------------
    @staticmethod
    def parse_person(pquery="", name="", sender=""):
        """
            Search for People
        """

        
        T = current.T
        db = current.db
        s3db = current.s3db

        result = []
        reply = ""
        
        table = s3db.pr_person
        query = (table.deleted ==False)
        query = query & (current.auth.s3_accessible_query("read", table))
        rows = db(query).select(table.pe_id,
                                table.first_name,
                                table.middle_name,
                                table.last_name)
        _name = soundex(str(name))
        for row in rows:
            if (_name == soundex(row.first_name)) or \
               (_name == soundex(row.middle_name)) or \
               (_name == soundex(row.last_name)):
                presult = dict(name = row.first_name, id = row.pe_id)
                result.append(presult)

        if len(result) > 1:
            return T("Multiple Matches")
        if len(result) == 1:
            reply = result[0]["name"]
            table = s3db.pr_contact
            if "email" in pquery:
                query = (table.pe_id == result[0]["id"]) & \
		    (table.contact_method == "EMAIL")
                query = query & \
		    (current.auth.s3_accessible_query("read", table))
                recipient = db(query).select(table.value,
		                             orderby = table.priority,
		                             limitby=(0, 1)).first()
                if recipient:
                    reply = "%s Email->%s" % (reply, recipient.value)
                else:
                    reply = "%s 's Email Not available!"%reply
            if "phone" in pquery:
                query = (table.pe_id == result[0]["id"]) & \
		    (table.contact_method == "SMS")
                query = query & \
		    (current.auth.s3_accessible_query("read", table))
                recipient = db(query).select(table.value,
		                             orderby = table.priority,
		                             limitby=(0, 1)).first()
                if recipient:
                    reply = "%s Mobile->%s" % (reply,
		                               recipient.value)
                else:
                    reply = "%s 's Mobile Contact Not available!"%reply

        if len(result) == 0:
            return T("No Match")

        return reply
        
    
    # ---------------------------------------------------------------------
    @staticmethod
    def parse_hospital(pquery="", name="", sender=""):
        """
           Search for Hospitals
        """

        T = current.T
        db = current.db
        s3db = current.s3db
        reply = ""
        result = []

        table = s3db.hms_hospital
        query = (table.deleted == False)
        query = query & \
	    (current.auth.s3_accessible_query("read", table))
        rows = db(query).select(table.id,
	                        table.name,
	                        table.aka1,
	                        table.aka2,
	                        table.phone_emergency,
	                        table.clinical_status,
	                        table.facility_status,
	                        table.security_status,
	                        )
        _name = soundex(str(name))
        for row in rows:
            if (_name == soundex(row.name)) or \
	       (_name == soundex(row.aka1)) or \
	       (_name == soundex(row.aka2)):
                result.append(row)

        if len(result) > 1:
            return T("Multiple Matches")

        if len(result) == 1:
            hospital = result[0]
            reply = "%s %s (%s) " % (reply, hospital.name,
	                             T("Hospital"))
            if "phone" in pquery:
                reply = reply + "Phone->" + str(hospital.phone_emergency)
            if "facility" in pquery:
                reply = reply + "Facility status " + \
		    str(table.facility_status.\
		        represent(hospital.facility_status))
            if "clinical" in pquery:
                reply = reply + "Clinical status " + \
		    str(table.clinical_status.\
		        represent(hospital.clinical_status))
            if "security" in pquery:
                reply = reply + "Security status " + \
		    str(table.security_status.\
		        represent(hospital.security_status))

        if len(result) == 0:
            return T("No Match")

        return reply

    # ---------------------------------------------------------------------
    @staticmethod
    def parse_org(pquery="", name="", sender=""):
        """
           Search for Organisations
        """

        T = current.T
        db = current.db
        s3db = current.s3db
	
        result = []
        reply = ""

        table = s3db.org_organisation
        query = (table.deleted == False)
        query = query & \
	    (current.auth.s3_accessible_query("read", table))
        rows = db(query).select(table.id,
	                        table.name,
	                        table.donation_phone,
	                        table.acronym)
        _name = soundex(str(name))
        for row in rows:
            if (_name == soundex(row.name)) or \
	       (_name == soundex(row.acronym)):
                result.append(row)

        if len(result) > 1:
            return T("Multiple Matches")

        if len(result) == 1:
            org = result[0]
            reply = "%s %s (%s) " % (reply, org.name,
	                             T("Organization"))
            if "phone" in pquery:
                reply = reply + "Phone->" + str(org.donation_phone)
            if "office" in pquery:
                otable = s3db.org_office
                query = (otable.organisation_id == org.id)
                query = query & \
		    (current.auth.s3_accessible_query("read", otable))
                office = db(query).select(otable.address, \
		                          limitby=(0, 1)).first()
                reply = reply + "Address->" + office.address
        if len(result) == 0:
            return T("No Match")

        return reply
    # -------------------------------------------------------------------------
    @staticmethod
    def parse_ireport(lat="", lon="", text="", message="", sender=""):
        """
            Parse Replies To Deployment Request.
        """

        T = current.T
        db = current.db
        s3db = current.s3db
        msg = current.msg
        rhtable = s3db.irs_ireport_human_resource
        ctable = s3db.pr_contact
        htable = s3db.hrm_human_resource
        ptable = s3db.pr_person_user
        words = string.split(message)
        message = ""
        reponse = ""
        ireport = False
        reply = ""
        category = ""
        name = ""
        comments = False

        rtable = s3db.irs_ireport
        gtable = s3db.gis_location
        if text:
            info = string.split(text)
            name = info[len(info)-1]
            for a in range(0, len(info)-1):
                category = category + info[a] + " "
	
        #@ToDo: Check for an existing location in DB
        #records = db(gtable.id>0).select(gtable.id, \
        #                                 gtable.lat, gtable.lon)
        #for record in records:
        #	try:
        #	    if "%.6f"%record.lat == str(lat) and \
        #	       "%.6f"%record.lon == str(lon):
        #		location_id = record.id
        #		break
        #	except:
        #	    pass
	    
        if lat and lon and name and category:
            location_id = gtable.insert(name="Incident:%s" % name,
	                                lat=lat,
	                                lon=lon)
            rtable.insert(name=name,
	                  message="",
	                  category=category,
	                  location_id=location_id)			
	    
            db.commit()
            return "Incident Report Logged!"
	
        for word in words:
            if "SI#" in word and not ireport:
                report = word.split("#")[1]
                report = int(report)
                ireport = True
            elif (soundex(word) == soundex("Yes")) and ireport and not comments:
                response = True
                comments = True
	    elif soundex(word) == soundex("No") and ireport and not comments:
                response = False
                comments = True
            elif comments:
                message += word + " "

        if not ireport:
            reply = """Expected format:SI#1 Yes/No Comments"""
        else:
            query = (ctable.contact_method == "EMAIL") & \
	        (ctable.value == sender)
            responder = db(query).select(ctable.pe_id, limitby=(0, 1)).first()
            if responder:
                query = (ptable.pe_id == responder.pe_id)
                human_resource = db(query).select(ptable.id,
		                                  limitby=(0, 1)).first()
	    
                if human_resource:
                    query = (htable.person_id == human_resource.id)
                    person = db(query).select(htable.id, limitby=(0, 1)).first()
                    if person:
                        query = (rhtable.ireport_id == report) & \
			    (rhtable.human_resource_id == person.id)
                        db(query).update(reply=message,
			                 response=response)
                        reply = "Response Logged in the Report (Id: %d )"%report

        if not reply:
            reply = "Send help to see how to respond!"
        db.commit()
        return reply

# END =========================================================================
