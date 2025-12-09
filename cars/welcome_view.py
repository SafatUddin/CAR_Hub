def welcome(request):
    # If user is already logged in, redirect to home
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'cars/welcome.html')
