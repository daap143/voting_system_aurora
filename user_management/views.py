from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from user_management.models import Candidate, CitizenData
from aadhaar_voter_card.models import AadhaarVerification
from voting.models import VotingStatus
from .models import Admin
from django.contrib import messages
from .models import CitizenData
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.db.models import Q

# Home Page View
def home(request):
    return render(request, 'home_page.html')


# Admin Panel View for Custom Admin Login
def admin_panel(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        password = request.POST.get('password')

        try:
            # Validate credentials from the Admin table
            admin_user = Admin.objects.get(user_id=user_id, password=password)

            # If valid, redirect to the admin editing page
            request.session['admin_user_id'] = admin_user.user_id  # Set session for the logged-in admin
            return redirect('admin_editing')  # Redirect to the admin editing page
        except Admin.DoesNotExist:
            # If credentials are invalid, show error message
            messages.error(request, 'Invalid user ID or password.')
            return redirect('admin_panel')

    return render(request, 'admin_panel.html')  # Render the admin login page


@login_required
def admin_editing(request):
    # Ensure the admin user is logged in (session check)
    if 'admin_user_id' not in request.session:
        return redirect('admin_panel')

    # Render the admin editing page with buttons
    return render(request, 'admin_editing.html')


@login_required
def add_new_citizen(request):
    if request.method == 'POST':
        # Extract data from POST request
        citizen_name = request.POST.get('citizen_name')
        father_name = request.POST.get('father_name')
        gender = request.POST.get('gender')
        dob = request.POST.get('dob')
        address = request.POST.get('address')
        mobile = request.POST.get('mobile')
        email = request.POST.get('email')
        aadhaar_number = request.POST.get('aadhaar_number')
        voter_id_number = request.POST.get('voter_id_number')
        constituency = request.POST.get('constituency')  # Added constituency
        photo_aadhaar = request.FILES.get('photo_aadhaar')
        photo_voter = request.FILES.get('photo_voter')

        # Create a new CitizenData object and save it to the database
        try:
            citizen = CitizenData.objects.create(
                citizen_name=citizen_name,
                father_name=father_name,
                gender=gender,
                dob=dob,
                address=address,
                mobile=mobile,
                email=email,
                aadhaar_number=aadhaar_number,
                voter_id_number=voter_id_number,
                constituency=constituency,  # Save constituency
                photo_aadhaar=photo_aadhaar,
                photo_voter=photo_voter
            )
            citizen.save()
            
            # Show a success message and redirect to the admin editing page
            messages.success(request, 'Citizen successfully registered!')
            return redirect('admin_editing')
        except Exception as e:
            # Show an error message if the registration fails
            messages.error(request, f'Error: {str(e)}')
    return render(request, 'add_new_citizen.html')



@login_required
def edit_existing_citizen(request):
    return render(request, 'edit_existing_citizen.html')

from django.views.decorators.csrf import csrf_exempt

# search existing citizen for edit
class EditExistingCitizenView(TemplateView):
    template_name = 'edit_existing_citizen.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('query', '')

        if query:
            citizens = CitizenData.objects.filter(
                Q(aadhaar_number__icontains=query) |
                Q(voter_id_number__icontains=query) |
                Q(citizen_name__icontains=query)
            )
        else:
            citizens = CitizenData.objects.none()

        context['citizens'] = citizens
        return context

def citizen_search_ajax(request):
    query = request.GET.get('query', '')

    citizens = CitizenData.objects.filter(
        Q(aadhaar_number__icontains=query) |
        Q(voter_id_number__icontains=query) |
        Q(citizen_name__icontains=query)
    )

    results = list(citizens.values('id', 'citizen_name', 'aadhaar_number', 'voter_id_number', 'constituency'))
    return JsonResponse(results, safe=False)




@login_required
def edit_citizen2(request, citizen_id):
    # Get the citizen object by ID
    citizen = get_object_or_404(CitizenData, id=citizen_id)
    
    if request.method == 'POST':
        # Update citizen's data with the form input
        citizen.citizen_name = request.POST.get('citizen_name')
        citizen.father_name = request.POST.get('father_name')
        citizen.gender = request.POST.get('gender')
        citizen.dob = request.POST.get('dob')
        citizen.address = request.POST.get('address')
        citizen.mobile = request.POST.get('mobile')
        citizen.email = request.POST.get('email')
        citizen.aadhaar_number = request.POST.get('aadhaar_number')
        citizen.voter_id_number = request.POST.get('voter_id_number')
        citizen.constituency = request.POST.get('constituency')
        
        citizen.save()  # Save the updated citizen data
        
        messages.success(request, 'Citizen information updated successfully.')
        return redirect('admin_editing')  # Redirect to admin editing page
    
    return render(request, 'edit_citizen2.html', {'citizen': citizen})


@login_required
def update_citizen(request, citizen_id):
    citizen = get_object_or_404(CitizenData, id=citizen_id)

    if request.method == 'POST':
        citizen.citizen_name = request.POST.get('citizen_name')
        citizen.father_name = request.POST.get('father_name')
        citizen.gender = request.POST.get('gender')
        citizen.dob = request.POST.get('dob')
        citizen.address = request.POST.get('address')
        citizen.mobile = request.POST.get('mobile')
        citizen.email = request.POST.get('email')
        citizen.aadhaar_number = request.POST.get('aadhaar_number')
        citizen.voter_id_number = request.POST.get('voter_id_number')
        citizen.constituency = request.POST.get('constituency')

        citizen.save()  # Save updated citizen data
        messages.success(request, 'Citizen information updated successfully.')
        return redirect('admin_editing')  # Redirect to the admin editing page

    return render(request, 'edit_citizen2.html', {'citizen': citizen})





# @login_required
# def edit_citizen(request, citizen_id):
#     try:
#         citizen = CitizenData.objects.get(pk=citizen_id)
#         # You can add logic here to edit the citizen's data, handle the form, etc.
#         if request.method == 'POST':
#             citizen.citizen_name = request.POST['citizen_name']
#             citizen.father_name = request.POST['father_name']
#             citizen.address = request.POST['address']
#             # ... update other fields accordingly
#             citizen.save()
#             return redirect('edit_existing_citizen')  # Redirect after successful edit

#         return render(request, 'edit_citizen_form.html', {'citizen': citizen})
#     except CitizenData.DoesNotExist:
#         return redirect('edit_existing_citizen')



@login_required
def add_edit_candidate(request):
    return redirect('add_edit_candidate')  # You can replace this with the actual logic
























# Vote Status View
@login_required
def vote_status(request):
    pass

# Voting View
@login_required
def vote(request):
    pass

# Result View
@login_required
def result(request):
    pass