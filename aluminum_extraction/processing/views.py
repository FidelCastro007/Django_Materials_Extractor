from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.contrib.auth.decorators import login_required
from .models import RawMaterial, Processing, ByProduct, UserProfile
from ml_model.predict import predict_aluminum_output  # Quantile regression prediction
from ml_model.reinforcement_learning import reinforcement_learning_simulation  # RL logic
from django.contrib.auth.models import User
from django.contrib import messages
from .models import UserProfile

# Home page view
def homepage(request):
    raw_materials = RawMaterial.objects.all()
    if not raw_materials:
        raise Http404("No raw materials found.")
    return render(request, 'processing/homepage.html', {'raw_materials': raw_materials})

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password_confirm = request.POST['password_confirm']

        if password != password_confirm:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        # Create UserProfile for the new user
        UserProfile.objects.create(user=user, role='Operator')  # Default role, adjust if needed

        messages.success(request, "Account created successfully! Please login.")
        return redirect('login')

    return render(request, 'processing/register.html')

# Start processing view with both ML and RL integration
@login_required
def start_processing(request, raw_material_id):
    # Try to get UserProfile for the current user
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if user_profile.role != 'Operator':
        return redirect('access_denied')

    raw_material = get_object_or_404(RawMaterial, id=raw_material_id)

    # Use quantile regression for initial aluminum output estimate
    ml_input_data = {
        'quantity': raw_material.quantity,
        'quality': raw_material.quality,
    }
    initial_estimate = predict_aluminum_output(ml_input_data)

    # Adjust output using reinforcement learning simulation
    rl_adjusted_output = reinforcement_learning_simulation()

    # Combine ML estimate and RL adjustment
    final_output_estimate = initial_estimate * rl_adjusted_output

    # Create a processing instance
    processing = Processing.objects.create(
        raw_material=raw_material,
        aluminum_output_estimate=final_output_estimate,
        status='Pending'
    )
    return render(request, 'processing/start_processing.html', {
        'processing': processing,
        'initial_estimate': initial_estimate,
        'rl_adjusted_output': rl_adjusted_output,
        'final_output_estimate': final_output_estimate
    })

# Manage byproducts view
@login_required
def manage_byproducts(request, processing_id):
    processing = get_object_or_404(Processing, id=processing_id)
    by_products = ByProduct.objects.filter(processing=processing)
    return render(request, 'processing/manage_byproducts.html', {'by_products': by_products})

# Access Denied view
def access_denied(request):
    return render(request, 'processing/access_denied.html')


