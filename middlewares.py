import traceback
import sys

class Repair(object):

    def process_exception(self,request, exception):
        #print traceback.print_stack()
        try:
            type, value, tb = sys.exc_info()
            print type
            print value
            print traceback.extract_tb(tb)
        finally:
            del tb
       
