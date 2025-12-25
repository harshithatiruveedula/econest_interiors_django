from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from .models import Consultation

def home(request):
    return render(request, 'main/index.html')

def about(request):
    return render(request, 'main/about.html')

def services(request):
    from .models import Service
    all_services = Service.objects.all()
    return render(request, 'main/services.html', {"services": all_services})


from django.shortcuts import render
from django.http import JsonResponse
from .models import Consultation

def contact(request):
    if request.method == "POST":
        # Check if it's an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                consultation = Consultation.objects.create(
                    name=request.POST.get("name"),
                    email=request.POST.get("email"),
                    phone=request.POST.get("phone"),
                    service=request.POST.get("service"),
                    appointment_date=request.POST.get("appointment_date"),
                )
                return JsonResponse({
                    "success": True,
                    "message": "Your consultation has booked successfully (demo only)"
                })
            except Exception as e:
                return JsonResponse({
                    "success": False,
                    "message": f"Error: {str(e)}"
                }, status=400)
        else:
            # Regular form submission (fallback)
            Consultation.objects.create(
                name=request.POST.get("name"),
                email=request.POST.get("email"),
                phone=request.POST.get("phone"),
                service=request.POST.get("service"),
                appointment_date=request.POST.get("appointment_date"),
            )
            return render(request, "main/contact.html", {"success": True})

    return render(request, "main/contact.html")



from .models import GalleryImage

def gallery(request):
    photos = GalleryImage.objects.all()
    return render(request, 'main/gallery.html', {"photos": photos})
from .models import BlogPost

def blog_list(request):
    posts = BlogPost.objects.all().order_by('-created_at')
    return render(request, 'main/blog_list.html', {'posts': posts})


def blog_detail(request, id):
    post = BlogPost.objects.get(id=id)
    return render(request, 'main/blog_detail.html', {'post': post})
from .models import Consultation, Service, GalleryImage, BlogPost

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Consultation

@login_required(login_url='/admin/login/')
def dashboard(request):
    consultations = Consultation.objects.all().order_by('-created_at')
    return render(request, 'main/dashboard.html', {
        'consultations': consultations
    })


@staff_member_required
def dashboard(request):
    total_bookings = Consultation.objects.count()
    total_services = Service.objects.count()
    total_images = GalleryImage.objects.count()
    total_posts = BlogPost.objects.count()

    recent_bookings = Consultation.objects.order_by('-submitted_at')[:5]

    context = {
        "total_bookings": total_bookings,
        "total_services": total_services,
        "total_images": total_images,
        "total_posts": total_posts,
        "recent_bookings": recent_bookings,
    }

    return render(request, 'main/dashboard.html', context)


def chat_ai(request):
    """AI Chat endpoint to handle interior design queries"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    import json
    import re
    
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').lower().strip()
        
        if not user_message:
            return JsonResponse({'error': 'Message is required'}, status=400)
        
        # AI Response Logic
        response = generate_ai_response(user_message)
        
        return JsonResponse({
            'response': response,
            'success': True
        })
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'success': False
        }, status=500)


def generate_ai_response(user_message):
    """Generate AI response based on user query"""
    # Keywords for different query types
    eco_materials_keywords = ['material', 'eco', 'sustainable', 'green', 'environment', 'recycled', 'bamboo', 'cork', 'wood', 'furniture']
    services_keywords = ['service', 'what do you', 'offer', 'provide', 'help', 'can you', 'do you']
    booking_keywords = ['book', 'consultation', 'appointment', 'schedule', 'meeting', 'available']
    design_keywords = ['design', 'interior', 'decor', 'style', 'color', 'room', 'space', 'layout', 'furniture', 'arrangement']
    greeting_keywords = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening']
    
    # Check for greetings
    if any(keyword in user_message for keyword in greeting_keywords):
        return "Hello! I'm your virtual design assistant at EcoNest Interiors. I can help you with interior design queries, suggest eco-friendly materials, explain our services, and guide you to book a consultation. How can I assist you today?"
    
    # Check for eco-friendly materials queries
    if any(keyword in user_message for keyword in eco_materials_keywords):
        return """Great question! Here are some excellent eco-friendly materials we recommend:

🌿 **Sustainable Flooring:**
- Bamboo (fast-growing, renewable)
- Cork (harvested without harming trees)
- Reclaimed wood (recycled from old structures)
- Linoleum (made from natural materials)

🪑 **Eco-Friendly Furniture:**
- FSC-certified wood (sustainably sourced)
- Recycled metal furniture
- Furniture made from reclaimed materials
- Natural fiber upholstery (organic cotton, hemp, jute)

🎨 **Sustainable Paints & Finishes:**
- Low-VOC or zero-VOC paints
- Natural clay paints
- Milk paint (non-toxic, biodegradable)

Would you like more details about any specific material, or would you like to book a consultation to discuss your project?"""
    
    # Check for services queries
    if any(keyword in user_message for keyword in services_keywords):
        return """We offer comprehensive eco-friendly interior design services:

✨ **Interior Design Consultation**
Personalized sessions to align your home with sustainable living principles.

🪑 **Custom Eco-Friendly Furniture**
Handcrafted pieces using sustainable materials and finishes, tailored to your space.

🏠 **Renovation with Sustainable Materials**
Upgrade your home with eco-friendly flooring, paints, and fixtures.

🌱 **Green Spaces & Indoor Plants**
Enhancing interiors with biophilic designs and indoor gardens for better air quality.

Would you like to learn more about any specific service, or book a consultation?"""
    
    # Check for booking queries
    if any(keyword in user_message for keyword in booking_keywords):
        return """I'd be happy to help you book a consultation! 

To schedule your appointment, please:
1. Visit our "Book Consultation" page (click the link in the navigation or chat)
2. Fill out the form with your details
3. Select your preferred service and date

You can also call us at +91 6301739482 or email harshithatiruveedula@gmail.com

Would you like me to guide you through the booking process?"""
    
    # Check for design queries
    if any(keyword in user_message for keyword in design_keywords):
        return """I'd love to help with your interior design questions! 

Here are some sustainable design tips:
- **Maximize Natural Light**: Reduces energy consumption and creates a welcoming atmosphere
- **Choose Sustainable Materials**: Opt for bamboo, cork, reclaimed wood, and natural fibers
- **Incorporate Plants**: Indoor plants improve air quality and add natural beauty
- **Energy-Efficient Lighting**: Use LED bulbs and maximize daylight
- **Multi-functional Furniture**: Reduces waste and maximizes space efficiency

For personalized design advice tailored to your specific space and needs, I recommend booking a consultation with our design experts. Would you like to schedule one?"""
    
    # Default response
    return """I'm here to help you with:
- Interior design advice and tips
- Eco-friendly material suggestions
- Information about our services
- Booking consultations

Could you please rephrase your question? Or feel free to ask about:
- "What eco-friendly materials do you recommend?"
- "What services do you offer?"
- "How can I book a consultation?"
- "Design tips for my home"

I'm here to assist you! 😊"""

from django.contrib.auth.models import User
from django.http import HttpResponse

def create_admin(request):
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='Admin@123'
        )
        return HttpResponse("Admin created")
    return HttpResponse("Admin already exists")
