import traceback
import sys
import time
from demo_webapp.models import Request

class Repair(object):

    def process_request(self, request):
        timestamp = str(int(time.time()))
        full_url = str(request.get_host()) + str(request.get_full_path())
        host = str(request.get_host())
        url_path = str(request.get_full_path())
        is_good = True

        # Log GET requests
        if request.method == 'GET':
            param_map = request.GET
        # Log POST requests
        if request.method == 'POST':
            param_map = request.POST

        #save to the database
        if len(param_map) != 0 and "delete_selected" not in str(param_map):
            r = Request(timestamp=timestamp, full_url=full_url, host=host, url_path=url_path, is_good=is_good, param_map=param_map)
            r.save()
        
        # AND/OR write to file 
        f = open('requests.log', 'a')
        f.write(timestamp + ";" + full_url + ";" + host + ";" + url_path + ";" + str(is_good) + ";" +  str(param_map) + "\n")
        f.close()
        return

    def process_exception(self,request, exception):
        #print traceback.print_stack()

        # From interpretter get name that caused exception
        # 
        # Use name to query the database, get newest one, update is_good to False
        #
        # Query for benign and malicious input
        #
        # Pass these two data sets to the GA
        #
        # Handle the results to update filter

        try:
            type, value, tb = sys.exc_info()
            print type
            print value
            print traceback.extract_tb(tb)
        finally:
            del tb