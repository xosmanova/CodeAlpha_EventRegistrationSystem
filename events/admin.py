from django.contrib import admin
from .models import Event, Registration


class RegistrationInline(admin.TabularInline):
    model = Registration
    extra = 0
    readonly_fields = ['ticket_code', 'created_at']
    fields = ['ticket_code', 'full_name', 'email', 'phone', 'status', 'created_at']
    can_delete = True


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'category',
        'date',
        'capacity',
        'get_registered_count',
        'get_available_seats',
        'is_active',
        'organizer',
        'created_at'
    ]
    list_filter = ['category', 'is_active', 'date']
    search_fields = ['title', 'description', 'location', 'organizer__username']
    date_hierarchy = 'date'
    inlines = [RegistrationInline]

    @admin.display(description='Registered')
    def get_registered_count(self, obj):
        return obj.registered_count

    @admin.display(description='Available Seats')
    def get_available_seats(self, obj):
        seats = obj.available_seats
        return seats if seats > 0 else "FULL"


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = [
        'ticket_code',
        'full_name',
        'email',
        'phone',
        'event',
        'status',
        'created_at'
    ]
    list_filter = ['status', 'event', 'created_at']
    search_fields = ['ticket_code', 'full_name', 'email', 'phone', 'event__title']
    readonly_fields = ['ticket_code', 'created_at', 'updated_at']
    actions = ['mark_confirmed', 'mark_cancelled']

    @admin.action(description="Mark selected registrations as Confirmed")
    def mark_confirmed(self, request, queryset):
        queryset.update(status=Registration.STATUS_CONFIRMED)
        self.message_user(request, "Selected registrations marked as Confirmed.")

    @admin.action(description="Mark selected registrations as Cancelled")
    def mark_cancelled(self, request, queryset):
        queryset.update(status=Registration.STATUS_CANCELLED)
        self.message_user(request, "Selected registrations marked as Cancelled.")
