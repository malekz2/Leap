from django.contrib import admin
from .models import Profile, Relationship
from .forms import ProfileAdminForm

class ProfileAdmin(admin.ModelAdmin):
    form = ProfileAdminForm
    fieldsets = (
        (None, {'fields': ('user', 'is_online', 'following', 'friends', 'bio', 'date_of_birth', 'image', 'google_form_url')}),
        ('Personal info', {'fields': ('teach', 'learn')}),
    )

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Relationship)