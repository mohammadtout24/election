from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count 
from .models import Candidate, Vote 

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import PermissionDenied


def submit_vote(request):
    if request.method == 'POST':
        candidate_id = request.POST.get('vote')
        user = request.user

        # --- BLOCK ADMIN VOTES ---
        if user.is_authenticated and (user.is_staff or user.is_superuser):
            messages.error(request, "Administrators are not allowed to submit votes.")
            return redirect('home')

        if not candidate_id:
            messages.error(request, "Please select a candidate before submitting your vote.")
            return redirect('home')

        candidate = get_object_or_404(Candidate, id=candidate_id)

        # Ensure session exists
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key

        # --- Prevent double voting (regular user check) ---
        if user.is_authenticated:
            if Vote.objects.filter(user=user).exists():
                messages.warning(request, "You have already voted.")
                return redirect('home')
        else:
            if Vote.objects.filter(session_key=session_key).exists():
                messages.warning(request, "You have already cast your vote in this browser.")
                return redirect('home')

        # --- Record vote ---
        Vote.objects.create(
            candidate=candidate,
            user=user if user.is_authenticated else None,
            session_key=session_key
        )

        request.session['voted_for'] = candidate.name
        messages.success(request, f"Thank you! Your vote for {candidate.name} has been recorded.")
        return redirect('home')

    return redirect('home')


@login_required
def home(request):
    if not request.session.session_key:
        request.session.create()

    user = request.user
    is_admin = user.is_authenticated and (user.is_staff or user.is_superuser)

    # 1. Determine if user has voted (Regular users only)
    has_voted_by_regular_user = False
    if not is_admin and user.is_authenticated:
        has_voted_by_regular_user = Vote.objects.filter(user=user).exists()
        
    voted_for_name = request.session.get('voted_for')

    # 2. Conditionally fetch results (Admins only) or candidate list (Voters only)
    candidates_with_votes = []
    total_votes = 0

    if is_admin:
        # Admin: Fetch full data (results)
        total_votes = Vote.objects.count()
        candidates_data = Candidate.objects.annotate(vote_count=Count('votes')).order_by('-vote_count')
        
        candidates_with_votes = [
            {
                'candidate': candidate,
                'vote_count': candidate.vote_count,
                'vote_percentage': round((candidate.vote_count / total_votes * 100), 1) if total_votes > 0 else 0
            }
            for candidate in candidates_data
        ]
    else:
        # Regular User: Fetch only candidate list (for voting form/info)
        candidates_data = Candidate.objects.all().order_by('name')
        candidates_with_votes = [
            {'candidate': candidate, 'vote_count': 0, 'vote_percentage': 0}
            for candidate in candidates_data
        ]
        
    # 3. Determine the template flow state
    show_results_or_confirmation = has_voted_by_regular_user or is_admin

    context = {
        'candidates_with_votes': candidates_with_votes,
        'total_votes': total_votes,
        'has_voted': show_results_or_confirmation, 
        'is_admin': is_admin,
        'voted_for_name': voted_for_name
    }

    return render(request, 'candidates/home.html', context)


# --- Candidate Profile Views ---

def candidate_detail(request, candidate_id):
    candidate = get_object_or_404(Candidate, id=candidate_id)
    return render(request, 'candidates/candidate_detail.html', {'candidate': candidate })


# --- Authentication Views ---

def login_view(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # --- CANCELED CANDIDATE CREATION ---
            # Candidate.objects.get_or_create(user=user)
            # You must now manually create Candidate profiles for those who need one.
            
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('home') 
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'candidates/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')