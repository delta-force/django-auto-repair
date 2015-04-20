import traceback, sys, time, re
from secure_app.models import Request, Filter
from django.http import HttpResponse, HttpResponsePermanentRedirect
import logging
from garepair import GaRegexCreator

logger = logging.getLogger(__name__)

class Repair(object):
 

    def save_request(self, timestamp, host, full_url, url_path, param_map):
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
                        full_url=full_url, 
                        host=host, 
                        url_path=url_path, 
                        is_good=is_good, 
                        key=str(key), 
                        value=str(value)
                    )
                r.save()
                logger.info("SAVE time=" + timestamp + " url=" + full_url + " host=" + host + " path=" + url_path + " " + str(key) + "=" + str(value) )

    def has_evil_input(self, url_path, param_map):
        # Filter requests
        # Check if Filter objects' url path, form field name, and regex matches the request
        isEvil = False
        for f in Filter.objects.filter(url_path=url_path):
            field_name = getattr(f, 'field_name'); regex = getattr(f, 'regex_filter')
            
            requested_value = param_map[field_name]
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

    def process_request(self, request):
        timestamp = str(int(time.time()))
        full_url = str(request.get_host()) + str(request.get_full_path())
        host = str(request.get_host())
        url_path = str(request.get_full_path())

        param_map = self.get_param_map(request)
        if param_map:
            if self.has_evil_input(url_path, param_map):           
                return HttpResponse("Evil input detected -_-")
            else:
                #save to the database
                self.save_request(timestamp, host, full_url, url_path, param_map) 

        return

    def get_request_data(self, param_name, is_good):
        return [r.value for r in Request.filter(key = param_name, is_good = False)]

    
    def process_exception(self,request, exception):
        logger.debug("Processing exception...")        
        url_path = str(request.get_full_path())
        # From interpretter get name that caused exception
        vulnerable_name = "" 

        # Use request to query the database, so we can update the input to evil
        evil_req = Request.filter(url_path=url_path, key=vulnerable_name).order_by('timestamp')[0]
        evil_req.is_good = False

        # Query for benign and malicious input
        data_evil = self.get_request_data(vulnerable_name, False)
        data_benign = self.get_request_data(vulnerable_name, True)

        # Pass these two data sets to the GA
        ga = GaRegexCreator(data_evil, data_benign)
        regex = ga.create_regex()

        # Handle the results to update filter
        #Filter.objects.filter(order_by('')
        try:
            type, value, tb = sys.exc_info()
            print type
            print value
            print traceback.extract_tb(tb)
        finally:
            del tb



