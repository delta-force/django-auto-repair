import traceback
import sys
import time

class Repair(object):

    def process_request(self, request):
        # Open request log file
        f = open('requests.log', 'a')

        # Log GET requests
        if request.method == 'GET':
            f.write(str(time.strftime("%Y-%m-%d %H:%M:%S")) + ";" + str(request.META["REMOTE_ADDR"]) + ";" + str(request.get_host()) + ";" + str(request.get_full_path()) + ";" + str(request.method) + ";" + str(request.GET) + "\n")
            f.close()

        # Log POST requests
        if request.method == 'POST':
            f.write(str(time.strftime("%Y-%m-%d %H:%M:%S")) + ";" + str(request.META["REMOTE_ADDR"]) + ";" + str(request.get_host()) + ";" + str(request.get_full_path()) + ";" + str(request.method) + ";" + str(request.POST) + "\n")
            f.close()

        return

    def process_exception(self,request, exception):
        #print traceback.print_stack()
        try:
            type, value, tb = sys.exc_info()
            print type
            print value
            print traceback.extract_tb(tb)
        finally:
            del tb