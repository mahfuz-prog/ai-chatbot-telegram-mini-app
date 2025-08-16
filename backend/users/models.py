from django.db import models
from django.utils import timezone

class User(models.Model):
	'''
	Represent a authorized user from telegram
	'''

	telegram_id = models.BigIntegerField(unique=True)
	username = models.CharField(max_length=255)
	joined = models.DateTimeField(default=timezone.now)

	class Meta:
		verbose_name = "User"
		verbose_name_plural = "Users"
		ordering = ['-joined']

	def __str__(self):
		return f"{self.username} -> tg: {self.telegram_id}"