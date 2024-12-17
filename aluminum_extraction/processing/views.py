from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.contrib.auth.decorators import login_required
from .models import RawMaterial, Processing, ByProduct, UserProfile
from ml_model.predict import predict_aluminum_output  # Quantile regression prediction
from ml_model.reinforcement_learning import reinforcement_learning_simulation  # RL logic
from django.contrib.auth.models import User
from .forms import RawMaterialForm, ProcessingForm, ByProductForm, UserRegistrationForm, UserProfileForm
# from django.contrib import messages
from .models import UserProfile
from django.db import IntegrityError
import logging
# Start processing view with both ML and RL integration
from django.db import transaction
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout

def homepage(request):
    # Check if the user is authenticated and handle logout
    if request.user.is_authenticated:
        if 'logout' in request.GET:
            logout(request)
            return redirect('login')  # Redirect to the login page after logout
    
    raw_materials = RawMaterial.objects.all()
    if not raw_materials:
        raise Http404("No raw materials found.")
    
    return render(request, 'processing/homepage.html', {'raw_materials': raw_materials})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('homepage')  # If the user is already logged in, redirect to homepage
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                return redirect('homepage')
            else:
                return render(request, 'processing/login.html', {'form': form, 'error': 'Invalid username or password.'})
        else:
            return render(request, 'processing/login.html', {'form': form, 'error': 'Please correct the errors below.'})
    else:
        form = AuthenticationForm()
    return render(request, 'processing/login.html', {'form': form})

def logout_view(request):
    logout(request)  # This will log out the user and clear the session
    return redirect('login')  # Redirect to login page

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        # confirm_password = request.POST.get('confirm_password')
        role = request.POST.get('role')

        print(f"POST Data: username={username}, email={email}, password={password}, role={role}")

        # Check for missing fields
        if not username or not email or not password or not role:
            return render(request, 'processing/register.html', {'error': 'All fields are required.'})

        # Check password match
        # if password != confirm_password:
        #     return render(request, 'processing/register.html', {'error': 'Passwords do not match.'})

        try:
            # Create User and UserProfile
            user = User.objects.create_user(username=username, email=email, password=password)
            UserProfile.objects.create(user=user, role=role)
            # Ensure the user is saved and authenticated
            user.save()

            print(f"User and UserProfile created successfully for {username}")
            return redirect('login')
        except IntegrityError as e:
            if 'Duplicate entry' in str(e):
                return render(request, 'processing/register.html', {'error': 'Email or Username already exists.'})
            print(f"IntegrityError: {e}")
            return render(request, 'processing/register.html', {'error': 'An unexpected error occurred.'})

    return render(request, 'processing/register.html')


def add_raw_material(request):
    if request.method == 'POST':
        form = RawMaterialForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('homepage')  # Replace with your home page URL name
    else:
        form = RawMaterialForm()
    return render(request, 'processing/add_raw_material.html', {'form': form})

def add_processing(request):
    if request.method == 'POST':
        form = ProcessingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('homepage')
    else:
        form = ProcessingForm()
    return render(request, 'processing/add_processing.html', {'form': form})

def add_byproduct(request):
    if request.method == 'POST':
        form = ByProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('homepage')
    else:
        form = ByProductForm()
    return render(request, 'processing/add_byproduct.html', {'form': form})


def register_user(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            return redirect('login')  # Replace with your login page URL name
    else:
        user_form = UserRegistrationForm()
        profile_form = UserProfileForm()
    return render(request, 'processing/register_user.html', {'user_form': user_form, 'profile_form': profile_form})

def calculate_byproducts(final_output):
    # Generate by-products based on the aluminum output
    slag = final_output * 0.4  # 40% of the output becomes slag
    scraps = final_output * 0.2  # 20% of the output is scrap
      # Return a list of dictionaries, not just a dictionary
    return [
        {'name': 'slag', 'quantity': slag, },
        {'name': 'scraps', 'quantity': scraps,}
    ]

# Define raw materials
raw_materials = [
    {"quantity": 200, "quality": 90},  # High quantity and quality
    {"quantity": 150, "quality": 85},  # Moderate quantity and quality
    {"quantity": 100, "quality": 95},  # Lower quantity but high quality
    {"quantity": 250, "quality": 80},  # High quantity, lower quality
    {"quantity": 180, "quality": 88},  # Balanced
    {"quantity": 120, "quality": 92},  # Moderate
    {"quantity": 300, "quality": 70},  # High quantity, low quality
    {"quantity": 220, "quality": 85}   # High quantity, moderate quality
]

# Process raw materials
for raw_material in raw_materials:
    initial_estimate = predict_aluminum_output(raw_material)
    rl_adjusted_output = reinforcement_learning_simulation()
    final_output_estimate = initial_estimate * rl_adjusted_output

    # Assign statuses based on thresholds
    if final_output_estimate < 50:
        status = 'Failed'
    elif 50 <= final_output_estimate < 10000:
        status = 'Pending'
    else:
        status = 'Completed'
    
    # Calculate by-products
    by_products = calculate_byproducts(final_output_estimate)
    
    # Save processing details (Replace this with actual saving logic)
    # print(f"Raw Material: {raw_material}, Final Estimate: {final_output_estimate:.2f}, "
    #       f"Status: {status}, By-Products: {by_products}")


@login_required
def start_processing(request, raw_material_id):
    # Try to get UserProfile for the current user
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if user_profile.role != 'Admin':
        return redirect('access_denied')

    # Fetch the raw material
    raw_material = get_object_or_404(RawMaterial, id=raw_material_id)

    logger = logging.getLogger(__name__)

    try:
        # Use quantile regression for initial aluminum output estimate
        ml_input_data = {
            'quantity': raw_material.quantity,
            'quality': raw_material.quality,
        }
        print(f"ML Input Data: {ml_input_data}")
        initial_estimate = predict_aluminum_output(ml_input_data)  # Ensure this function is defined
        print(f"Initial Estimate from ML: {initial_estimate}")
    except Exception as e:
        logger.error(f"Error in ML prediction: {e}")
        initial_estimate = 0  # Default to zero if ML fails

    try:
        # Adjust output using reinforcement learning simulation
        rl_adjusted_output = reinforcement_learning_simulation()  # Ensure this function is defined
        print(f"RL Adjusted Output: {rl_adjusted_output}")
    except Exception as e:
        logger.error(f"Error in RL simulation: {e}")
        rl_adjusted_output = 1  # Default multiplier if RL fails

    final_output_estimate = initial_estimate * rl_adjusted_output
    print(f"Final Output Estimate: {final_output_estimate}")

    # Wrap processing creation and by-product handling in a transaction
    try:
        with transaction.atomic():
            # Create or update processing instance
            processing, created = Processing.objects.update_or_create(
                raw_material=raw_material,
                defaults={
                    'aluminum_output_estimate': final_output_estimate,
                }
            )

            # Set the processing status explicitly based on the ML/RL outputs
            if initial_estimate == 0 or rl_adjusted_output == 1:
                processing.status = 'Failed'
            elif final_output_estimate < 5000:  # Example threshold for Pending
                processing.status = 'Pending'
            else:
                processing.status = 'Completed'

            # Calculate the by-products (ensure it's a list of dicts)
            by_products_data = calculate_byproducts(final_output_estimate)
            print(f"By-Products Data: {by_products_data}")

            # Ensure you are iterating over the list of dictionaries
            for by_product_data in by_products_data:
                ByProduct.objects.update_or_create(
                    processing=processing,
                    name=by_product_data['name'],
                    defaults={'quantity': by_product_data['quantity'],
                    # 'quality': by_product_data.get('quality', 'Medium')  # Provide a default fallback
                    }
                )

            # **Save the processing status after all updates**
            processing.save()  # This ensures all changes (status, by-products) are saved properly

    except Exception as e:
        logger.error(f"Error in processing or by-products: {e}")
        processing.status = 'Failed'  # Set status to 'Failed' on exception
        processing.save()  # Save the status here as well if something goes wrong

    by_products = ByProduct.objects.filter(processing=processing)

    # Render template with processing details
    return render(request, 'processing/start_processing.html', {
        'processing': processing,
        'initial_estimate': initial_estimate,
        'rl_adjusted_output': rl_adjusted_output,
        'final_output_estimate': final_output_estimate,
        'by_products': by_products,
    })


# Manage byproducts view
@login_required
def manage_byproducts(request, processing_id):
    # Fetch the processing instance
    processing = get_object_or_404(Processing, id=processing_id)
    by_products = ByProduct.objects.filter(processing=processing)

    # Message for empty by-products
    message = None if by_products.exists() else 'No by-products available for this processing.'

    return render(request, 'processing/manage_byproducts.html', {
        'by_products': by_products,
        'message': message,
        'processing_id': processing_id,
    })


# AJAX to update processing values
@login_required
def get_processing_data(request, processing_id):
    # Fetch the processing object or return a 404 error if it doesn't exist
    processing = get_object_or_404(Processing, id=processing_id)

    # Context data to pass to the template
    context = {
        'processing': processing,
        'status_percent': 50,  # Example value; adjust based on your logic
    }

    return render(request, 'processing/processing.html', context)

@login_required
def edit_raw_material(request, raw_material_id):
    raw_material = get_object_or_404(RawMaterial, id=raw_material_id)

    if request.method == 'POST':
        form = RawMaterialForm(request.POST, instance=raw_material)
        if form.is_valid():
            form.save()
            return redirect('edit_raw_material',raw_material_id=raw_material_id)  # Redirect to the list view or detail view
    else:
        form = RawMaterialForm(instance=raw_material)

    return render(request, 'processing/edit_raw_material.html', {'form': form, 'raw_material': raw_material})

@login_required
def edit_byproduct(request, byproduct_id):
    byproduct = get_object_or_404(ByProduct, id=byproduct_id)

    if request.method == 'POST':
        form = ByProductForm(request.POST, instance=byproduct)
        if form.is_valid():
            form.save()
            return redirect('manage_byproducts', processing_id=byproduct.processing_id)  # Redirect to manage by-products view
    else:
        form = ByProductForm(instance=byproduct)

    return render(request, 'processing/edit_byproduct.html', {'form': form, 'byproduct': byproduct})


@login_required
def delete_raw_material(request, raw_material_id):
    raw_material = get_object_or_404(RawMaterial, id=raw_material_id)
    raw_material.delete()
    return redirect('homepage')  # Redirect to homepage after deletion

@login_required
def delete_byproduct(request, byproduct_id):
    byproduct = get_object_or_404(ByProduct, id=byproduct_id)
    processing_id = byproduct.processing_id  # Assuming byproduct has a foreign key to processing.
    byproduct.delete()
    return redirect('manage_byproducts', processing_id=processing_id)

@login_required
def byproduct_details(request, byproduct_id):
    byproduct = get_object_or_404(ByProduct, id=byproduct_id)
    return render(request, 'processing/byproduct_details.html', {'byproduct': byproduct})

# Access Denied view
def access_denied(request):
    return render(request, 'processing/access_denied.html')


