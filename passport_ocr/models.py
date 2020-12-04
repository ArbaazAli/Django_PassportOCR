from django.db import models

class PassportImage(models.Model):
    name = models.CharField(max_length=20, null=True)
    passport_img = models.FileField(upload_to='img/')

    def __str__(self):
        return self.name