"""Circles Admin."""

# Django
from django.contrib import admin

# Models
from cride.circles.models import Circle


@admin.register(Circle)
class CircleAdmin(admin.ModelAdmin):
    """Circle Admin."""

    list_display = (
        'slug_name',
        'name',
        'public',
        'verified',
        'is_limited',
        'members_limit'
    )

    search_fields = ('slug_name', 'name')

    list_filter = ('public', 'verified', 'is_limited')
