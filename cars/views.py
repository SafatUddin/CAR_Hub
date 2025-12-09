from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from .models import Car, Notification, Order, CarImage
from .patterns.factory import SedanFactory, SUVFactory, TruckFactory, CoupeFactory
from .patterns.strategy import CarSearchContext, PriceSearchStrategy, BrandSearchStrategy, MileageSearchStrategy
from .patterns.decorator import BasicCar, WarrantyDecorator, InsuranceDecorator, PremiumListingDecorator
from .patterns.proxy import CarAccessProxy
from .patterns.observer import CarPriceSubject, UserObserver
from .patterns.singleton import DatabaseConfigManager
from .patterns.adapter import CurrencyAdapter
from .forms import SignUpForm, EditProfileForm

def welcome(request):
    # If user is already logged in, redirect to home
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'cars/welcome.html')

def custom_login(request):
    print("DEBUG: custom_login view called")
    if request.user.is_authenticated:
        print("DEBUG: User already authenticated, redirecting to home")
        return redirect('home')
        
    if request.method == 'POST':
        print("DEBUG: POST request received")
        from django.contrib.auth import authenticate, login as auth_login
        username_or_email = request.POST.get('username')
        password = request.POST.get('password')
        print(f"DEBUG: Attempting login for: {username_or_email}")
        
        # Try to authenticate with username first
        user = authenticate(request, username=username_or_email, password=password)
        
        # If authentication failed and input looks like an email, try to find user by email
        if user is None and '@' in username_or_email:
            print("DEBUG: Input looks like email, trying to find user by email")
            try:
                from django.contrib.auth.models import User
                user_obj = User.objects.get(email=username_or_email)
                # Now try to authenticate with the username
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                print("DEBUG: No user found with that email")
                user = None
        
        if user is not None:
            print("DEBUG: Authentication successful")
            auth_login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            print("DEBUG: Success message added")
            return redirect('home')
        else:
            print("DEBUG: Authentication failed")
            messages.error(request, "Invalid username/email or password. Please try again.")
            print("DEBUG: Error message added")
            return render(request, 'registration/login.html')
    
    print("DEBUG: Rendering login form (GET request)")
    return render(request, 'registration/login.html')

def custom_logout(request):
    from django.contrib.auth import logout as auth_logout
    auth_logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('welcome')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def buy_car(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    
    if car.status != 'available':
        messages.error(request, "This car is no longer available.")
        return redirect('car_detail', car_id=car.id)
        
    # Check if order already exists
    if Order.objects.filter(buyer=request.user, car=car, status='pending').exists():
        messages.warning(request, "You have already sent a buy request for this car.")
        return redirect('car_detail', car_id=car.id)
        
    # Create Order
    Order.objects.create(buyer=request.user, car=car)
    
    # Notify Owner
    Notification.objects.create(
        user=car.owner, 
        message=f"New Buy Request: {request.user.username} wants to buy your {car.year} {car.make} {car.model}."
    )
    
    messages.success(request, "Buy request sent! The seller has been notified.")
    return redirect('car_detail', car_id=car.id)

@login_required
def update_car_status(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    
    if request.user != car.owner:
        messages.error(request, "You are not authorized to perform this action.")
        return redirect('home')
        
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['available', 'sold']:
            car.status = new_status
            car.save()
            messages.success(request, f"Car status updated to {new_status}.")
            
    return redirect('car_detail', car_id=car.id)

@login_required
def accept_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    car = order.car
    
    if request.user != car.owner:
        messages.error(request, "You are not authorized to perform this action.")
        return redirect('profile')
        
    # 1. Mark this order as completed
    order.status = 'completed'
    order.save()
    
    # 2. Mark car as sold
    car.status = 'sold'
    car.save()
    
    # 3. Cancel other pending orders for this car
    other_orders = Order.objects.filter(car=car, status='pending').exclude(id=order.id)
    for other_order in other_orders:
        other_order.status = 'cancelled'
        other_order.save()
        # Notify rejected buyer
        Notification.objects.create(
            user=other_order.buyer,
            message=f"Your buy request for {car.year} {car.make} {car.model} was cancelled because the car was sold to another buyer."
        )
        
    # 4. Notify accepted buyer
    Notification.objects.create(
        user=order.buyer,
        message=f"Congratulations! Your buy request for {car.year} {car.make} {car.model} has been accepted!"
    )
    
    messages.success(request, f"Order accepted! Car marked as sold and other requests cancelled.")
    return redirect('profile')

@login_required
def home(request):
    # Singleton usage (just for demo)
    db_config = DatabaseConfigManager().get_config()
    
    cars = Car.objects.all()
    
    # Strategy Pattern
    search_type = request.GET.get('search_type')
    query = request.GET.get('query')
    
    from .patterns.strategy import ModelSearchStrategy
    
    if search_type:
        context = None
        if search_type == 'price':
            min_price = request.GET.get('min_price')
            max_price = request.GET.get('max_price')
            if min_price and max_price:
                try:
                    # Get current currency
                    currency = request.GET.get('currency', request.session.get('currency', 'BDT'))
                    
                    # Convert input prices (in selected currency) to BDT
                    min_price_bdt = CurrencyAdapter.convert_to_bdt_static(float(min_price), currency)
                    max_price_bdt = CurrencyAdapter.convert_to_bdt_static(float(max_price), currency)
                    
                    context = CarSearchContext(PriceSearchStrategy())
                    cars = context.execute_search([min_price_bdt, max_price_bdt])
                except ValueError:
                    pass
        elif search_type == 'brand':
            query = request.GET.get('query')
            if query:
                context = CarSearchContext(BrandSearchStrategy())
                cars = context.execute_search(query)
        elif search_type == 'model':
            query = request.GET.get('query')
            if query:
                context = CarSearchContext(ModelSearchStrategy())
                cars = context.execute_search(query)
        elif search_type == 'mileage':
            min_mileage = request.GET.get('min_mileage')
            max_mileage = request.GET.get('max_mileage')
            if min_mileage and max_mileage:
                try:
                    context = CarSearchContext(MileageSearchStrategy())
                    cars = context.execute_search([int(min_mileage), int(max_mileage)])
                except ValueError:
                    pass
    
    # Currency Handling
    currency = request.GET.get('currency', request.session.get('currency', 'BDT'))
    request.session['currency'] = currency
    
    # Adapt prices for display
    for car in cars:
        adapter = CurrencyAdapter()
        car.display_price = adapter.convert_from_bdt(car.price, currency)
        car.currency_symbol = CurrencyAdapter.get_symbol(currency)
            
    return render(request, 'cars/home.html', {'cars': cars, 'current_currency': currency})

def car_detail(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    
    # Decorator Pattern
    car_component = BasicCar(car)
    
    if request.GET.get('warranty'):
        car_component = WarrantyDecorator(car_component)
    if request.GET.get('insurance'):
        car_component = InsuranceDecorator(car_component)
    if request.GET.get('premium'):
        car_component = PremiumListingDecorator(car_component)
        
    final_price_bdt = car_component.get_price()
    description = car_component.get_description()
    
    # Currency Handling
    currency = request.GET.get('currency', request.session.get('currency', 'BDT'))
    request.session['currency'] = currency
    
    adapter = CurrencyAdapter()
    display_price = adapter.convert_from_bdt(final_price_bdt, currency)
    currency_symbol = CurrencyAdapter.get_symbol(currency)
    
    # Calculate add-on prices in selected currency
    adapter = CurrencyAdapter()
    warranty_price = adapter.convert_from_bdt(50000, currency)
    insurance_price = adapter.convert_from_bdt(100000, currency)
    premium_price = adapter.convert_from_bdt(15000, currency)
    
    return render(request, 'cars/detail.html', {
        'car': car,
        'final_price': display_price,
        'currency_symbol': currency_symbol,
        'current_currency': currency,
        'description': description,
        'warranty_price': warranty_price,
        'insurance_price': insurance_price,
        'premium_price': premium_price,
    })

@login_required
def create_car(request):
    # Proxy Pattern check
    proxy = CarAccessProxy(request.user)
    allowed, msg = proxy.post_car({})
    if not allowed:
        messages.error(request, msg)
        return redirect('home')

    if request.method == 'POST':
        make = request.POST.get('make')
        model = request.POST.get('model')
        year = request.POST.get('year')
        price_input = float(request.POST.get('price'))
        currency_input = request.POST.get('currency', 'BDT')
        mileage = request.POST.get('mileage')
        car_type = request.POST.get('car_type')
        contact_email = request.POST.get('contact_email')
        contact_whatsapp = request.POST.get('contact_whatsapp')
        images = request.FILES.getlist('images')
        
        # Validate Contact Info
        if not contact_email and not contact_whatsapp:
            messages.error(request, "You must provide at least one contact method (Email or WhatsApp).")
            return render(request, 'cars/create.html')
        
        # Convert to BDT
        price_bdt = CurrencyAdapter.convert_to_bdt_static(price_input, currency_input)
        
        if len(images) < 1:
            messages.error(request, "You must upload at least 1 image.")
            return render(request, 'cars/create.html')
        
        if len(images) > 5:
            messages.error(request, "You can upload a maximum of 5 images.")
            return render(request, 'cars/create.html')
        
        # Factory Pattern
        factory = None
        if car_type == 'sedan':
            factory = SedanFactory()
        elif car_type == 'suv':
            factory = SUVFactory()
        elif car_type == 'truck':
            factory = TruckFactory()
        elif car_type == 'coupe':
            factory = CoupeFactory()
            
        if factory:
            car = factory.create_car(make, model, year, price_bdt, mileage, request.user)
            
            # Save contact info
            car.contact_email = contact_email
            car.contact_whatsapp = contact_whatsapp
            car.save()
            
            # Save images
            for image in images:
                CarImage.objects.create(car=car, image=image)
                
            messages.success(request, "Car listed successfully!")
            return redirect('home')
            
    import datetime
    current_year = datetime.date.today().year
    year_range = range(current_year, 1939, -1)
    
    # Get user's contact info from profile
    user_email = request.user.email
    user_whatsapp = ''
    if hasattr(request.user, 'profile'):
        user_whatsapp = request.user.profile.whatsapp_number or ''
    
    return render(request, 'cars/create.html', {
        'year_range': year_range,
        'user_email': user_email,
        'user_whatsapp': user_whatsapp
    })

@login_required
def delete_car(request, car_id):
    # Proxy Pattern
    proxy = CarAccessProxy(request.user)
    success, msg = proxy.delete_car(car_id)
    
    if success:
        messages.success(request, msg)
    else:
        messages.error(request, msg)
        
    return redirect('home')

@login_required
def update_car(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    
    if request.user != car.owner:
        messages.error(request, "You are not authorized to edit this car.")
        return redirect('car_detail', car_id=car.id)
    
    if request.method == 'POST':
        # Get fields
        make = request.POST.get('make')
        model = request.POST.get('model')
        year = request.POST.get('year')
        price_input = float(request.POST.get('price'))
        currency_input = request.POST.get('currency', 'BDT')
        mileage = request.POST.get('mileage')
        car_type = request.POST.get('car_type')
        contact_email = request.POST.get('contact_email')
        contact_whatsapp = request.POST.get('contact_whatsapp')
        images = request.FILES.getlist('images')
        
        # Validate Contact Info
        if not contact_email and not contact_whatsapp:
            messages.error(request, "You must provide at least one contact method (Email or WhatsApp).")
            import datetime
            current_year = datetime.date.today().year
            year_range = range(current_year, 1939, -1)
            return render(request, 'cars/update.html', {'car': car, 'year_range': year_range})
            
        # Convert to BDT
        new_price_bdt = CurrencyAdapter.convert_to_bdt_static(price_input, currency_input)
        
        # Check if price changed for notification
        old_price = float(car.price)
        price_changed = abs(old_price - new_price_bdt) > 1.0 # Float comparison
        
        # Update fields
        car.make = make
        car.model = model
        car.year = year
        car.price = new_price_bdt
        car.mileage = mileage
        car.car_type = car_type
        car.contact_email = contact_email
        car.contact_whatsapp = contact_whatsapp
        car.save()
        
        # Add new images
        for image in images:
            CarImage.objects.create(car=car, image=image)
            
        # Notify followers if price changed
        if price_changed:
            subject = CarPriceSubject()
            # In a real app, we'd only notify actual followers, which we do in observer.py
            # The previous code attached all users, which was for demo. 
            # Now we use the followers relationship in the model.
            subject.change_price(car, new_price_bdt)
            
        messages.success(request, "Car details updated successfully!")
        return redirect('car_detail', car_id=car.id)
        
    import datetime
    current_year = datetime.date.today().year
    year_range = range(current_year, 1939, -1)
    return render(request, 'cars/update.html', {'car': car, 'year_range': year_range})

@login_required
def profile(request):
    my_cars = Car.objects.filter(owner=request.user).order_by('-created_at')
    
    # Get incoming buy requests for user's cars
    buy_requests = Order.objects.filter(car__owner=request.user).order_by('-created_at')
    
    return render(request, 'cars/profile.html', {'my_cars': my_cars, 'buy_requests': buy_requests})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save()
            
            # Handle Password Change
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            if new_password:
                if new_password == confirm_password:
                    user.set_password(new_password)
                    user.save()
                    login(request, user)
                    messages.success(request, "Profile and password updated successfully!")
                else:
                    messages.error(request, "Passwords do not match.")
                    return render(request, 'cars/edit_profile.html', {'form': form})
            else:
                messages.success(request, "Profile updated successfully!")
                
            return redirect('profile')
    else:
        form = EditProfileForm(instance=request.user)
        
    return render(request, 'cars/edit_profile.html', {'form': form})

@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, "Your account has been deleted successfully.")
        return redirect('home')
    return redirect('profile')

def notifications(request):
    if not request.user.is_authenticated:
        return redirect('login')
    notifs = Notification.objects.filter(user=request.user).order_by('-created_at')
    unread_count = notifs.filter(is_read=False).count()
    return render(request, 'cars/notifications.html', {
        'notifications': notifs,
        'unread_count': unread_count
    })

@login_required
def mark_all_read(request):
    if request.method == 'POST':
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        messages.success(request, "All notifications marked as read.")
    return redirect('notifications')

@login_required
def follow_car(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    if request.user in car.followers.all():
        car.followers.remove(request.user)
        messages.success(request, f"You have unfollowed this {car.make} {car.model}.")
    else:
        car.followers.add(request.user)
        messages.success(request, f"You are now following this {car.make} {car.model}. You will be notified of updates.")
    return redirect('car_detail', car_id=car.id)
