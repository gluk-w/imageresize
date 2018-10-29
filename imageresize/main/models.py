import hashlib

from django.db import models

class Thumbnail(models.Model):
    hash = models.CharField(unique=True, max_length=64)
    src = models.URLField()
    result = models.FileField(upload_to="thumbnail")

    @classmethod
    def calculate_hash(cls, bucket_name, file_path, crop, rotate, resize) -> str:
        source = "::".join(map(str, [bucket_name, file_path, crop, rotate, resize]))
        return hashlib.sha256(source.encode()).hexdigest()
