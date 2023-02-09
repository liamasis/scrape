from django.db import models
from django.core.exceptions import ValidationError

# Create your models here.
from django.db import models

# Create your models here.


class Session(models.Model):

    STATUS_CHOICES = [
        (1, 'Preprocessing'),
        (2, 'Waiting for follow'),
        (3, 'Processing'),
        (4, 'Presenting'),
        (5, 'Complete'),
        (6, 'Error'),
        (7, 'User interrupted')
    ]

    first_name = models.CharField(max_length=120)
    status = models.IntegerField(
        choices=STATUS_CHOICES,
        default=1,
    )

    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.first_name


class InstagramAccount(models.Model):

    STATUS_CHOICES = [
        (1, 'Processing'),
        (2, 'Complete'),
    ]

    handle = models.CharField(max_length=120)
    status = models.IntegerField(
        choices=STATUS_CHOICES,
        default=1,
    )
    date_created = models.DateTimeField(auto_now_add=True)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)

    def __str__(self):
        return self.handle


class Media(models.Model):

    class Meta:
        ordering = ['-date_media']

    MEDIA_TYPE_CHOICES = [
        (1, 'Photo'),
        (2, 'Video'),
        (8, 'Album')
    ]

    date_media = models.DateTimeField()
    media_id = models.CharField(max_length=255)
    media_pk = models.CharField(max_length=255)
    media_type = models.IntegerField(
        choices=MEDIA_TYPE_CHOICES,
        default=1,
    )
    caption_text = models.TextField()
    audio_filename = models.CharField(max_length=255)
    # short_caption_text = models.TextField()
    comment_count = models.IntegerField(default=0)
    like_count = models.IntegerField(default=0)
    title = models.CharField(max_length=255)

    account = models.ForeignKey(InstagramAccount, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.media_id

    @classmethod
    def create_from_igrapi(cls, instagram_account_id, igrapi_media: dict):
        media = cls(
            media_id=igrapi_media.id,
            media_pk=igrapi_media.pk,
            media_type=igrapi_media.media_type,
            caption_text=igrapi_media.caption_text,
            comment_count=igrapi_media.comment_count,
            like_count=igrapi_media.like_count,
            title=igrapi_media.title,
            account_id=instagram_account_id,
            date_media=igrapi_media.taken_at
        )
        return media


class InstagramLoginAccount(models.Model):
    first_name = models.CharField(max_length=120, blank=True, null=True)
    last_name = models.CharField(max_length=120, blank=True, null=True)
    username = models.CharField(max_length=120)
    password = models.CharField(max_length=120)

    dont_use_until = models.DateTimeField(blank=True, null=True)
    last_used = models.DateTimeField(blank=True, null=True)
    error_count = models.IntegerField(default=0)

    def __str__(self):
        if self.first_name and self.last_name:
            return f'{self.username} ({self.first_name} {self.last_name})'
        elif self.first_name:
            return f'{self.username} ({self.first_name})'
        else:
            return self.username



class State(models.Model):

    STATE_CHOICES = [
        (1, 'Ready'),
        (2, 'Occupied'),
        (5, 'Processing'),
    ]

    state = models.IntegerField(
        choices=STATE_CHOICES,
        default=1,
    )

    active_session = models.ForeignKey(Session, on_delete=models.SET_NULL, null=True, blank=True)

    date_ready = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.pk and State.objects.exists():
            raise ValidationError('There can be only one State instance')
        self.pk = self.id = 1
        return super(State, self).save(*args, **kwargs)

    def __str__(self):
        return "Scrape_Elegy App State"


class ScrapeException(Exception):
    pass