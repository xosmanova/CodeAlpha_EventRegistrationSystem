from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Event, Registration
from .serializers import (
    EventSerializer,
    RegistrationSerializer,
    RegistrationCreateSerializer,
    UserSerializer,
    UserRegisterSerializer
)


class AuthRegisterView(APIView):
    """Register a new user account."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            login(request, user)
            return Response({
                "message": "User registered successfully.",
                "user": UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AuthLoginView(APIView):
    """Log in an existing user."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({
                "message": "Login successful.",
                "user": UserSerializer(user).data
            })
        return Response(
            {"detail": "Invalid username or password."},
            status=status.HTTP_401_UNAUTHORIZED
        )


class AuthLogoutView(APIView):
    """Log out current user."""
    def post(self, request):
        logout(request)
        return Response({"message": "Successfully logged out."})


class AuthCurrentUserView(APIView):
    """Get profile of current authenticated user."""
    def get(self, request):
        if request.user.is_authenticated:
            return Response(UserSerializer(request.user).data)
        return Response({"authenticated": False, "user": None})


class EventListCreateAPIView(generics.ListCreateAPIView):
    """
    GET: List all active events (supports search via `?search=...` and category filter `?category=...`).
    POST: Create a new event (Authenticated users / Organizers).
    """
    serializer_class = EventSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        queryset = Event.objects.filter(is_active=True).order_by('date')
        
        # Search filter
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(location__icontains=search)
            )

        # Category filter
        category = self.request.query_params.get('category')
        if category and category != 'ALL':
            queryset = queryset.filter(category=category)

        return queryset

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)


class EventDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: View specific event details.
    PUT/PATCH/DELETE: Update or delete event (Organizer or Staff only).
    """
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def check_object_permissions(self, request, obj):
        super().check_object_permissions(request, obj)
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            if not (request.user.is_staff or obj.organizer == request.user):
                self.permission_denied(
                    request,
                    message="You do not have permission to modify this event."
                )


class RegistrationCreateAPIView(APIView):
    """
    POST: Submit a registration for an event.
    Associates with authenticated user if logged in, or guest details.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, event_id=None):
        data = request.data.copy()
        if event_id:
            data['event'] = event_id

        # Auto-fill user info if authenticated
        if request.user.is_authenticated:
            if not data.get('full_name'):
                full_name = f"{request.user.first_name} {request.user.last_name}".strip()
                data['full_name'] = full_name or request.user.username
            if not data.get('email'):
                data['email'] = request.user.email

        serializer = RegistrationCreateSerializer(data=data)
        if serializer.is_valid():
            user = request.user if request.user.is_authenticated else None
            registration = serializer.save(user=user)
            return Response({
                "message": "Registration successful! You have secured your seat.",
                "registration": RegistrationSerializer(registration).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MyRegistrationsAPIView(APIView):
    """
    GET: View user registrations.
    If authenticated, returns the user's registrations.
    If guest, can lookup by query parameter `?email=example@domain.com`.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        email = request.query_params.get('email')

        if request.user.is_authenticated:
            # Query either by user FK or by user's email
            queryset = Registration.objects.filter(
                Q(user=request.user) | Q(email__iexact=request.user.email)
            ).distinct().order_by('-created_at')
        elif email:
            queryset = Registration.objects.filter(email__iexact=email).order_by('-created_at')
        else:
            return Response(
                {"detail": "Please log in or provide an '?email=...' query parameter to view your registrations."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = RegistrationSerializer(queryset, many=True)
        return Response(serializer.data)


class RegistrationCancelAPIView(APIView):
    """
    POST / DELETE: Cancel a registration.
    Allows user to cancel their registration and free up a seat.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, pk):
        try:
            reg = Registration.objects.get(pk=pk)
        except Registration.DoesNotExist:
            return Response({"detail": "Registration not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check permissions: if registration belongs to a user, ensure the requesting user matches, or match email verification
        if request.user.is_authenticated:
            if reg.user and reg.user != request.user and not request.user.is_staff:
                return Response({"detail": "Unauthorized to cancel this registration."}, status=status.HTTP_403_FORBIDDEN)
        else:
            provided_email = request.data.get('email') or request.query_params.get('email')
            if provided_email and provided_email.lower() != reg.email.lower():
                return Response({"detail": "Email does not match this registration."}, status=status.HTTP_403_FORBIDDEN)

        if reg.status == Registration.STATUS_CANCELLED:
            return Response({"message": "This registration is already cancelled."}, status=status.HTTP_200_OK)

        reg.cancel()
        return Response({
            "message": "Registration successfully cancelled. The seat has been freed.",
            "registration": RegistrationSerializer(reg).data
        })

    def delete(self, request, pk):
        return self.post(request, pk)


class EventAttendeesAPIView(APIView):
    """
    GET: View list of attendees for an event (Organizer or Staff only).
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, event_id):
        try:
            event = Event.objects.get(pk=event_id)
        except Event.DoesNotExist:
            return Response({"detail": "Event not found."}, status=status.HTTP_404_NOT_FOUND)

        if not (request.user.is_staff or event.organizer == request.user):
            return Response(
                {"detail": "Only the event organizer or administrators can view attendees."},
                status=status.HTTP_403_FORBIDDEN
            )

        registrations = event.registrations.all().order_by('-created_at')
        serializer = RegistrationSerializer(registrations, many=True)
        return Response({
            "event": event.title,
            "total_registrations": registrations.count(),
            "confirmed_count": registrations.filter(status=Registration.STATUS_CONFIRMED).count(),
            "attendees": serializer.data
        })
