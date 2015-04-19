import traceback, sys, time, re
from secure_app.models import Request, Filter
from django.http import HttpResponse, HttpResponsePermanentRedirect

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

        # Filter requests
        # Check if Filter objects' url path, form field name, and regex matches the request
        isEvil = False
        for key, value in param_map.iteritems():
            for f in Filter.objects.all():
                url_path_f = getattr(f, 'url_path'); field_name_f = getattr(f, 'field_name'); regex_filter_f = getattr(f, 'regex_filter')
                x = re.compile(regex_filter_f)
                if url_path == url_path_f and key == field_name_f and x.search(str(value)):
                    isEvil = True
                    return HttpResponse("Evil input detected -_-")
                    
        #save to the database
        if len(param_map) != 0 and "delete_selected" not in str(param_map):
            r = Request(timestamp=timestamp, full_url=full_url, host=host, url_path=url_path, is_good=is_good, param_map=param_map)
            r.save()
        
        # AND/OR write to file 
        f = open('secure_app_requests.log', 'a')
        f.write(timestamp + ";" + full_url + ";" + host + ";" + url_path + ";" + str(is_good) + ";" +  str(param_map) + "\n")
        f.write("Is request evil?: " + str(isEvil) + "\n")
        f.close()
        return

    def process_exception(self,request, exception):

        # From interpretter get name that caused exception
        # 
        # Use name to query the database, get newest one, update is_good to False
        #
        # Query for benign and malicious input
        #
        # Pass these two data sets to the GA
        #
        # Handle the results to update filter
        #Filter.objects.filter(order_by('')
        try:
            type, value, tb = sys.exc_info()
            print type
            print value
            print traceback.extract_tb(tb)
        finally:
            del tb
