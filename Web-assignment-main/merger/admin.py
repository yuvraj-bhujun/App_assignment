from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import Activity, ActivityImage, ActivityHighlight, User, Booking, Payment, BookingReview, Notification

class ActivityImageInline(admin.TabularInline):
    model = ActivityImage
    extra = 1
    readonly_fields = ('uploaded_at',)
    fields = ('image', 'uploaded_at')

class ActivityHighlightInline(admin.TabularInline):
    model = ActivityHighlight
    extra = 0
    fields = ('icon_image', 'icon_title', 'icon_description')

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    # Fields shown in the list view
    list_display = (
        'name',
        'activity_type',
        'base_price',
        'max_participants',
        'num_images',
        'num_highlights',
    )

    # Fields editable directly from list view
    list_editable = ('base_price', 'max_participants')

    # Search and filters
    search_fields = ('name', 'activity_type', 'location')
    list_filter = ('activity_type', 'base_price', 'location')

    # Organize fields in the admin form
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'activity_type', 'description', 'base_price', 'location', 'duration', 'max_participants')
        }),
        ('Rules & Policies', {
            'fields': ('activity_rules', 'safety_equipment', 'cancellation_policy')
        }),
        ('Location', {
            'fields': ('map_embed_url', 'map_location_description')
        }),
    )

    inlines = [ActivityImageInline, ActivityHighlightInline]

    # computed fields
    def num_images(self, obj):
        return obj.images.count()
    num_images.short_description = 'Images'

    def num_highlights(self, obj):
        return obj.highlights.count()
    num_highlights.short_description = 'Highlights'

    # Custom admin actions
    actions = ['apply_discount', 'update_max_participants']

    def apply_discount(self, request, queryset):
        """
        Apply a 10% discount to the selected activities' base price
        """
        for activity in queryset:
            original_price = activity.base_price
            activity.base_price = int(activity.base_price * 0.9)
            activity.save()
        self.message_user(request, f"Applied 10% discount to {queryset.count()} activities.")
    apply_discount.short_description = "Apply 10 percent discount to selected activities"

    def update_max_participants(self, request, queryset):
        """
        Bulk update max participants for selected activities
        """
        for activity in queryset:
            activity.max_participants += 5
            activity.save()
        self.message_user(request, f"Increased max participants by 5 for {queryset.count()} activities.")
    update_max_participants.short_description = "Increase max participants by 5 for selected activities"


# ---------------- User Admin ----------------
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'phone', 'total_bookings', 'total_spent', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    list_filter = ('date_joined',)
    readonly_fields = ('total_bookings', 'total_spent', 'date_joined')

    fieldsets = (
        (None, {'fields': ('email', 'password', 'username')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Stats', {'fields': ('total_bookings', 'total_spent')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'first_name', 'last_name', 'phone', 'password1', 'password2'),
        }),
    )


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'activity', 'customer', 'date', 'group_size', 'price_total', 'status', 'created_at')
    list_editable = ('status', 'group_size')
    search_fields = ('customer__email', 'activity__name')
    list_filter = ('status', 'date', 'activity')
    readonly_fields = ('price_total', 'created_at')
    actions = ['mark_completed', 'mark_cancelled']

    def mark_completed(self, request, queryset):
        updated = 0
        for booking in queryset:
            if booking.status != Booking.Status.COMPLETED:
                booking.status = Booking.Status.COMPLETED
                booking.save()
                
                # Create notification for customer with review link
                review_url = f"/grandblue/user/review/{booking.id}/"
                Notification.objects.create(
                    user=booking.customer,
                    title='Booking Completed',
                    message=f'Your booking for {booking.activity.name} on {booking.date} has been marked as completed. Please consider leaving a review. <a href=\'{review_url}\' class=\'review-link\'>Leave a Review</a>|||'
                            f'Booking Details:\n\n'
                            f'Activity: {booking.activity.name}\n\n'
                            f'Date: {booking.date}\n\n'
                            f'People: {booking.group_size}\n\n'
                            f'Amount: Rs {booking.price_total}',
                    type=Notification.Type.BOOKING_COMPLETED
                )
                updated += 1
        
        self.message_user(request, f"{updated} bookings marked as completed.")
    mark_completed.short_description = "Mark selected bookings as completed"

    def mark_cancelled(self, request, queryset):
        updated = 0
        for booking in queryset:
            if booking.status != Booking.Status.CANCELLED:
                booking.status = Booking.Status.CANCELLED
                booking.save()
                
                # Create notification for customer
                Notification.objects.create(
                    user=booking.customer,
                    title='Booking Cancelled',
                    message=f'Your booking for {booking.activity.name} on {booking.date} has been cancelled due to harsh weather. '
                            f"Your safety is our priority. We apologize for the inconvenience.|||"
                            f'Booking Details:\n\n'
                            f'Activity: {booking.activity.name}\n\n'
                            f'Date: {booking.date}\n\n'
                            f'People: {booking.group_size}\n\n'
                            f'Amount Paid: Rs {booking.price_total}'
                            f"A refund will be processed within 5–7 business days.",
                    type=Notification.Type.BOOKING_CANCELLED
                )
                updated += 1
        
        self.message_user(request, f"{updated} bookings marked as cancelled.")
    mark_cancelled.short_description = "Mark selected bookings as cancelled"
    
    def save_model(self, request, obj, form, change):
        """Handle inline status changes and create notifications"""
        if change and 'status' in form.changed_data:
            old_status = Booking.objects.get(pk=obj.pk).status
            
            # Only send notification if status actually changed
            if old_status != obj.status:
                if obj.status == Booking.Status.COMPLETED:
                    review_url = f"/grandblue/user/review/{obj.id}/"
                    Notification.objects.create(
                        user=obj.customer,
                        title='Booking Completed',
                        message=f'Your booking for {obj.activity.name} on {obj.date} has been marked as completed. Please consider leaving a review. <a href=\'{review_url}\' class=\'review-link\'>Leave a Review</a>|||'
                                f'Booking Details:\n\n'
                                f'Activity: {obj.activity.name}\n\n'
                                f'Date: {obj.date}\n\n'
                                f'People: {obj.group_size}\n\n'
                                f'Amount: Rs {obj.price_total}',
                        type=Notification.Type.BOOKING_COMPLETED
                    )
                elif obj.status == Booking.Status.CANCELLED:
                    Notification.objects.create(
                        user=obj.customer,
                        title='Booking Cancelled',
                        message=f'Your booking for {obj.activity.name} on {obj.date} has been cancelled due to harsh weather. '
                                f"Your safety is our priority. We apologize for the inconvenience.|||"
                                f'Booking Details:\n\n'
                                f'Activity: {obj.activity.name}\n\n'
                                f'Date: {obj.date}\n\n'
                                f'People: {obj.group_size}\n\n'
                                f'Amount Paid: Rs {obj.price_total}'
                                f"A refund will be processed within 5–7 business days.",
                        type=Notification.Type.BOOKING_CANCELLED
                    )
        
        super().save_model(request, obj, form, change)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'booking', 'amount', 'status', 'method', 'provider', 'paid_at')
    list_editable = ('status',)
    search_fields = ('booking__customer__email', 'booking__activity__name', 'provider')
    list_filter = ('status', 'method', 'paid_at')
    readonly_fields = ('amount', 'booking', 'paid_at')
    


@admin.register(BookingReview)
class BookingReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'booking', 'customer', 'rating', 'is_deleted', 'created_at')
    list_editable = ('is_deleted',)
    search_fields = ('customer__email', 'booking__activity__name', 'comment')
    list_filter = ('rating', 'is_deleted', 'created_at')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "booking":
            kwargs["queryset"] = Booking.objects.filter(
                status=Booking.Status.COMPLETED
            ).exclude(
                review__isnull=False
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(ActivityImage)
class ActivityImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'activity', 'image_tag', 'uploaded_at')
    search_fields = ('activity__name',)
    readonly_fields = ('uploaded_at', 'image_tag')

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 60px; height:auto;" />', obj.image.url)
        return "-"
    image_tag.short_description = 'Image'


@admin.register(ActivityHighlight)
class ActivityHighlightAdmin(admin.ModelAdmin):
    list_display = ('id', 'activity', 'icon_title', 'icon_description', 'icon_tag')
    search_fields = ('activity__name', 'icon_title')

    def get_readonly_fields(self, request, obj=None):
        # this only shows the image preview when editing an existing instance
        if obj:
            return ('icon_tag',)
        return ()  # no readonly preview on the Add page
    
    #This is a thumbnail preview of how the icon would look like in the activity page
    def icon_tag(self, obj):
        if obj and obj.icon_image:
            return format_html('<img src="{}" style="width: 24px; height:24px;" />', obj.icon_image.url)
        return "-"
    icon_tag.short_description = 'Icon Preview'

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'type',
        'title',
        'short_message',
        'created_at',
    )
    list_filter = ('type', 'created_at')
    search_fields = ('user__email', 'title', 'message')
    readonly_fields = ('created_at',)

    def short_message(self, obj):
        if len(obj.message) > 50:
            return obj.message[:50] + "..."
        return obj.message
    short_message.short_description = "Message Preview"