import tempfile
import requests
from PIL import Image, ImageFile
from django.http import HttpResponsePermanentRedirect
from django.core.files import File
from django.shortcuts import render
# from django.core.files.storage import default_storage
from rest_framework.exceptions import ValidationError
# from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Thumbnail

def health_view(request):
    return render(request, "health.html")


class ResizeViewSet(APIView):
    ALLOWED_BUCKETS = ['clutch-image-resize']
    # Following flags are set in `.validate_params()`
    bucket_name = None
    file_path = None
    crop = None
    rotate = None
    resize = None

    def get(self, request):
        self._validate_params(request)

        image_hash = Thumbnail.calculate_hash(self.bucket_name, self.file_path, self.crop, self.rotate, self.resize)
        th = Thumbnail.objects.filter(hash=image_hash).first()
        # Check file exists and does not need to be regenerated
        # if th and not default_storage.exists(th.result.path):  # django-storages does not support python3
        #     th.delete()
        #     th = None  # force regeneration
        if not th:
            img = self._process_image()
            th = self._store_result(img, image_hash)

        return HttpResponsePermanentRedirect(th.result.url)

    def _validate_params(self, request):
        self.bucket_name = request.query_params.get("bucket")
        if self.bucket_name not in self.ALLOWED_BUCKETS:
            raise ValidationError("Prohibited bucket name")

        self.file_path = request.query_params.get("file")
        if not self.file_path:
            raise ValidationError("File path is required")

        crop = request.query_params.get("crop")  # comma separated values: left, upper, right, lower
        if crop:
            crop_values = crop.split(',')
            if len(crop_values) != 4:
                raise ValidationError("Crop parameter must be comma separated list of values: left, upper, right, lower")
            try:
                self.crop = map(lambda x: int(x), crop_values)
            except ValueError:
                raise ValidationError("Crop parameters must be a list of numbers")

        resize = request.query_params.get("resize")
        if resize:
            width_and_height = resize.split('x')
            if len(width_and_height) != 2:
                raise ValidationError("New width and height must be separated by \"x\", e.g.: 100x100")
            try:
                self.resize = (int(width_and_height[0]), int(width_and_height[1]))
            except ValueError:
                raise ValidationError("New width and height must be integers")

        rotate = request.query_params.get("rotate")
        if rotate:
            try:
                self.rotate = float(rotate)
            except ValueError:
                raise ValidationError("Invalid angle")

    def _process_image(self):
        img = self._download_image(self.bucket_name, self.file_path)
        # img = Image.open(tempfile.name)
        if self.crop:
            img = img.crop(self.crop)
        if self.resize:
            img = img.resize(self.resize)
        if self.rotate:
            img = img.rotate(self.rotate)
        return img

    def _download_image(self, bucket_name, file_path) -> Image:
        url = "https://%s.s3.amazonaws.com/%s" % (bucket_name, file_path)
        response = requests.get(url)
        if response.status_code == 404:
            raise ValidationError("File not found")
        elif response.status_code == 403:
            raise ValidationError("File must be public")

        p = ImageFile.Parser()
        for chunk in response.iter_content(4096):
            p.feed(chunk)
        return p.close()

    def _store_result(self, image: Image, image_hash: str):
        th = Thumbnail()
        th.hash = image_hash
        with tempfile.NamedTemporaryFile("rb", suffix=".jpg") as temp_file:
            image.save(temp_file.name)
            th.result.save(image_hash + ".jpg", File(temp_file.file))
        th.save()
        return th
