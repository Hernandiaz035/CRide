"""Profile Model."""

# Django
from django.db import models
from django.db.models.deletion import CASCADE

# Utilities
from cride.utils.models import CRideModel


class Profile(CRideModel):
    """Profile Model.

     A profile holds user's public data like biography, picture
     and statistics.
    """

    user = models.OneToOneField('users.User', on_delete=models.CASCADE)

    picture = models.ImageField(
        'profile_picture',
        upload_to='users/pictures/',
        blank=True,
        null=True
    )

    biography = models.TextField(max_length=500, blank=True)

    # Stats
    rides_taken = models.PositiveIntegerField(default=0)
    rides_offered = models.PositiveIntegerField(default=0)
    reputation = models.FloatField(
        default=5.0,
        help_text="User's reputation based on the rides offered and taken"
    )
