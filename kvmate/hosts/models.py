from django.db import models

class Host(models.Model):
    hostname = models.CharField(max_length=30, primary_key=True)
    is_on = models.BooleanField()
    has_salt = models.BooleanField()
    upgrades = models.PositiveSmallIntegerField(default=1, blank=True, null=True)
    def __unicode__(self):
        return 'KVMate.Host %s [On: %d]' % (self.hostname, self.is_on)
