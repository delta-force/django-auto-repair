from django.db import models

# Create your models here.
class Request(models.Model):
        # This isnt that good to be unique
        # better to do ip||port||timestamp
        sessionid = models.TextField()
	timestamp = models.TextField()
	url_path = models.CharField(max_length=50)
	is_good = models.BooleanField(default=True)
        key = models.CharField(max_length=200)
        value = models.CharField(max_length=200)

	def __unicode__(self):
		return str(self.timestamp)

        def __str__(self):
            return self._to_str()
        def __repr__(self):
            return self._to_str()
        def _to_str(self):
            return self.sessionid + " " + self.timestamp + " " + self.key + ":" + self.value + " " + str(self.is_good)
class Filter(models.Model):
        '''
        The url path that is mapped to a view
        '''
	url_path = models.CharField(max_length=50)
        '''
        The parameter or field the regex should be applied too
        '''
	field_name = models.CharField(max_length=200, null=True)
        '''
        The regular expression to applie to the corresponding
        field name
        '''
	regex_filter = models.CharField(max_length=200)

	def __unicode__(self):
		return "url_path: " + self.url_path + ", field_name: " + self.field_name + ", regex_filter: " + self.regex_filter
	
