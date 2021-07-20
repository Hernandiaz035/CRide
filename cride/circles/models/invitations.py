"""Invitation Model."""

# Django
from django.db import models

# Managers
from cride.circles.managers import InvitationManager

# Utilities
from cride.utils.models import CRideModel
from uuid import uuid4


class Invitation(CRideModel):
    """Invitation Model.

    Invitation is a tables that holds the code or permission granted
    from one circle member to another user to join to the circle."""

    code =  models.CharField(unique=True, editable=False, max_length=50)

    issued_by = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        help_text="Circle Member that is providing the invitation",
        related_name='issued_by'
    )
    used_by = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        null=True,
        help_text="User that used the code to join to the circle"
    )

    circle = models.ForeignKey('circles.Circle', on_delete=models.CASCADE)

    used = models.BooleanField(
        default=False,
        help_text="Only unused invitations can join users."
    )
    used_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Date time on which the invitation was used'
    )

    # Manager
    objects = InvitationManager()

    def __str__(self):
        """Returns circle's slug_name and code."""
        return "#{}: {}".format(self.circle.slug_name, self.code)
