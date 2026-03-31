from django.views import View
from django.views.generic import ListView, TemplateView, DeleteView, FormView, DetailView
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, Sum, Avg, Q, Value
from django.db.models.functions import Concat
from django.utils import timezone
from django.contrib.auth.views import LoginView as AdminLoginView, redirect_to_login
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.timezone import localdate
from datetime import date

from .models import User, Booking, Activity, Payment, BookingReview, ActivityImage, ActivityHighlight


# Mixin to require staff access 
class StaffRequiredMixin(UserPassesTestMixin):
    """Mixin to require is_staff and redirect to Django admin login if not."""

    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        return redirect_to_login(
            self.request.get_full_path(),
            login_url='/admin/login/',
            redirect_field_name=REDIRECT_FIELD_NAME
        )

# TemplateView
class DashboardView(LoginRequiredMixin, StaffRequiredMixin, TemplateView):
    template_name = 'admin_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        stats = Booking.objects.aggregate(
            cancelled=Count('id', filter=Q(status='CANCELLED')),
            confirmed=Count('id', filter=Q(status='CONFIRMED')),
            completed=Count('id', filter=Q(status='COMPLETED')),
        )

        avg_rating = BookingReview.objects.exclude(is_deleted=True).aggregate(average=Avg('rating'))['average'] or 0
        
        context.update({
            'active_class': "dashboard",
            'cancelled_booking': stats['cancelled'],
            'confirmed_booking': stats['confirmed'],
            'total_booking': stats['cancelled'] + stats['confirmed'] + stats['completed'],
            'total_activities': Activity.objects.count(),
            'registered_customers': User.objects.filter(is_staff=False, is_superuser=False).count(),
            'total_revenue': (
            Payment.objects
            .filter(status="PAID")
            .aggregate(total=Sum("amount"))['total'] or 0
            ),
            'average_rating': round(avg_rating, 1) if avg_rating else 0,
            'total_reviews': BookingReview.objects.exclude(is_deleted=True).aggregate(total=Count('id'))['total'] or 0,
            'total_paid': Payment.objects.filter(status='PAID').count(),
            'total_refunded': Payment.objects.filter(status='REFUNDED').count(),
            'bookings': Booking.objects.select_related('customer').filter(
                created_at__month=timezone.now().month
            ).order_by('-created_at')[:15],
            'reviews': BookingReview.objects.exclude(is_deleted=True).select_related('customer').order_by('-created_at')[:15],
        })

        return context

# ListView
class CustomersPageView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = User
    template_name = 'admin_customers_page.html'
    context_object_name = 'customers'
    paginate_by = 10

    def get_queryset(self):
        queryset = User.objects.filter(is_staff=False, is_superuser=False).order_by('-date_joined')
        
        # Search filter
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.annotate(
                full_name=Concat('first_name', Value(' '), 'last_name')
            ).filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(full_name__icontains=search) |
                Q(email__icontains=search) |
                Q(phone__icontains=search)
            )
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_class'] = 'customers'
        context['current_search'] = self.request.GET.get('search', '')
        return context


# Uses default Django admin login
class CustomAdminLoginView(AdminLoginView):
    template_name = 'admin/login.html'


class ReviewsPageView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = BookingReview
    template_name = 'admin_reviews.html'
    context_object_name = 'reviews'
    paginate_by = 10

    def get_queryset(self):
        queryset = BookingReview.objects.exclude(is_deleted=True).select_related('customer', 'booking__activity').order_by('-created_at')
        
        # Filter by rating
        rating = self.request.GET.get('rating')
        if rating and rating != 'all':
            queryset = queryset.filter(rating=rating)
        
        # Search filter
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.annotate(
                customer_full_name=Concat('customer__first_name', Value(' '), 'customer__last_name')
            ).filter(
                Q(customer__first_name__icontains=search) |
                Q(customer__last_name__icontains=search) |
                Q(customer_full_name__icontains=search) |
                Q(booking__activity__name__icontains=search) |
                Q(comment__icontains=search)
            )
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        all_reviews = BookingReview.objects.exclude(is_deleted=True)
        avg_rating = all_reviews.aggregate(average=Avg('rating'))['average'] or 0
        
        context.update({
            'active_class': 'reviews',
            'total_reviews': all_reviews.count(),
            'average_rating': round(avg_rating, 1) if avg_rating else 0,
            'current_rating': self.request.GET.get('rating', 'all'),
            'current_search': self.request.GET.get('search', ''),
        })
        return context


class ActivitiesPageView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = Activity
    template_name = 'admin_activity.html'
    context_object_name = 'activities'
    paginate_by = 10

    def get_queryset(self):
        #return Activity.objects.prefetch_related('images','highlights')
        queryset = Activity.objects.prefetch_related('images').order_by('-created_at')
        
        # Filter by activity type
        activity_type = self.request.GET.get('activity_type')
        if activity_type and activity_type != 'all':
            queryset = queryset.filter(activity_type=activity_type)
        
        # Search filter
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(location__icontains=search) |
                Q(description__icontains=search)
            )
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_class'] = 'activities'
        context['current_activity_type'] = self.request.GET.get('activity_type', 'all')
        context['current_search'] = self.request.GET.get('search', '')
        return context


class BookingsPageView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = Booking
    template_name = 'admin_booking.html'
    context_object_name = 'bookings'
    paginate_by = 10

    def get_queryset(self):
        queryset = Booking.objects.select_related('customer', 'activity').order_by('-created_at')
        
        # Filter by status
        status = self.request.GET.get('status')
        if status and status != 'all':
            queryset = queryset.filter(status=status.upper())
        
        # Filter by activity
        activity = self.request.GET.get('activity')
        if activity and activity != 'all':
            queryset = queryset.filter(activity__activity_type=activity)
        
        # Search filter
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.annotate(
                customer_full_name=Concat('customer__first_name', Value(' '), 'customer__last_name')
            ).filter(
                Q(customer__first_name__icontains=search) |
                Q(customer__last_name__icontains=search) |
                Q(customer_full_name__icontains=search) |
                Q(customer__email__icontains=search) |
                Q(activity__name__icontains=search)
            )
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_class'] = 'bookings'
        context['current_status'] = self.request.GET.get('status', 'all')
        context['current_activity'] = self.request.GET.get('activity', 'all')
        context['current_search'] = self.request.GET.get('search', '')
        return context


class PaymentsPageView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = Payment
    template_name = 'admin_payment.html'
    context_object_name = 'payments'
    paginate_by = 10

    def get_queryset(self):
        queryset = Payment.objects.select_related('booking__customer', 'booking__activity').order_by('-paid_at')
        
        # Filter by status
        status = self.request.GET.get('status')
        if status and status != 'all':
            queryset = queryset.filter(status=status.upper())
        
        # Search filter
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.annotate(
                customer_full_name=Concat('booking__customer__first_name', Value(' '), 'booking__customer__last_name')
            ).filter(
                Q(booking__customer__first_name__icontains=search) |
                Q(booking__customer__last_name__icontains=search) |
                Q(customer_full_name__icontains=search) |
                Q(booking__customer__email__icontains=search) |
                Q(id__icontains=search)
            )
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'active_class': 'payments',
            'total_revenue': (
                Payment.objects
                .filter(status="PAID")
                .aggregate(total=Sum("amount"))["total"] or 0
            ),
            'total_transactions': Payment.objects.aggregate(total=Count('amount'))['total'] or 0,
            'current_status': self.request.GET.get('status', 'all'),
            'current_search': self.request.GET.get('search', ''),
        })
        return context

# DeleteView
class ActivityDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Activity
    success_url = reverse_lazy("activities")

    def post(self, request, *args, **kwargs):
        activity = self.get_object()
        name = activity.name
        activity.delete()
        messages.success(request, f"Activity '{name}' deleted successfully!")
        return redirect("activities")

# CreateView + UpdateView    
class ActivityFormView(StaffRequiredMixin, LoginRequiredMixin, FormView):
    template_name = "admin_activity.html"
    success_url = reverse_lazy("activities")
    form_class = None  # using manual form handling

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        activity_id = request.POST.get("activity_id")
        try:
            activity_id = int(activity_id) if activity_id else 0
        except (TypeError, ValueError):
            activity_id = 0

        name = request.POST.get("name")
        activity_type = request.POST.get("activity_type", "")
        location = request.POST.get("location", "")
        description = request.POST.get("description")
        price = request.POST.get("price")
        duration = request.POST.get("duration", "")
        max_participants = request.POST.get("max_participants", 1)

        activity_rules = request.POST.get("activity_rules", "")
        safety_equipment = request.POST.get("safety_equipment", "")
        cancellation_policy = request.POST.get("cancellation_policy", "")
        map_embed_url = request.POST.get("map_embed_url", "")
        map_location_description = request.POST.get("map_location_description", "")

        if not name or not description or not price:
            messages.error(request, "Please fill in all required fields.")
            return redirect("activities")

        try:
            price_int = int(price)
        except (TypeError, ValueError):
            messages.error(request, "Price must be a valid number.")
            return redirect("activities")

        try:
            max_int = int(max_participants)
        except (TypeError, ValueError):
            max_int = 1

        # EDIT
        if activity_id > 0:
            activity = get_object_or_404(Activity, id=activity_id)

            activity.name = name
            activity.activity_type = activity_type
            activity.description = description
            activity.base_price = price_int
            activity.location = location
            activity.duration = duration
            activity.max_participants = max_int

            activity.activity_rules = activity_rules
            activity.safety_equipment = safety_equipment
            activity.cancellation_policy = cancellation_policy
            activity.map_embed_url = map_embed_url
            activity.map_location_description = map_location_description

            activity.save()

            # Delete highlights
            delete_ids = request.POST.getlist("delete_highlight_ids")
            if delete_ids:
                highlights_to_delete = ActivityHighlight.objects.filter(activity=activity, id__in=delete_ids)
                for hl in highlights_to_delete:
                    if hl.icon_image:
                        hl.icon_image.delete(save=False)
                highlights_to_delete.delete()

            # Delete images
            delete_ids = request.POST.getlist("delete_image_ids")
            if delete_ids:
                ActivityImage.objects.filter(activity=activity, id__in=delete_ids).delete()

            # Add new images
            new_images = request.FILES.getlist("images")
            remaining_count = activity.images.count()
            room_left = max(0, 10 - remaining_count)
            for img in new_images[:room_left]:
                ActivityImage.objects.create(activity=activity, image=img)

            self._save_highlights(request, activity)

            messages.success(request, f"Activity '{activity.name}' updated successfully!")
            return redirect("activities")

        # CREATE
        activity = Activity.objects.create(
            name=name,
            activity_type=activity_type,
            description=description,
            base_price=price_int,
            location=location,
            duration=duration,
            max_participants=max_int,
            activity_rules=activity_rules,
            safety_equipment=safety_equipment,
            cancellation_policy=cancellation_policy,
            map_embed_url=map_embed_url,
            map_location_description=map_location_description,
        )

        # Images for new activity
        images = request.FILES.getlist("images")
        for img in images[:10]:
            ActivityImage.objects.create(activity=activity, image=img)

        self._save_highlights(request, activity)

        messages.success(request, f"Activity '{activity.name}' added successfully!")
        return redirect("activities")

    def _save_highlights(self, request, activity):
        titles = request.POST.getlist("highlight_title")
        descrs = request.POST.getlist("highlight_description")
        ids = request.POST.getlist("highlight_id")

        image_map = {key.replace("highlight_image_", ""): file
                     for key, file in request.FILES.items()
                     if key.startswith("highlight_image_")}

        for i, title in enumerate(titles):
            desc = descrs[i] if i < len(descrs) else ""
            hid = ids[i] if i < len(ids) else ""

            if hid.isdigit() and int(hid) > 0:
                hl = ActivityHighlight.objects.filter(id=hid, activity=activity).first()
                if not hl:
                    hl = ActivityHighlight(activity=activity)
            else:
                hl = ActivityHighlight(activity=activity)

            hl.icon_title = title
            hl.icon_description = desc

            img = image_map.get(hid)
            if img:
                hl.icon_image = img

            hl.save()

class ActivityDetailView(DetailView):
    model = Activity
    template_name = "activity_booking.html"
    context_object_name = "activity"

    def get_object(self, queryset=None):
        activity_name = self.kwargs["activity_name"]
        return get_object_or_404(Activity, name__iexact=activity_name.replace("-", " "))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        activity = self.object
        
        context["highlights"] = activity.highlights.all()
        context["images"] = activity.images.all()
        context["average_rating"] = BookingReview.objects.filter(booking__activity=activity).exclude(is_deleted=True).aggregate(average=Avg('rating'))['average'] or 0
        context["total_reviews"] = BookingReview.objects.filter(booking__activity=activity).exclude(is_deleted=True).aggregate(total=Count('id'))['total'] or 0
        context["reviews"] = BookingReview.objects.filter(booking__activity=activity, is_deleted=False)

        #Calculates disabled dates and availability
        bookings = Booking.objects.filter(activity=activity, date__gte=localdate()).exclude(status=Booking.Status.CANCELLED)
        availability = {}
        disabled_dates = []

        today = date.today().isoformat()   
        disabled_dates.append(today)

        for booking in bookings:
            date_str = booking.date.strftime("%Y-%m-%d")
            availability[date_str] = availability.get(date_str, activity.max_participants) - booking.group_size
            if availability[date_str] <= 0:
                disabled_dates.append(date_str)
        
        availability = {date: spots for date, spots in availability.items() if spots > 0}

        context["availability"] = availability
        context["disabled_dates"] = disabled_dates
        print("DISABLED DATES:", disabled_dates)
        print("AVAILABILITY:", availability)
        return context