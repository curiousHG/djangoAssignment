from django.shortcuts import render

# Create your views here.
def GoogleCalendarInitView(request):
    return render(request, 'Hello World!')

def GoogleCalendarRedirectView(request):
    return render(request, 'Hello World!')