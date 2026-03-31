from django.shortcuts import render, redirect, get_object_or_404
from .forms import SignUpForm, LoginForm, PaymentForm, ActivityForm, ContactForm
from .models import User, Activity, ActivityImage, ActivityHighlight, Booking, Payment, BookingReview, Notification
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.utils import timezone
from django.db.models import Sum, Count, Avg, Q, Value
from django.db.models.functions import Concat
from django.db.models.functions import TruncMonth
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from datetime import datetime
import random

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.hashers import make_password, check_password
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.http import JsonResponse

from django.contrib.auth.password_validation import validate_password



def homepage(request):
    """
    Display homepage - different for logged-in users vs guests
    """
    catamaran_total_reviews = BookingReview.objects.filter(
        booking__activity__activity_type="Catamaran", is_deleted=False
    ).count()
    catamaran_average_rating = BookingReview.objects.filter(
        booking__activity__activity_type="Catamaran", is_deleted=False
    ).aggregate(avg=Avg('rating'))['avg'] or 0

    scuba_diving_total_reviews = BookingReview.objects.filter(
        booking__activity__activity_type="Scuba diving", is_deleted=False
    ).count()
    scuba_diving_average_rating = BookingReview.objects.filter(
        booking__activity__activity_type="Scuba diving", is_deleted=False
    ).aggregate(avg=Avg('rating'))['avg'] or 0

    dolphin_watching_total_reviews = BookingReview.objects.filter(
        booking__activity__activity_type="Dolphin watching", is_deleted=False
    ).count()
    dolphin_watching_average_rating = BookingReview.objects.filter(
        booking__activity__activity_type="Dolphin watching", is_deleted=False
    ).aggregate(avg=Avg('rating'))['avg'] or 0

    water_ski_total_reviews = BookingReview.objects.filter(
        booking__activity__activity_type="Water ski", is_deleted=False
    ).count()
    water_ski_average_rating = BookingReview.objects.filter(
        booking__activity__activity_type="Water ski", is_deleted=False
    ).aggregate(avg=Avg('rating'))['avg'] or 0

    speed_boat_total_reviews = BookingReview.objects.filter(
        booking__activity__activity_type="Speed boat", is_deleted=False
    ).count()
    speed_boat_average_rating = BookingReview.objects.filter(
        booking__activity__activity_type="Speed boat", is_deleted=False
    ).aggregate(avg=Avg('rating'))['avg'] or 0

    # Get 5 random highest-rated reviews (no duplicates)
    top_reviews = list(BookingReview.objects.filter(is_deleted=False, rating=5).select_related('customer', 'booking__activity'))
    
    # If fewer than 5 five-star reviews, add 4-star reviews
    if len(top_reviews) < 5:
        four_star_reviews = list(BookingReview.objects.filter(is_deleted=False, rating=4).select_related('customer', 'booking__activity'))
        top_reviews.extend(four_star_reviews)
    
    # Randomly select 5 unique reviews
    if len(top_reviews) >= 5:
        random_reviews = random.sample(top_reviews, 5)
    else:
        random_reviews = top_reviews

    context = {
        'catamaran_avg': round(catamaran_average_rating, 1),
        'catamaran_tot': catamaran_total_reviews,
        'scuba_avg': round(scuba_diving_average_rating, 1),
        'scuba_tot': scuba_diving_total_reviews,
        'dolphin_avg': round(dolphin_watching_average_rating, 1),
        'dolphin_tot': dolphin_watching_total_reviews,
        'ski_avg': round(water_ski_average_rating, 1),
        'ski_tot': water_ski_total_reviews,
        'boat_avg': round(speed_boat_average_rating, 1),
        'boat_tot': speed_boat_total_reviews,
        'reviews': random_reviews,
    }

    if request.user.is_authenticated:
        return render(request, 'homepage.html', context)
    else:
        return render(request, 'guest_homepage.html', context)

def about_us_view(request):
    """About us page"""
    return render(request, 'about_us.html')

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from .models import User

@login_required(login_url='login')
def profile(request):
    user = request.user

    if request.method == "POST":
        # Password verification check (for AJAX request)
        if 'verify_password' in request.POST:
            password = request.POST.get('verify_password')
            is_valid = check_password(password, request.user.password)
            return JsonResponse({'password_valid': is_valid})

        # Regular form submission
        new_first = request.POST.get("first_name", "").strip()
        new_last = request.POST.get("last_name", "").strip()
        new_email = request.POST.get("email", "").strip()
        new_phone = request.POST.get("phone", "").strip()
        new_username = request.POST.get("uname", "").strip()  # Changed from "username" to "uname" to match your form
        new_password = request.POST.get("pwd", "").strip()  # Changed from "password" to "pwd" to match your form

        # -------------------
        # VALIDATION
        # -------------------

        # Email validation
        try:
            validate_email(new_email)
        except ValidationError:
            messages.error(request, "Invalid email format.")
            return redirect("profile")

        # Email uniqueness
        if User.objects.filter(email=new_email).exclude(id=user.id).exists():
            messages.error(request, "This email is already used by another account.")
            return redirect("profile")

        # Username uniqueness
        if User.objects.filter(username=new_username).exclude(id=user.id).exists():
            messages.error(request, "This username is already taken.")
            return redirect("profile")

        # Phone validation
        if new_phone and not new_phone.replace("+", "").replace(" ", "").isdigit():
            messages.error(request, "Phone number must contain digits only.")
            return redirect("profile")

        # Password validation (only if password was entered)
        if new_password and len(new_password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return redirect("profile")

        # -------------------
        # UPDATE USER FIELDS
        # -------------------
        user.first_name = new_first
        user.last_name = new_last
        user.email = new_email
        user.phone = new_phone
        user.username = new_username
        
        # Only update password if a new one was provided
        if new_password:
            user.password = make_password(new_password)

        user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect("profile")

    # GET request → show profile page
    context = {
        "active_class": "User Profile",
        "user": user,
    }
    return render(request, "profile.html", context)


def signup(request):
    """Handle user signup using Django forms"""
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                messages.success(request, 'Account created successfully! Please log in.')
                return redirect('login')
            except Exception as e:
                messages.error(request, f'Error creating account: {str(e)}')
        else:
            # Display form validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                        messages.error(request, error)
                    else:
                        field_name = field.replace('_', ' ').title()
                        messages.error(request, f'{field_name}: {error}')

    return render(request, 'signup.html')


def login_view(request):
    """Handle user login using Django forms"""
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name}!')
            return redirect('homepage')
        else:
            # Display form validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                        messages.error(request, error)
                    else:
                        field_name = field.replace('_', ' ').title()
                        messages.error(request, f'{field_name}: {error}')

    return render(request, 'login.html')


def logout_view(request):
    """Handle user logout"""
    logout(request)
    return redirect('homepage')


@csrf_protect
@login_required
@user_passes_test(lambda u: u.is_staff, login_url='login')
def delete_review(request, review_id):
    """Soft delete a review"""
    if request.method == "POST":
        review = get_object_or_404(BookingReview, id=review_id)
        review.is_deleted = True
        review.save()
        messages.success(request, "Review deleted successfully!")
    return redirect("reviews")


@csrf_protect
@login_required
@user_passes_test(lambda u: u.is_staff, login_url='login')
def cancel_booking(request, booking_id):
    """Cancel a booking"""
    if request.method == "POST":
        booking = get_object_or_404(Booking, id=booking_id)
        booking.status = Booking.Status.CANCELLED
        booking.cancelled_at = timezone.now()
        booking.cancellation_reason = request.POST.get('reason', '')
        booking.save()
        payment = Payment.objects.get(booking=booking_id)
        payment.status = 'REFUNDED'
        payment.save()

        # Create notification for customer
        Notification.objects.create(
            user=booking.customer,
            title="Booking Cancelled",
            message=f"Your booking for {booking.activity.name} on {booking.date} has been cancelled due to harsh weather. "
                    f"Your safety is our priority. We apologize for the inconvenience.|||"
                    f"Booking Details:\n\n"
                    f"Activity: {booking.activity.name}\n\n"
                    f"Date: {booking.date}\n\n"
                    f"People: {booking.group_size}\n\n"
                    f"Amount: Rs {booking.price_total}\n\n"
                    f"A refund will be processed within 5–7 business days."
            ,
            type=Notification.Type.BOOKING_CANCELLED
        )
        messages.success(request, f"Booking #{booking.id} cancelled successfully!")
    return redirect("bookings")

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Booking

@login_required(login_url='login')
def profile_booking(request):
    """User bookings - dynamically load bookings"""
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    
    # Update booking statuses for past dates
    refresh_bookings()
    
    user_bookings = Booking.objects.filter(customer=request.user).select_related('activity').order_by('-created_at')
    
    # Filter by status
    status = request.GET.get('status')
    if status and status != 'all':
        user_bookings = user_bookings.filter(status=status.upper())
    
    # Filter by activity
    activity = request.GET.get('activity')
    if activity and activity != 'all':
        user_bookings = user_bookings.filter(activity__activity_type=activity)
    
    # Search filter
    search = request.GET.get('search')
    if search:
        user_bookings = user_bookings.filter(
            Q(activity__name__icontains=search) |
            Q(id__icontains=search)
        )
    
    # Get unique activity types for filter
    unique_activities = Booking.objects.filter(customer=request.user).values_list('activity__activity_type', flat=True).distinct()
    
    # Pagination - 10 bookings per page
    paginator = Paginator(user_bookings, 10)
    page = request.GET.get('page', 1)
    
    try:
        bookings_page = paginator.page(page)
    except PageNotAnInteger:
        bookings_page = paginator.page(1)
    except EmptyPage:
        bookings_page = paginator.page(paginator.num_pages)
    
    context = {
        'active_class': 'Bookings',
        'bookings': bookings_page,
        'unique_activities': unique_activities,
        'current_status': status or 'all',
        'current_activity': activity or 'all',
        'current_search': search or '',
    }
    return render(request, 'profile_booking.html', context)


@csrf_protect
@login_required(login_url='login')
def user_cancel_booking(request, booking_id):
    """User cancel booking - only for their own confirmed bookings"""
    if request.method == "POST":
        booking = get_object_or_404(Booking, id=booking_id)
        
        # Security: only the booking owner can cancel
        if booking.customer != request.user:
            messages.error(request, "You are not authorized to cancel this booking.")
            return redirect('profile_booking')
        
        # Only confirmed bookings can be cancelled
        if booking.status != Booking.Status.CONFIRMED:
            messages.error(request, "Only confirmed bookings can be cancelled.")
            return redirect('profile_booking')
        
        # Update booking status
        booking.status = Booking.Status.CANCELLED
        booking.cancelled_at = timezone.now()
        booking.save()
        
        # Update payment status to REFUNDED
        try:
            payment = Payment.objects.get(booking=booking)
            payment.status = Payment.Status.REFUNDED
            payment.save()
        except Payment.DoesNotExist:
            pass  # No payment found, continue anyway

        # Create notification for customer
        Notification.objects.create(
            user=booking.customer,
            title="Booking Cancelled",
            message=f"Your booking for {booking.activity.name} on {booking.date} has been cancelled as requested. \n"
                    f"We are saddened not to see you and hope to welcome you soon.|||"
                    f"Booking Details:\n\n"
                    f"Activity: {booking.activity.name}\n\n"
                    f"Date: {booking.date}\n\n"
                    f"People: {booking.group_size}\n\n"
                    f"Amount: Rs {booking.price_total}\n\n"
                    f"A refund will be processed within 5–7 business days."
            ,
            type=Notification.Type.BOOKING_CANCELLED
        )
        
        messages.success(request, f"Booking #{booking.id} has been cancelled successfully. Your refund will be processed.")
    
    return redirect('profile_booking')


@login_required(login_url='login')
def review(request, booking_id):
    """
    GET: show review form for a booking (only if the booking belongs to user and is COMPLETED)
    POST: create or update BookingReview for the booking
    """
    booking = get_object_or_404(Booking, pk=booking_id)

    # security: only owner can review and only completed bookings
    if booking.customer != request.user:
        messages.error(request, "You are not allowed to review this booking.")
        return redirect('profile_booking')

    if booking.status != Booking.Status.COMPLETED:
        messages.error(request, "Only completed bookings can be reviewed.")
        return redirect('profile_booking')

    # try get existing review
    try:
        existing = booking.review
    except BookingReview.DoesNotExist:
        existing = None

    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '').strip()

        try:
            rating = int(rating)
        except (TypeError, ValueError):
            messages.error(request, "Please provide a valid rating (1-5).")
            return redirect('review', booking_id=booking_id)

        if rating < 1 or rating > 5:
            messages.error(request, "Rating must be between 1 and 5.")
            return redirect('review', booking_id=booking_id)

        if existing:
            existing.rating = rating
            existing.comment = comment
            existing.is_deleted = False
            existing.save()
            messages.success(request, "Your review has been updated.")
        else:
            BookingReview.objects.create(
                booking=booking,
                customer=request.user,
                rating=rating,
                comment=comment,
            )
            messages.success(request, "Thank you — your review has been saved.")

        # redirect back to profile bookings (where user came from)
        return redirect('profile_booking')

    # GET: render form
    context = {
        'booking': booking,
        'activity': booking.activity,
        'existing_review': existing,
    }
    return render(request, 'review.html', context)


def activity_list(request):
    """
    Display activities grouped by type - pulls from database
    """
    activities_by_type = {}
    activities = Activity.objects.all().prefetch_related('images').order_by('activity_type', 'name')

    for activity in activities:
        activity_type = activity.activity_type or 'Other'
        activities_by_type.setdefault(activity_type, [])

        if activity_type not in activities_by_type:

            activities_by_type[activity_type] = []

        

        image_url = 'images/placeholder.png'
        if activity.images.exists():
            image_url = activity.images.first().image.url

        activities_by_type[activity_type].append({
            'name': activity.name,
            'image': image_url,
            'id': activity.id,
        })

    return render(request, 'activities_browse.html', {
        'activities_by_type': activities_by_type,
    })


@login_required(login_url='login')
@csrf_protect
def payment(request, activity_name):
    # When form is submitted (POST with card info)
    if request.method == 'POST' and 'card_number' in request.POST:
        activity_id = request.POST.get('activity_id')
        booking_date = request.POST.get('booking_date')
        num_people = request.POST.get('num_people')
        total_price = request.POST.get('total_price')

        if not all([activity_id, booking_date, num_people, total_price]):
            messages.error(request, "Invalid booking data.")
            return redirect('homepage')

        form = PaymentForm(request.POST)

        if form.is_valid():
            try:
                activity = get_object_or_404(Activity, id=activity_id)
                booking = Booking.objects.create(
                    customer=request.user,
                    activity=activity,
                    date=booking_date,
                    group_size=int(num_people),
                    price_total=int(total_price),
                    status=Booking.Status.CONFIRMED
                )

                Payment.objects.create(
                    booking=booking,
                    amount=int(total_price),
                    method=Payment.Method.CARD,
                    status=Payment.Status.PAID,
                    provider='Card Payment',
                    paid_at=timezone.now(),
                )
                # -------------------------------
                # Card info is validated but NOT stored
                # form.cleaned_data['card_number']
                # form.cleaned_data['card_name']
                # form.cleaned_data['expiry_date']
                # form.cleaned_data['cvv']
                # all used ONLY for validation
                # -------------------------------

                Notification.objects.create(
                    user=request.user,
                    title="Booking Confirmed",
                    message=f"Your booking for {activity.name} on {booking_date} has been successfully confirmed. "
                            f"If you have any questions or need to make changes to your booking, "
                            f"please contact us or visit your bookings page.|||"
                            f"Booking Details:\n\n"
                            f"Activity: {activity.name}\n\n"
                            f"Date: {booking_date}\n\n"
                            f"Number of People: {num_people}\n\n"
                            f"Total Amount: Rs{total_price}\n\n"
                            f"We look forward to seeing you on {booking_date}. "
                    ,
                    type=Notification.Type.BOOKING_CONFIRMED
                )


                messages.success(request, "Payment successful! Booking confirmed.")
                return redirect('profile_booking')
            except Exception as e:
                messages.error(request, f"Booking failed: {str(e)}")
                return redirect('homepage')
        else:
            # Form invalid - re-display payment page
            activity = get_object_or_404(Activity, id=activity_id)
            context = {
                'activity_name': activity.name,
                'activity_date': booking_date,
                'num_people': num_people,
                'total_price': total_price,
                'activity_id': activity_id,
                'form': form,
            }
            messages.error(request, "Please correct the errors below.")
            return render(request, 'payment.html', context)

    if request.method == 'POST':
        activity_id = request.POST.get('activity_id')
        booking_date = request.POST.get('booking_date')
        num_people = request.POST.get('num_people')
        total_price = request.POST.get('total_price')
    else:
        activity_id = request.GET.get('activity_id')
        booking_date = request.GET.get('booking_date')
        num_people = request.GET.get('num_people')
        total_price = request.GET.get('total_price')

    if not all([activity_id, booking_date, num_people, total_price]):
        messages.error(request, "Invalid booking data. Please try again.")
        return redirect('homepage')

    activity = get_object_or_404(Activity, id=activity_id)
    form = PaymentForm()

    context = {
        'activity_name': activity.name,
        'activity_date': booking_date,
        'num_people': num_people,
        'total_price': total_price,
        'activity_id': activity_id,
        'form': form,
    }
    return render(request, 'payment.html', context)


@login_required(login_url='login')
def notifications(request):
    user_notifications = Notification.objects.filter(user=request.user)
    
    # Split messages into parts
    notifications_with_parts = []
    for note in user_notifications:
        parts = note.message.split('|||')
        notifications_with_parts.append({
            'id': note.id,
            'title': note.title,
            'message_part': parts[0].strip() if len(parts) > 0 else '',
            'details_part': parts[1].strip() if len(parts) > 1 else '',
            'created_at': note.created_at
        })
    
    context = {
        'active_class': "Notifications",
        'notifications': notifications_with_parts
    }
    return render(request, 'notifications.html', context)

def refresh_bookings():
    from django.utils.timezone import localdate
    # Find bookings to complete (bookings with dates before today)
    today = localdate()
    bookings_to_complete = Booking.objects.filter(
        status=Booking.Status.CONFIRMED,
        date__lt=today
    )

    for booking in bookings_to_complete:
        # Create notification
        review_url = f"/grandblue/user/review/{booking.id}/"
        
        Notification.objects.create(
            user=booking.customer,
            title="Booking Completed",
            message=f"We hope you enjoyed your experience! Please consider leaving a review. <a href='{review_url}' class='review-link'>Leave a Review</a>|||"
                    f"Booking Details:\n\n"
                    f"Activity: {booking.activity.name}\n\n"
                    f"Date: {booking.date}\n\n"
                    f"People: {booking.group_size}\n\n"
                    f"Amount: Rs {booking.price_total}",
            type=Notification.Type.BOOKING_COMPLETED
        )
        
        # Update status
        booking.status = Booking.Status.COMPLETED
        booking.save()

@login_required
@user_passes_test(lambda u: u.is_staff, login_url='login')
def download_revenue_report(request):
    """Generate detailed monthly revenue report with all transactions"""
    
    # Get all payments with paid_at not null, ordered by date
    payments = Payment.objects.exclude(paid_at__isnull=True).select_related(
        'booking__customer', 'booking__activity'
    ).order_by('paid_at')
    
    # Group payments by month
    monthly_payments = {}
    for payment in payments:
        month_key = payment.paid_at.strftime('%Y-%m')
        month_name = payment.paid_at.strftime('%B %Y')
        
        if month_key not in monthly_payments:
            monthly_payments[month_key] = {
                'name': month_name,
                'payments': [],
                'expected_revenue': 0,
                'realized_revenue': 0
            }
        
        monthly_payments[month_key]['payments'].append(payment)
        monthly_payments[month_key]['expected_revenue'] += payment.amount
        
        if payment.status == 'PAID':
            monthly_payments[month_key]['realized_revenue'] += payment.amount
    
    # Create PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="detailed_revenue_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
    
    # Create canvas
    pdf = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    
    # Initialize variables for totals
    grand_expected = 0
    grand_realized = 0
    
    # Start position
    y_position = height - 0.75 * inch
    
    # Title
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(1 * inch, y_position, "Detailed Revenue Report")
    y_position -= 0.4 * inch
    
    # Generated date
    pdf.setFont("Helvetica", 11)
    pdf.drawString(1 * inch, y_position, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    y_position -= 0.6 * inch
    
    # Process each month
    for month_key in sorted(monthly_payments.keys()):
        month_data = monthly_payments[month_key]
        
        # Check if we need a new page
        if y_position < 2.5 * inch:
            pdf.showPage()
            y_position = height - 0.75 * inch
        
        # Month header
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(1 * inch, y_position, f"Month: {month_data['name']}")
        y_position -= 0.35 * inch
        
        # Transaction table header
        pdf.setFont("Helvetica-Bold", 9)
        pdf.drawString(1 * inch, y_position, "ID")
        pdf.drawString(1.6 * inch, y_position, "Customer")
        pdf.drawString(3 * inch, y_position, "Activity")
        pdf.drawString(4.8 * inch, y_position, "Amount (Rs)")
        pdf.drawString(5.8 * inch, y_position, "Status")
        pdf.drawString(6.6 * inch, y_position, "Date")
        y_position -= 0.05 * inch
        
        # Draw line under header
        pdf.line(1 * inch, y_position, 7.5 * inch, y_position)
        y_position -= 0.2 * inch
        
        # Transaction details
        pdf.setFont("Helvetica", 8)
        for payment in month_data['payments']:
            # Check for page break
            if y_position < 1 * inch:
                pdf.showPage()
                y_position = height - 0.75 * inch
                
                # Redraw header on new page
                pdf.setFont("Helvetica-Bold", 9)
                pdf.drawString(1 * inch, y_position, "ID")
                pdf.drawString(1.6 * inch, y_position, "Customer")
                pdf.drawString(3 * inch, y_position, "Activity")
                pdf.drawString(4.8 * inch, y_position, "Amount (Rs)")
                pdf.drawString(5.8 * inch, y_position, "Status")
                pdf.drawString(6.6 * inch, y_position, "Date")
                y_position -= 0.25 * inch
                pdf.setFont("Helvetica", 8)
            
            # Transaction details
            customer_name = f"{payment.booking.customer.first_name} {payment.booking.customer.last_name}"
            if len(customer_name) > 20:
                customer_name = customer_name[:18] + "..."
            
            activity_name = payment.booking.activity.name
            if len(activity_name) > 25:
                activity_name = activity_name[:23] + "..."
            
            pdf.drawString(1 * inch, y_position, f"T{payment.id}")
            pdf.drawString(1.6 * inch, y_position, customer_name)
            pdf.drawString(3 * inch, y_position, activity_name)
            pdf.drawRightString(5.5 * inch, y_position, f"{payment.amount:,}")
            
            # Status with color
            if payment.status == 'PAID':
                pdf.setFillColor(colors.green)
            else:
                pdf.setFillColor(colors.red)
            pdf.drawString(5.8 * inch, y_position, payment.get_status_display())
            pdf.setFillColor(colors.black)
            
            pdf.drawString(6.6 * inch, y_position, payment.paid_at.strftime('%Y-%m-%d'))
            y_position -= 0.18 * inch
        
        # Month summary
        y_position -= 0.15 * inch
        pdf.line(4.5 * inch, y_position, 7.5 * inch, y_position)
        y_position -= 0.25 * inch
        
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(4.5 * inch, y_position, "Expected Revenue:")
        pdf.drawRightString(7.5 * inch, y_position, f"Rs {month_data['expected_revenue']:,}")
        y_position -= 0.2 * inch
        
        pdf.drawString(4.5 * inch, y_position, "Realized Revenue:")
        pdf.setFillColor(colors.green)
        pdf.drawRightString(7.5 * inch, y_position, f"Rs {month_data['realized_revenue']:,}")
        pdf.setFillColor(colors.black)
        y_position -= 0.2 * inch
        
        pdf.setFont("Helvetica", 9)
        refunded_amount = month_data['expected_revenue'] - month_data['realized_revenue']
        pdf.drawString(4.5 * inch, y_position, "Refunded Amount:")
        pdf.setFillColor(colors.red)
        pdf.drawRightString(7.5 * inch, y_position, f"Rs {refunded_amount:,}")
        pdf.setFillColor(colors.black)
        y_position -= 0.5 * inch
        
        # Add to grand totals
        grand_expected += month_data['expected_revenue']
        grand_realized += month_data['realized_revenue']
    
    # Grand totals section
    if y_position < 2 * inch:
        pdf.showPage()
        y_position = height - 0.75 * inch
    
    y_position -= 0.3 * inch
    pdf.setLineWidth(2)
    pdf.line(1 * inch, y_position, 7.5 * inch, y_position)
    y_position -= 0.35 * inch
    
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(1 * inch, y_position, "GRAND TOTALS")
    y_position -= 0.35 * inch
    
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(1 * inch, y_position, "Total Expected Revenue:")
    pdf.drawRightString(7.5 * inch, y_position, f"Rs {grand_expected:,}")
    y_position -= 0.3 * inch
    
    pdf.drawString(1 * inch, y_position, "Total Realized Revenue:")
    pdf.setFillColor(colors.green)
    pdf.drawRightString(7.5 * inch, y_position, f"Rs {grand_realized:,}")
    pdf.setFillColor(colors.black)
    y_position -= 0.3 * inch
    
    total_refunded = grand_expected - grand_realized
    pdf.drawString(1 * inch, y_position, "Total Refunded Amount:")
    pdf.setFillColor(colors.red)
    pdf.drawRightString(7.5 * inch, y_position, f"Rs {total_refunded:,}")
    pdf.setFillColor(colors.black)
    
    # Footer
    pdf.setFont("Helvetica-Oblique", 8)
    pdf.drawString(1 * inch, 0.5 * inch, "Grand Blue - Confidential Financial Report")
    
    pdf.showPage()
    pdf.save()
    
    return response

def your_view(request):
    add_form = ActivityForm()
    edit_form = ActivityForm()

    # Fetch all activities from database
    activities = Activity.objects.all()
    
    context = {
        'activities': activities,
        'add_form': add_form,
        'edit_form': edit_form,
    }
    return render(request, 'admin_activity.html', context)

from django.core.mail import send_mail
from django.conf import settings

def contact(request):
    """
    Contact page - allows users to send messages via email
    Sends email to website and acknowledgement to user
    """
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            
            try:
                # Send email to website
                website_message = f"""
New Contact Form Submission

From: {name}
Email: {email}
Subject: {subject}

Message:
{message}
"""
                send_mail(
                    subject=f'Contact Form: {subject}',
                    message=website_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.EMAIL_HOST_USER],
                    fail_silently=False,
                )
                
                # Send acknowledgement to user
                acknowledgement = f"""
Dear {name},

Thank you for contacting Grand Blue Mauritius!

We have received your message and will get back to you as soon as possible.

Your message:
Subject: {subject}
{message}

Best regards,
Grand Blue Mauritius Team
"""
                send_mail(
                    subject='Thank you for contacting Grand Blue Mauritius',
                    message=acknowledgement,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
                
                messages.success(request, 'Thank you for your message! We will get back to you soon. Check your email for confirmation.')
                return redirect('contact')
                
            except Exception as e:
                messages.error(request, f'Sorry, there was an error sending your message. Please try again later.')
        else:
            # Display form validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                        messages.error(request, error)
                    else:
                        field_name = field.replace('_', ' ').title()
                        messages.error(request, f'{field_name}: {error}')
    else:
        form = ContactForm()
    
    return render(request, 'contact.html', {'form': form})


def terms_and_condition(request):
    return render(request, 'T&C.html')