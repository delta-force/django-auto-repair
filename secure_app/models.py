from django.db import models
from jsonfield import JSONField

# Create your models here.
class Request(models.Model):
	timestamp = models.IntegerField(default=0)
	full_url = models.CharField(max_length=200)
	host = models.CharField(max_length=50)
	url_path = models.CharField(max_length=50)
	is_good = models.BooleanField(default=True)
	param_map = JSONField()
	
	def __unicode__(self):
		return str(self.timestamp)
	
