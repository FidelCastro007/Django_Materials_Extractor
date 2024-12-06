from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.contrib.auth.decorators import login_required
from .models import RawMaterial, Processing, ByProduct, UserProfile
from ml_model.predict import predict_aluminum_output  # Quantile regression prediction
from ml_model.reinforcement_learning import reinforcement_learning_simulation  # RL logic
from django.contrib.auth.models import User
# from django.contrib import messages
from .models import UserProfile
from django.db import IntegrityError
import logging
# Start processing view with both ML and RL integration
from django.db import transaction

# Home page view
def homepage(request):
    raw_materials = RawMaterial.objects.all()
    if not raw_materials:
        raise Http404("No raw materials found.")
    return render(request, 'processing/homepage.html', {'raw_materials': raw_materials})

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

def calculate_byproducts(processing_record):
    by_products = []
    if processing_record.raw_material.name == "Bauxite Ore":
        by_products = [
            {"name": "Iron Residue", "quantity": 50.0},
            {"name": "Silica Residue", "quantity": 20.0}
        ]
    elif processing_record.raw_material.name == "Aluminum Ore":
        by_products = [
            {"name": "Aluminum Slag", "quantity": 10.0}
        ]
    return by_products

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
    except Exception as e:
        logger.error(f"Error in ML prediction: {e}")
        initial_estimate = 0  # Default to zero if ML fails

    try:
        # Adjust output using reinforcement learning simulation
        rl_adjusted_output = reinforcement_learning_simulation()  # Ensure this function is defined
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
                    'status': 'Completed',  # Default to Completed for now
                }
            )

            # Handle by-products (create or update logic)
            by_products_data = calculate_byproducts(final_output_estimate)  # Function to calculate by-products
            for by_product_data in by_products_data:
                ByProduct.objects.update_or_create(
                    processing=processing,
                    name=by_product_data['name'],
                    defaults={'quantity': by_product_data['quantity']}
                )
    except Exception as e:
        logger.error(f"Error in processing or by-products: {e}")
        processing.status = 'Failed'
        processing.save()

    by_products = ByProduct.objects.filter(processing=processing)

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


# Access Denied view
def access_denied(request):
    return render(request, 'processing/access_denied.html')


