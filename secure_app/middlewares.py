import traceback, sys, time, re
import inspect

from django.contrib.sessions.backends.db import SessionStore
from secure_app.models import Request, Filter
from django.db.models import Count
from django.http import HttpResponse, HttpResponsePermanentRedirect, QueryDict

import logging
from garepair import GaRegexCreator
import pprint
logger = logging.getLogger(__name__)
import requests
#sh = logging.StreamHandler()
#logger.addHandler(sh)

class Repair(object):
    '''
    Repair a fatal crash that occurs by creating a regex filter to
    allow "good" input and block "bad" input. Bad input is input that 
    causes a fatal crash.

    The current design is vulnerable to sophisticated training data poisioning
    such that a malicious user inserts bad data that gets counted as good. 
    When the regex is created, it cant tell the difference between good and 
    bad.
    '''

    REQUEST_ID = "req_id"

    def save_request(self,sessionid, timestamp, url_path, param_map):
        '''
        Save every request so it can be later used for training. 
        Each requst name and value is stored
        '''
        
        #TODO shouldnt store name=value pair duplicates

        is_good = True
        # TODO Why is there a delete_seleted condition? what does it do
        if len(param_map) != 0 and "delete_selected" not in str(param_map):
            for key, value in param_map.iteritems():
                r = Request(
                        timestamp=timestamp, 
                        sessionid=sessionid,
                        url_path=url_path, 
                        is_good=is_good, 
                        key=str(key), 
                        value=str(value)
                    )
                r.save()
                logger.info("SAVE time=" + timestamp + " path=" + url_path + " " + str(key) + "=" + str(value) )

    def has_evil_input(self, url_path, param_map):
        # Filter requests
        # Check if Filter objects' url path, form field name, and regex matches the request
        isEvil = False
        for f in Filter.objects.filter(url_path=url_path):
            field_name = getattr(f, 'field_name'); regex = getattr(f, 'regex_filter')
             
            requested_value = param_map[field_name]
            logger.debug("Field " + field_name + " filter " + regex + " for value " + requested_value)
            # The filters are inclusions, if the input doesnt
            # match the accecpt regex then its malicious 
            if not re.match(regex, str(requested_value)):
                isEvil = True
                break
        return isEvil

    def get_param_map(self, request):
        # Log GET requests
        if request.method == 'GET':
            param_map = request.GET
        # Log POST requests
        elif request.method == 'POST':
            param_map = request.POST
        return param_map

    def taint_input(self, request):
        '''
        Taint the input so we can determine if one of these inputs
        caused an exception 
        '''
        def taint_request_data(req):
            for k in req:
                req[k] = req[k].taint_src(k)
        
        # set request to mutable and mark all of its inputs as tainted
        request.POST._mutable = True
        taint_request_data(request.POST)
        request.POST._mutable = False
        
        request.GET._mutable = True
        taint_request_data(request.GET)
        request.GET._mutable = False

    def process_request(self, request):
        if not request.session.exists(request.session.session_key):
            logger.debug("creating new session")
            request.session.create()
        sessionid = request.session.session_key
        logger.debug(sessionid)
#        pprint.pprint(request.META, stream=sys.stderr)
        timestamp = str(time.time())
        # we define a request id and tie it to the 
        # request object so there is a way during an exception 
        # we can retrieve information saved from the database
        request.META[self.REQUEST_ID] = timestamp
        url_path = str(request.get_full_path())
  
        self.taint_input(request)
        
        param_map = self.get_param_map(request)
        if param_map:
        
            if self.has_evil_input(url_path, param_map):
                html = "<div align=\"center\"><h1>Chuck blocks all EVIL!</h1><br/><img src=\"http://masternorris.com/images/content/Chuck_Norris_kick-MasterNorris_com.jpg\"></div>"
                return HttpResponse(html)           
                #return HttpResponse("Evil input detected -_-")
            else:
                #save to the database
                self.save_request(sessionid, timestamp, url_path, param_map) 

        return

    def get_request_data(self, param_name, is_good):
        return [r.value for r in Request.objects.filter(key = param_name, is_good = is_good)]

    def _remove_poisoned_data(self, sessionid):
        '''
        If an exception occurs we want to remove all the data entered by 
        this malicous user because it may have been poisoned
        '''
        Request.objects.filter(sessionid=sessionid, is_good=True).delete()

    def make_request_to_clone(self, method, url_path, payload):

        url = "http://127.0.0.1:8888" + url_path
        status_code = None
        if method == 'GET':
            r = requests.get(url, params=payload) 
            status_code = r.status_code
        else: 
            r = requests.post(url, data=payload) 
            status_code = r.status_code
        return status_code

    def identify_evil_input(self, request, url_path, bad_time):
        logger.info("Identifying evil input...")
        params = self.get_param_map(request)

        #Get the first good record
        good_record_timestamp = Request.objects.filter(url_path=url_path, is_good = True).exclude(timestamp=bad_time).values('timestamp').annotate(total=Count('timestamp'))[0]['timestamp']

        
        key_vals = Request.objects.filter(timestamp=good_record_timestamp).values('key','value')
        logger.debug("Good key valu pairs " + str(key_vals))

        #Need to make at most request sof rnumber of params
        for i in range(len(key_vals)):

            #For the request
            payload = {}
            for row in range(len(key_vals)):
                key = key_vals[row]['key']
                #Use possible bad input
                if row == i:
                    val = params[key]
                else: 
                    val = key_vals[row]['value']
                
        #        val = "hi"
                payload[key] = val

            status_code = self.make_request_to_clone(request.method, url_path, payload)
            logger.debug("Request made " + str(payload) + " return " + str(status_code))
            if status_code == 500:
                evil_key = key_vals[i]['key']
                evil_input = params[evil_key]
                logger.debug("Found the evil input! key=" + evil_key + " val=" + evil_input)

                return evil_key
        return None

    def process_exception(self,request, exception):
        
        sessionid = request.session.session_key
        #try:
        id = request.META[self.REQUEST_ID]
        logger.debug("Processing exception..." + id + " " + sessionid)        

        url_path = str(request.get_full_path())
       
        ty, val, tb = sys.exc_info()
       
	def renderframe(frame):
            filename, lineno, function, code_context, index = inspect.getframeinfo(tb.tb_frame)
            print "Visiting frame for function {} () @ {}: {}".format(function, filename, lineno)
	    print code_context[0]

        while tb.tb_next:
            renderframe(tb.tb_frame)
            tb = tb.tb_next
        
        frame = tb.tb_frame
        renderframe(frame)

	print "Found the frame where exception occured"
	
        args, varargs, keywords, locals = inspect.getargvalues(frame)
	
        vulnerable_name = None

        for name in args:
            v = locals[name]
            if hasattr(v, "istainted") and v.istainted():
                vulnerable_name = v.sources()[0][0]
                print "Found tainted data in function argument '{}'".format(name)
                print "{} originated from the '{}' input field".format(name, vulnerable_name)
		break
 
        #evil_key = self.identify_evil_input(request, url_path, id)
        # From interpretter get name that caused exception
        #TODO REMOVE ME, I AM HERE FOR TESTING
        #vulnerable_name = evil_key 
        
        if vulnerable_name == None:
            logger.error("Could not find name, :-(")
            return

        # Use request to query the database, so we can update the input to evil
        evil_req = Request.objects.filter(timestamp=id, url_path=url_path, key=vulnerable_name)[0]
        evil_req.is_good = False
        evil_req.save()
        self._remove_poisoned_data(sessionid)

        # Query for benign and malicious input
        data_evil = self.get_request_data(vulnerable_name, False)
        logger.debug("================EVIL=================")
        logger.debug(str(data_evil))
        data_benign = self.get_request_data(vulnerable_name, True)
        logger.debug("================GOOD=================")
        logger.debug(str(data_benign))

        # Pass these two data sets to the GA
        ga = GaRegexCreator(data_evil, data_benign, verbose=False)
        regex, gens, good_score, bad_score, = ga.create_regex()

        filter, created = Filter.objects.get_or_create(url_path=url_path,field_name=vulnerable_name) 
        filter.regex_filter = regex
        filter.save()
        logger.debug("good " + str(good_score) + " bad " + str(bad_score))
        logger.debug("Filter " + regex + " has been applied for " + vulnerable_name + " in " + str(gens) + " gens")
        
        #try:        
        #    type, value, tb = sys.exc_info()
        #    logger.debug(type)
        #    logger.debug(value)
        #    logger.debug(traceback.extract_tb(tb))
        #except Exception as e:
        #    print e
            #del tb
            # Save the regex so it can filter evil things next time
        #except Exception as e:
        #    logger.error("Unknown exception " + str(e))

        #finally:
            #return HttpResponsePermanentRedirect(request.get_full_path().split("?")[0])
        html = "<div align=\"center\"><h1>Chuck doesn't make EXCEPTIONS!</h1><br/><img src=\"http://cdn.redalertpolitics.com/files/2014/06/chuck-norris-ap-photo.jpg\"></div>"
        return HttpResponse(html)
        #     pass
