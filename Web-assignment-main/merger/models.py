from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db.models import Sum, F, Q, ExpressionWrapper, IntegerField
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.timesince import timesince
from django.conf import settings


class User(AbstractUser):
    email = models.EmailField(blank=True, unique=True)
    date_joined = models.DateTimeField(default=timezone.now)
    phone = models.CharField(max_length=20, blank=True)
    total_bookings = models.PositiveIntegerField(default=0)
    total_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        ordering = ['email']

    def __str__(self):
        full_name = self.get_full_name() or self.username
        phone = self.phone or "N/A"
        return (
            f"\nUser Profile: {full_name}\n"
            f"Email: {self.email}\n"
            f"Phone: {phone}\n"
            f"Member since: {self.date_joined.strftime('%b %d, %Y')}\n"
            f"Total bookings: {self.total_bookings}\n"
            f"Total spent: Rs {self.total_spent:.2f}\n"
        )


class Activity(models.Model):
    ACTIVITY_TYPES = [
        ("Catamaran", "Catamaran"),
        ("Scuba diving", "Scuba diving"),
        ("Dolphin watching", "Dolphin watching"),
        ("Water ski", "Water ski"),
        ("Speed boat", "Speed boat"),
    ]

    name = models.CharField(max_length=255)
    activity_type = models.CharField(max_length=120, blank=True, choices=ACTIVITY_TYPES)
    description = models.TextField()
    base_price = models.PositiveIntegerField(help_text="Price per pax (Rs)")
    location = models.CharField(max_length=120, blank=True)
    duration = models.CharField(max_length=60, blank=True)
    max_participants = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    activity_rules = models.TextField(blank=True, help_text="One rule per line")
    safety_equipment = models.TextField(blank=True, help_text="One item per line")
    cancellation_policy = models.TextField(blank=True, help_text="One policy per line")
    map_embed_url = models.TextField(blank=True)
    map_location_description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["activity_type"]),
            models.Index(fields=["location"]),
        ]
        verbose_name = "Activity" 
        verbose_name_plural = "Activities" 

    def save(self, *args, **kwargs):
        if self.activity_rules:
            self.activity_rules = self.activity_rules.replace(r'\n', '\n')
        if self.safety_equipment:
            self.safety_equipment = self.safety_equipment.replace(r'\n', '\n')
        if self.cancellation_policy:
            self.cancellation_policy = self.cancellation_policy.replace(r'\n', '\n')
        super().save(*args, **kwargs)

    def __str__(self):
        location = self.location or "N/A"
        duration = self.duration or "N/A"
        rules_count = len(self.activity_rules.splitlines()) if self.activity_rules else 0
        equipment_count = len(self.safety_equipment.splitlines()) if self.safety_equipment else 0
        cancellation_count = len(self.cancellation_policy.splitlines()) if self.cancellation_policy else 0

        return (
            f"\nActivity: {self.name}\n"
            f"Type: {self.activity_type}\n"
            f"Location: {location}\n"
            f"Base Price: Rs {self.base_price} per customer\n"
            f"Duration: {duration}\n"
            f"Max Participants: {self.max_participants}\n"
            f"Rules: {rules_count} item(s)\n"
            f"Safety Equipment: {equipment_count} item(s)\n"
            f"Cancellation Policies: {cancellation_count} item(s)\n"
            f"Created on: {self.created_at.strftime('%b %d, %Y')}\n"
        )



class ActivityImage(models.Model):
    activity = models.ForeignKey(Activity, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="activities/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        filename = self.image.name.split("/")[-1]  
        time_ago = timesince(self.uploaded_at).split(",")[0] 
        activity_type = self.activity.activity_type or "General"

        return f"\nImage '{filename}' for {self.activity.name} ({activity_type}) – uploaded {time_ago} ago\n"


class Booking(models.Model):
    class Status(models.TextChoices):
        CONFIRMED = "CONFIRMED", "Confirmed"
        CANCELLED = "CANCELLED", "Cancelled"
        COMPLETED = "COMPLETED", "Completed"

    customer = models.ForeignKey(User, related_name="bookings", on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, related_name="bookings", on_delete=models.CASCADE)

    date = models.DateField(help_text="Selected date for the activity")
    group_size = models.PositiveIntegerField(default=1)
    price_total = models.PositiveIntegerField(help_text="Total price (Rs)")
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.CONFIRMED)

    created_at = models.DateTimeField(auto_now_add=True)
    cancelled_at = models.DateTimeField(blank=True, null=True)
    cancellation_reason = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["date"]),
            models.Index(fields=["customer", "created_at"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=Q(date__gt=F("created_at")),
                name="booking_date_after_creation"
            ),
        ]

    def save(self, *args, **kwargs):
        self.price_total = self.activity.base_price * self.group_size
        super().save(*args, **kwargs)

    def __str__(self):
        customer_name = self.customer.get_full_name() or self.customer.username
        activity_info = f"{self.activity.name} ({self.activity.activity_type}, {self.activity.location})"
        time_ago = timesince(self.created_at).split(",")[0] 
        status_display = self.get_status_display()
        
        cancellation_note = ""
        if self.status == self.Status.CANCELLED:
            cancellation_note = f" – Cancelled: {self.cancellation_reason[:30]}{'...' if len(self.cancellation_reason) > 30 else ''}"

        return (f"Booking #{self.pk}: {customer_name} ×{self.group_size} for {activity_info} "
                f"on {self.date} [{status_display}, Rs {self.price_total}] "
                f"(Created {time_ago} ago){cancellation_note}")



class Payment(models.Model):
    class Status(models.TextChoices):
        PAID = "PAID", "Paid"
        REFUNDED = "REFUNDED", "Refunded"

    class Method(models.TextChoices):
        CARD = "CARD", "Credit/Debit Card"

    booking = models.OneToOneField(Booking, related_name="payments", on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(help_text="Amount in Rs")
    method = models.CharField(max_length=16, choices=Method.choices, default=Method.CARD)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PAID)

    provider = models.CharField(max_length=64, blank=True, help_text="e.g., Stripe, PayPal")
    paid_at = models.DateTimeField(blank=True, null=True)
    
    

    class Meta:
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["method"]),
            models.Index(fields=["booking", "paid_at"]),
        ]

    def __str__(self):
        customer_name = self.booking.customer.get_full_name() or self.booking.customer.username
        activity_name = self.booking.activity.name
        method_display = self.get_method_display()
        status_display = self.get_status_display()
        
        paid_note = ""
        if self.paid_at:
            time_ago = timesince(self.paid_at).split(",")[0]
            paid_note = f", paid {time_ago} ago"
        
        provider_note = f" via {self.provider}" if self.provider else ""
        
        return (f"\nPayment #{self.pk}: Rs {self.amount} for {activity_name} "
                f"(Booking #{self.booking.pk} by {customer_name}) "
                f"[{status_display}, {method_display}{provider_note}{paid_note}]\n")



class BookingReview(models.Model):
    booking = models.OneToOneField(Booking, related_name="review", on_delete=models.CASCADE)
    customer = models.ForeignKey(User, related_name="reviews", on_delete=models.CASCADE)

    rating = models.PositiveSmallIntegerField(help_text="1-5")
    comment = models.TextField(blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                check=models.Q(rating__gte=1, rating__lte=5),
                name="bookingreview_rating_between_1_and_5",
            ),
        ]
        indexes = [models.Index(fields=["customer", "created_at"])]

    def __str__(self):
        customer_name = self.customer.get_full_name() or self.customer.username
        activity_name = self.booking.activity.name
        rating_stars = "★" * self.rating + "☆" * (5 - self.rating)  # visual stars for 1-5 rating
        
        comment_snippet = (self.comment[:50] + "...") if len(self.comment) > 50 else self.comment
        deleted_note = " [DELETED]" if self.is_deleted else ""
        
        time_ago = timesince(self.created_at).split(",")[0]  # e.g., "3 hours"
        
        return (f"Review #{self.pk} for '{activity_name}' by {customer_name} "
                f"({rating_stars}, {time_ago} ago){deleted_note}: \"{comment_snippet}\"")


class ActivityHighlight(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name="highlights")
    icon_image = models.ImageField(upload_to="activities/")
    icon_title = models.CharField(max_length=255)
    icon_description = models.TextField()

    def __str__(self):
        # short snippet of description (max 40 chars)
        desc = (self.icon_description[:40] + "...") if len(self.icon_description) > 40 else self.icon_description
        
        # filename from the image field
        image_name = self.icon_image.name.split("/")[-1] if self.icon_image else "No image"
        return f"Highlight '{self.icon_title}' for '{self.activity.name}' [{image_name}]: \"{desc}\""


class Notification(models.Model):
    class Type(models.TextChoices):
        BOOKING_CONFIRMED = "CONFIRMED", "Booking Confirmed"
        BOOKING_CANCELLED = "CANCELLED", "Booking Cancelled"
        BOOKING_COMPLETED = "COMPLETED", "Booking Completed"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="notifications",
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    type = models.CharField(max_length=20, choices=Type.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        type_display = self.get_type_display()
        time_ago = timesince(self.created_at).split(",")[0]  # e.g., "2 hours"
        title_snippet = (self.title[:40] + "...") if len(self.title) > 40 else self.title
        message_snippet = (self.message[:60] + "...") if len(self.message) > 60 else self.message

        user_name = self.user.get_full_name() or self.user.email or "Unknown User"

        return (
            f"Notification #{self.pk} for {user_name} "
            f"[{type_display}, {time_ago} ago]: "
            f"'{title_snippet}' – \"{message_snippet}\""
        )
    

@receiver([post_save, post_delete], sender=Booking)
def update_user_totals(sender, instance, **kwargs):
    user = instance.customer
    valid_status = [Booking.Status.CONFIRMED, Booking.Status.COMPLETED]

    confirmed_bookings = user.bookings.filter(status__in=valid_status)

    user.total_bookings = confirmed_bookings.count()

    total_expr = ExpressionWrapper(
        F('activity__base_price') * F('group_size'),
        output_field=IntegerField()
    )
    user.total_spent = confirmed_bookings.aggregate(total=Sum(total_expr))['total'] or 0

    user.save(update_fields=["total_bookings", "total_spent"])
    print(f"Updated totals for {user.email}: bookings={user.total_bookings}, spent={user.total_spent}")