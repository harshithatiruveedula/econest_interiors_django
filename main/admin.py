from django.contrib import admin
from .models import Consultation, Service, GalleryImage, BlogPost

@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'service', 'appointment_date', 'submitted_at')
    list_filter = ('service', 'appointment_date', 'submitted_at')
    search_fields = ('name', 'email', 'phone', 'service')
    readonly_fields = ('submitted_at',)
    date_hierarchy = 'submitted_at'
    ordering = ('-submitted_at',)
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Consultation Details', {
            'fields': ('service', 'appointment_date', 'submitted_at')
        }),
    )

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'description_preview')
    search_fields = ('title', 'description')
    
    def description_preview(self, obj):
        return obj.description[:100] + '...' if len(obj.description) > 100 else obj.description
    description_preview.short_description = 'Description'

@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'image', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('title',)
    readonly_fields = ('uploaded_at',)
    date_hierarchy = 'uploaded_at'
    ordering = ('-uploaded_at',)

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at')
    list_filter = ('created_at', 'author')
    search_fields = ('title', 'content', 'author')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Post Information', {
            'fields': ('title', 'author', 'image')
        }),
        ('Content', {
            'fields': ('content',)
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )
