@python_2_unicode_compatible
class Project(models.Model):
	name = models.CharField(max_length=256)
	start_date = models.DateField(blank=True, null=True)
	end_date = models.DateField(blank=True, null=True)
	def __str__(self):
		return self.name
	
	class Meta:
		ordering = ['start_date', 'name']