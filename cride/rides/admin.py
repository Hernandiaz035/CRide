"""Rides Admin."""

# Django
from django.contrib import admin

# Models
from cride.rides.models import Ride


@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    """Ride Admin."""

    list_display = (
        'offered_by',
        'offered_in',
        'departure_date',
        'arrival_date',
        'rating',
        'is_active',
    )

    search_fields = ('offered_by', 'offered_in')

    list_filter = ('is_active', )
