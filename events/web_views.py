from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Event, Registration


def home(request):
    """Home view listing all upcoming active events with search and filters."""
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()

    events = Event.objects.filter(is_active=True)

    if query:
        events = events.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(location__icontains=query)
        )

    if category and category != 'ALL':
        events = events.filter(category=category)

    events = events.order_by('date')

    categories = Event.CATEGORY_CHOICES

    return render(request, 'events/home.html', {
        'events': events,
        'categories': categories,
        'selected_category': category,
        'query': query,
    })


def event_detail(request, pk):
    """Detailed view for a specific event with registration form."""
    event = get_object_or_404(Event, pk=pk)

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        notes = request.POST.get('notes', '').strip()

        if not full_name or not email:
            messages.error(request, "Please fill in all required fields (Name and Email).")
            return redirect('event_detail', pk=pk)

        if event.is_full:
            messages.error(request, "Sorry, this event is already fully booked.")
            return redirect('event_detail', pk=pk)

        if Registration.objects.filter(event=event, email__iexact=email, status=Registration.STATUS_CONFIRMED).exists():
            messages.warning(request, f"You are already registered for this event with {email}!")
            return redirect('my_registrations')

        user = request.user if request.user.is_authenticated else None
        registration = Registration.objects.create(
            event=event,
            user=user,
            full_name=full_name,
            email=email,
            phone=phone,
            notes=notes,
            status=Registration.STATUS_CONFIRMED
        )
        messages.success(request, f"🎉 Congratulations {full_name}! Registration confirmed. Your Ticket Code is: {registration.ticket_code}")
        return redirect('my_registrations')

    return render(request, 'events/event_detail.html', {'event': event})


def my_registrations(request):
    """View and manage user registrations (view ticket, cancel)."""
    email_query = request.GET.get('email', '').strip()
    registrations = []

    if request.user.is_authenticated:
        registrations = Registration.objects.filter(
            Q(user=request.user) | Q(email__iexact=request.user.email)
        ).distinct().order_by('-created_at')
    elif email_query:
        registrations = Registration.objects.filter(email__iexact=email_query).order_by('-created_at')

    return render(request, 'events/my_registrations.html', {
        'registrations': registrations,
        'email_query': email_query
    })


def cancel_registration(request, pk):
    """Cancel a registration."""
    registration = get_object_or_404(Registration, pk=pk)

    if request.method == 'POST':
        registration.cancel()
        messages.info(request, f"Registration {registration.ticket_code} for '{registration.event.title}' has been cancelled.")
        return redirect('my_registrations')

    return render(request, 'events/confirm_cancel.html', {'registration': registration})


@login_required(login_url='login')
def create_event(request):
    """Organizer view to publish a new event."""
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        category = request.POST.get('category')
        location = request.POST.get('location')
        date = request.POST.get('date')
        capacity = request.POST.get('capacity', 50)
        image_url = request.POST.get('image_url', '')

        if not (title and description and location and date):
            messages.error(request, "Please fill in all mandatory fields.")
            return redirect('create_event')

        event = Event.objects.create(
            title=title,
            description=description,
            category=category,
            location=location,
            date=date,
            capacity=int(capacity),
            image_url=image_url,
            organizer=request.user
        )
        messages.success(request, f"Event '{event.title}' created successfully!")
        return redirect('event_detail', pk=event.pk)

    return render(request, 'events/create_event.html', {
        'categories': Event.CATEGORY_CHOICES
    })


def api_documentation_view(request):
    """Interactive API documentation page detailing all REST API endpoints."""
    return render(request, 'events/api_docs.html')


def user_login(request):
    """Web login view."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'events/login.html')


def user_signup(request):
    """Web signup view."""
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password')
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect('signup')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        login(request, user)
        messages.success(request, f"Account created! Welcome, {user.username}.")
        return redirect('home')

    return render(request, 'events/signup.html')


def user_logout(request):
    """Web logout view."""
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')
