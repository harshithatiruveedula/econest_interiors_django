from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseNotFound
from django.contrib import messages
from django.core.exceptions import ValidationError
from .models import Consultation, Service, GalleryImage, BlogPost
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)

def home(request):
    return render(request, 'main/index.html')

def about(request):
    return render(request, 'main/about.html')

def services(request):
    all_services = Service.objects.all()
    return render(request, 'main/services.html', {"services": all_services})

def contact(request):
    if request.method == "POST":
        # Check if it's an AJAX request
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        try:
            # Get form data
            name = request.POST.get('name', '').strip()
            email = request.POST.get('email', '').strip()
            phone = request.POST.get('phone', '').strip()
            service = request.POST.get('service', '').strip()
            appointment_date = request.POST.get('appointment_date', '').strip()
            
            # Validate required fields
            if not name:
                raise ValidationError("Name is required")
            if not email:
                raise ValidationError("Email is required")
            if not phone:
                raise ValidationError("Phone is required")
            if not service:
                raise ValidationError("Service is required")
            if not appointment_date:
                raise ValidationError("Appointment date is required")
            
            # Create consultation
            consultation = Consultation.objects.create(
                name=name,
                email=email,
                phone=phone,
                service=service,
                appointment_date=appointment_date,
            )
            
            # Return JSON response for AJAX requests
            if is_ajax:
                return JsonResponse({
                    "success": True,
                    "message": "Your consultation has been booked successfully!"
                })
            else:
                # Fallback for non-AJAX requests
                messages.success(request, 'Your consultation has been booked successfully!')
                return redirect('/contact/?success=1')
                
        except ValidationError as e:
            if is_ajax:
                return JsonResponse({
                    "success": False,
                    "message": str(e)
                }, status=400)
            else:
                messages.error(request, str(e))
        except Exception as e:
            # Log the error for debugging
            logger.error(f"Error creating consultation: {str(e)}")
            
            if is_ajax:
                return JsonResponse({
                    "success": False,
                    "message": f"An error occurred: {str(e)}"
                }, status=500)
            else:
                messages.error(request, 'An error occurred. Please try again.')
    
    return render(request, 'main/contact.html', {
        'success': request.GET.get('success')
    })


def gallery(request):
    photos = GalleryImage.objects.all()
    return render(request, 'main/gallery.html', {"photos": photos})

def blog_list(request):
    posts = BlogPost.objects.all().order_by('-created_at')
    return render(request, 'main/blog_list.html', {'posts': posts})

def blog_detail(request, id):
    post = BlogPost.objects.get(id=id)
    return render(request, 'main/blog_detail.html', {'post': post})

def dashboard(request):
    try:
        # Auto-run migrations if tables don't exist
        try:
            # Test if tables exist by trying a simple query
            Consultation.objects.exists()
        except Exception as e:
            error_str = str(e).lower()
            if "no such table" in error_str or "does not exist" in error_str or "relation" in error_str:
                logger.info("Tables not found. Running migrations automatically...")
                try:
                    from django.core.management import call_command
                    from django.db import connection, transaction
                    
                    # Close any existing connections
                    connection.close()
                    
                    # Run migrations
                    call_command('migrate', verbosity=0, interactive=False)
                    
                    # Commit transaction
                    transaction.commit()
                    
                    # Close connection to force reconnection
                    connection.close()
                    
                    logger.info("Migrations completed successfully.")
                    messages.success(request, "Database tables created automatically! Please refresh the page.")
                    
                    # Try to query again after migration
                    try:
                        Consultation.objects.exists()
                    except:
                        pass  # Will show empty data
                        
                except Exception as migrate_error:
                    logger.error(f"Auto-migration failed: {str(migrate_error)}")
                    import traceback
                    logger.error(traceback.format_exc())
                    messages.warning(request, "Could not auto-create tables. Please run migrations manually.")
        
        # Safely get counts with error handling
        try:
            total_bookings = Consultation.objects.count()
        except Exception as e:
            logger.error(f"Error counting consultations: {str(e)}")
            total_bookings = 0
        
        try:
            total_services = Service.objects.count()
        except Exception as e:
            logger.error(f"Error counting services: {str(e)}")
            total_services = 0
        
        try:
            total_images = GalleryImage.objects.count()
        except Exception as e:
            logger.error(f"Error counting gallery images: {str(e)}")
            total_images = 0
        
        try:
            total_posts = BlogPost.objects.count()
        except Exception as e:
            logger.error(f"Error counting blog posts: {str(e)}")
            total_posts = 0

        # Get search query
        search_query = request.GET.get('search', '').strip()
        
        # Get filter parameters
        filter_service = request.GET.get('service', '').strip()
        filter_date_from = request.GET.get('date_from', '').strip()
        filter_date_to = request.GET.get('date_to', '').strip()

        # Get all bookings with filters
        all_bookings_list = []
        try:
            all_bookings = Consultation.objects.all()
            
            # Apply search filter
            if search_query:
                all_bookings = all_bookings.filter(
                    Q(name__icontains=search_query) |
                    Q(email__icontains=search_query) |
                    Q(phone__icontains=search_query) |
                    Q(service__icontains=search_query)
                )
            
            # Apply service filter
            if filter_service:
                all_bookings = all_bookings.filter(service=filter_service)
            
            # Apply date filters
            if filter_date_from:
                all_bookings = all_bookings.filter(appointment_date__gte=filter_date_from)
            if filter_date_to:
                all_bookings = all_bookings.filter(appointment_date__lte=filter_date_to)
            
            # Order by submitted date (newest first)
            all_bookings = all_bookings.order_by('-submitted_at')
            all_bookings_list = list(all_bookings)
            
        except Exception as e:
            logger.error(f"Error fetching consultations: {str(e)}")
            all_bookings_list = []

        # Get unique services for filter dropdown
        try:
            unique_services = Consultation.objects.values_list('service', flat=True).distinct().order_by('service')
        except:
            unique_services = [
                'Interior design consultation',
                'Custom eco-friendly furniture',
                'Renovation with sustainable materials',
                'Green spaces and indoor plants'
            ]

        context = {
            "total_bookings": total_bookings,
            "total_services": total_services,
            "total_images": total_images,
            "total_posts": total_posts,
            "recent_bookings": all_bookings_list,
            "all_bookings": all_bookings_list,
            "search_query": search_query,
            "filter_service": filter_service,
            "filter_date_from": filter_date_from,
            "filter_date_to": filter_date_to,
            "unique_services": unique_services,
        }

        return render(request, 'main/dashboard.html', context)
    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        
        # Return empty context if error
        context = {
            "total_bookings": 0,
            "total_services": 0,
            "total_images": 0,
            "total_posts": 0,
            "recent_bookings": [],
            "all_bookings": [],
            "search_query": "",
            "filter_service": "",
            "filter_date_from": "",
            "filter_date_to": "",
            "unique_services": [],
        }
        return render(request, 'main/dashboard.html', context)

def create_consultation(request):
    """Create a new consultation"""
    if request.method == "POST":
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        try:
            name = request.POST.get('name', '').strip()
            email = request.POST.get('email', '').strip()
            phone = request.POST.get('phone', '').strip()
            service = request.POST.get('service', '').strip()
            appointment_date = request.POST.get('appointment_date', '').strip()
            
            if not name:
                raise ValidationError("Name is required")
            if not email:
                raise ValidationError("Email is required")
            if not phone:
                raise ValidationError("Phone is required")
            if not service:
                raise ValidationError("Service is required")
            if not appointment_date:
                raise ValidationError("Appointment date is required")
            
            consultation = Consultation.objects.create(
                name=name,
                email=email,
                phone=phone,
                service=service,
                appointment_date=appointment_date,
            )
            
            if is_ajax:
                return JsonResponse({
                    "success": True,
                    "message": "Consultation created successfully!"
                })
            else:
                messages.success(request, 'Consultation created successfully!')
                return redirect('dashboard')
        except ValidationError as e:
            if is_ajax:
                return JsonResponse({
                    "success": False,
                    "message": str(e)
                }, status=400)
            else:
                messages.error(request, str(e))
        except Exception as e:
            if is_ajax:
                return JsonResponse({
                    "success": False,
                    "message": f"Error: {str(e)}"
                }, status=500)
            else:
                messages.error(request, f'Error: {str(e)}')
    
    # Get unique services for dropdown
    try:
        unique_services = Consultation.objects.values_list('service', flat=True).distinct().order_by('service')
        if not unique_services:
            unique_services = [
                'Interior design consultation',
                'Custom eco-friendly furniture',
                'Renovation with sustainable materials',
                'Green spaces and indoor plants'
            ]
    except:
        unique_services = [
            'Interior design consultation',
            'Custom eco-friendly furniture',
            'Renovation with sustainable materials',
            'Green spaces and indoor plants'
        ]
    
    return render(request, 'main/create_consultation.html', {
        'unique_services': unique_services
    })

def edit_consultation(request, id):
    """Edit a consultation"""
    try:
        consultation = get_object_or_404(Consultation, id=id)
    except Consultation.DoesNotExist:
        return HttpResponseNotFound("Consultation not found")
    
    if request.method == "POST":
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        try:
            consultation.name = request.POST.get('name', '').strip()
            consultation.email = request.POST.get('email', '').strip()
            consultation.phone = request.POST.get('phone', '').strip()
            consultation.service = request.POST.get('service', '').strip()
            appointment_date = request.POST.get('appointment_date', '').strip()
            
            if appointment_date:
                consultation.appointment_date = appointment_date
            
            consultation.save()
            
            if is_ajax:
                return JsonResponse({
                    "success": True,
                    "message": "Consultation updated successfully!"
                })
            else:
                messages.success(request, 'Consultation updated successfully!')
                return redirect('dashboard')
        except Exception as e:
            if is_ajax:
                return JsonResponse({
                    "success": False,
                    "message": f"Error: {str(e)}"
                }, status=400)
            else:
                messages.error(request, f'Error: {str(e)}')
    
    return render(request, 'main/edit_consultation.html', {
        'consultation': consultation
    })

def delete_consultation(request, id):
    """Delete a consultation"""
    if request.method == "POST":
        try:
            consultation = get_object_or_404(Consultation, id=id)
            consultation.delete()
            
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            if is_ajax:
                return JsonResponse({
                    "success": True,
                    "message": "Consultation deleted successfully!"
                })
            else:
                messages.success(request, 'Consultation deleted successfully!')
                return redirect('dashboard')
        except Consultation.DoesNotExist:
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            if is_ajax:
                return JsonResponse({
                    "success": False,
                    "message": "Consultation not found"
                }, status=404)
            else:
                messages.error(request, 'Consultation not found')
                return redirect('dashboard')
        except Exception as e:
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            if is_ajax:
                return JsonResponse({
                    "success": False,
                    "message": f"Error: {str(e)}"
                }, status=500)
            else:
                messages.error(request, f'Error: {str(e)}')
                return redirect('dashboard')
    
    # If GET request, show confirmation page
    try:
        consultation = get_object_or_404(Consultation, id=id)
        return render(request, 'main/delete_consultation.html', {
            'consultation': consultation
        })
    except Consultation.DoesNotExist:
        return HttpResponseNotFound("Consultation not found")


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
