from django.shortcuts import render, redirect
from .models import User,Product,Wishlist,Cart
from django.core.mail import send_mail
from django.conf import settings
import random
import requests
from django.http import JsonResponse, HttpResponse
import stripe   
from django.views.decorators.csrf import csrf_exempt
import json 

stripe.api_key = settings.STRIPE_PRIVATE_KEY
YOUR_DOMAIN = 'http://localhost:8000'
# Create your views here.
def index(request):
    try:
        user=User.objects.get(email=request.session['email'])
        if user.usertype=='buyer':  
            return render(request,'index.html')
        else:
            return render(request,'seller-index.html')
    except:
        return render(request,'index.html') 

def contact(request):
    return render(request,'contact.html')

def category(request):
    products=Product.objects.all()
    return render(request,'category.html',{'products': products})

def men(request):
    products=Product.objects.filter(product_category='Men')
    return render(request,'category.html',{'products': products})

def women(request):
    products=Product.objects.filter(product_category='Women')
    return render(request,'category.html',{'products': products})

def kids(request):
    products=Product.objects.filter(product_category='Kids')
    return render(request,'category.html',{'products': products})

def accessories(request):
    products=Product.objects.filter(product_category='Accessories')
    return render(request,'category.html',{'products': products})

def login(request):
    if request.method=='POST':
        try:
            user=User.objects.get(email=request.POST['email'])
            if user.password==request.POST['password']:
                request.session['email']=user.email
                request.session['fname']=user.fname
                request.session['profile_picture']=user.profile_picture.url
                wishlists=Wishlist.objects.filter(user=user)
                request.session['wishlist_count']=len(wishlists)
                carts=Cart.objects.filter(user=user,payment_status=False)
                request.session['cart_count']=len(carts)
                if user.usertype=='buyer':
                    return render(request,'index.html')
                else:
                    return render(request,'seller-index.html')
            else:
                msg="Invalid password"
                return render(request,'login.html',{'msg': msg})
        except:
            msg="Email not registered"
            return render(request,'login.html',{'msg': msg})
    else:
        return render(request,'login.html')

def signup(request):
    if request.method=='POST':
        try:
            user=User.objects.get(email=request.POST['email'])
            msg="Email already registered"
            return render(request,'login.html',{'msg': msg})
        except:
            if request.POST['password']==request.POST['cpassword']:
                User.objects.create(
                    fname=request.POST['fname'],
                    lname=request.POST['lname'],
                    mobile=request.POST['mobile'],
                    email=request.POST['email'],
                    address=request.POST['address'],
                    password=request.POST['password'],
                    profile_picture=request.FILES['profile_picture'],
                    usertype=request.POST['usertype']
                )
                msg="User signup successfully"
                return render(request,'login.html',{'msg': msg})
            else:
                msg="Password and confirm password does not match"
                return render(request,'signup.html',{'msg': msg})       
    else:        
         return render(request,'signup.html')

def logout(request):
    try:
        del request.session['email']
        del request.session['fname']
        del request.session['profile_picture']
        msg="Logged out successfully"
        return render(request,'login.html',{'msg': msg})
    except:
        msg="Logged out successfully"
        return render(request,'login.html',{'msg': msg})
    
def profile(request):
    user=User.objects.get(email=request.session['email'])
    if request.method=='POST':
        user.fname=request.POST['fname']
        user.lname=request.POST['lname']
        user.address=request.POST['address']
        user.mobile=request.POST['mobile']
        try:
            user.profile_picture=request.FILES['profile_picture']
        except:
            pass
        user.save()
        request.session['profile_picture']=user.profile_picture.url
        msg="Profile updated successfully"
        if user.usertype=='buyer':
            return render(request,'profile.html',{'user': user,'msg': msg})
        else:
            return render(request,'seller-profile.html',{'user': user,'msg': msg})
    else:
        if user.usertype=='buyer':
            return render(request,'profile.html',{'user': user})
        else:
            return render(request,'seller-profile.html',{'user': user})   
def change_password(request):
    user=User.objects.get(email=request.session['email'])
    if request.method=='POST':
        
        if user.password==request.POST['old_password']:
            if request.POST['new_password']==request.POST['cnew_password']:
                if user.password!=request.POST['new_password']:
                    user.password=request.POST['new_password']
                    user.save()
                    del request.session['email']
                    del request.session['fname']
                    del request.session['profile_picture']
                    msg="Password changed successfully"
                    return render(request,'login.html',{'msg': msg})
                else:
                    msg="New password must be different from old password"
                    if user.usertype=='buyer':
                        return render(request,'change-password.html',{'msg': msg})
                    else:
                        return render(request,'seller-change-password.html',{'msg': msg})
            else:
                msg="New password and confirm new password does not match"
                if user.usertype=='buyer':
                    return render(request,'change-password.html',{'msg': msg})
                else:
                    return render(request,'seller-change-password.html',{'msg': msg})
        else:
            msg="Old password is incorrect"
            if user.usertype=='buyer':
                return render(request,'change-password.html',{'msg': msg})
            else:
                return render(request,'seller-change-password.html',{'msg': msg})
    else:
        if user.usertype=='buyer':
            return render(request,'change-password.html')
        else:
            return render(request,'seller-change-password.html')
    
def forgot_password(request):
    if request.method=='POST':
        
        try:
            user=User.objects.get(email=request.POST['email']) 
            otp=random.randint(1000,9999)
            context = {}
            address = request.POST['email']
            subject = "OTP for Forgot Password"
            message = "Your Otp For Forgot Password is: " + str(otp)

            if address and subject and message:
                try:
                    send_mail(subject, message, settings.EMAIL_HOST_USER, [address])
                    context['result'] = 'Email sent successfully'
                    request.session['email1']=request.POST['email']
                    request.session['otp']=otp
                    return render(request, "otp.html", context)
                except Exception as e:
                    context['result'] = f'Error sending email: {e}'
            else:
                context['result'] = 'All fields are required'
                return render(request, "otp.html", context)
        except:
            msg="Email not registered"
            return render(request,'forgot-password.html',{'msg': msg})
    else:
        return render(request,'forgot-password.html')

def verify_otp(request):
    if int(request.POST['otp'])==int(request.session['otp']):
        del request.session['otp']
        msg="OTP verified successfully. You can now change your password."
        return render(request,'new-password.html',{'msg': msg})
    else:
        msg="Invalid OTP. Please try again."
        return render(request,'otp.html',{'msg': msg})
    
def new_password(request):
    if request.POST['new_password']==request.POST['cnew_password']:
        user=User.objects.get(email=request.session['email1'])
        user.password=request.POST['new_password']
        user.save()
        del request.session['email1']
        msg="Password reset successfully"
        return render(request,'login.html',{'msg': msg})
    else:
        msg="New password and confirm new password does not match"
        return render(request,'new-password.html',{'msg': msg})

def add_product(request):
    seller=User.objects.get(email=request.session['email'])
    if request.method=='POST':
        from .models import Product
        Product.objects.create(
            seller=seller,
            product_category=request.POST['product_category'],
            product_name=request.POST['product_name'],
            product_price=request.POST['product_price'],
            product_desc=request.POST['product_desc'],
            product_image=request.FILES['product_image']
        )
        msg="Product added successfully"
        return render(request,'add-product.html',{'msg': msg})
    else:
        return render(request,'add-product.html')
    
def view_product(request):
    seller=User.objects.get(email=request.session['email'])
    products=Product.objects.filter(seller=seller)
    return render(request,'view-product.html',{'products': products})

def seller_product_details(request,pk):
    product=Product.objects.get(pk=pk)
    return render(request,'seller-product-details.html',{'product': product})   

def product_details(request,pk):
    wishlist_flag=False
    cart_flag=False
    user=User.objects.get(email=request.session['email'])
    product=Product.objects.get(pk=pk)
    try:
        Wishlist.objects.get(user=user,product=product)
        wishlist_flag=True
    except:
        pass
    try:
        Cart.objects.get(user=user,product=product,payment_status=False)
        cart_flag=True
    except:
        pass
    return render(request,'product-details.html',{'product': product,'wishlist_flag': wishlist_flag, 'cart_flag': cart_flag})    

def seller_product_edit(request,pk):
    product=Product.objects.get(pk=pk)
    if request.method=='POST':
        product.product_category=request.POST['product_category']
        product.product_name=request.POST['product_name']
        product.product_price=request.POST['product_price']
        product.product_desc=request.POST['product_desc']
        try:
            product.product_image=request.FILES['product_image']
        except:
            pass
        product.save()
        return redirect('view-product')
    else:
        return render(request,'seller-product-edit.html',{'product': product})  
    
def seller_product_delete(request,pk):
    product=Product.objects.get(pk=pk)
    product.delete()
    return redirect('view-product')

def add_to_wishlist(request,pk):
    user=User.objects.get(email=request.session['email'])
    product=Product.objects.get(pk=pk)
    Wishlist.objects.create(
        user=user,
        product=product
    )
    return redirect('wishlist')

def wishlist(request):
    user=User.objects.get(email=request.session['email'])
    wishlists=Wishlist.objects.filter(user=user)
    request.session['wishlist_count']=len(wishlists)
    return render(request,'wishlist.html',{'wishlists': wishlists})

def remove_from_wishlist(request,pk):
    user=User.objects.get(email=request.session['email'])
    product=Product.objects.get(pk=pk)
    wishlist=Wishlist.objects.get(user=user,product=product)
    wishlist.delete()
    return redirect('wishlist')

def add_to_cart(request,pk):
    user=User.objects.get(email=request.session['email'])
    product=Product.objects.get(pk=pk)
    Cart.objects.create(
        user=user,
        product=product,
        product_price=product.product_price,
        product_qty=1,
        total_price=product.product_price,
        payment_status=False
    )
    return redirect('cart')

def cart(request):
    net_price=0
    user=User.objects.get(email=request.session['email'])
    carts=Cart.objects.filter(user=user,payment_status=False)
    for i in carts:
        net_price=net_price+i.total_price
    request.session['cart_count']=len(carts)
    return render(request,'cart.html',{'carts': carts,'net_price': net_price})

def remove_from_cart(request,pk):
    user=User.objects.get(email=request.session['email'])
    product=Product.objects.get(pk=pk)
    cart=Cart.objects.get(user=user,product=product,payment_status=False)
    cart.delete()
    return redirect('cart')

def change_qty(request):
    cart=Cart.objects.get(pk=request.POST['cid'])
    product_qty=int(request.POST['product_qty'])
    cart.total_price=int(cart.product_price)*product_qty 
    cart.product_qty=product_qty
    cart.save()
    
    return redirect('cart')

@csrf_exempt
def create_checkout_session(request):
    data = json.loads(request.body)
    amount = int(data['post_data'])

    final_amount = amount * 100  
    user = User.objects.get(email=request.session['email'])

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'inr',
                'unit_amount': final_amount,
                'product_data': {
                    'name': 'Checkout Session Data',
                    'description': f'''
                    Customer: {user.fname} {user.lname}
                    Address: {user.address}
                    Mobile: {user.mobile}
                    ''',
                },
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=YOUR_DOMAIN + '/success/',
        cancel_url=YOUR_DOMAIN + '/cancel/',
        customer_email=user.email,
        shipping_address_collection={
            'allowed_countries': ['IN'],
        }
    )

    return JsonResponse({'id': session.id})


def success(request):
    user=User.objects.get(email=request.session['email'])
    carts=Cart.objects.filter(user=user,payment_status=False)
    for i in carts:
        i.payment_status=True
        i.save()
    carts=Cart.objects.filter(user=user,payment_status=False)
    request.session['cart_count']=len(carts) 
    return render(request,'success.html')

def cancel(request):
    return render(request,'cancel.html')

def myorder(request):
    user=User.objects.get(email=request.session['email'])
    carts=Cart.objects.filter(user=user,payment_status=True)
    return render(request,'myorder.html',{'carts': carts})