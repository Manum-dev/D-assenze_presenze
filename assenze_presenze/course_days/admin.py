from django.contrib import admin
from .models import CourseDay


@admin.register(CourseDay)
class CourseDayAdmin(admin.ModelAdmin):
    """Admin panel per gestione giornate corso"""
    list_display = ['date', 'description', 'is_holiday', 'created_at']
    list_filter = ['is_holiday', 'date']
    search_fields = ['description']
    ordering = ['date']
    date_hierarchy = 'date'