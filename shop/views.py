from django.shortcuts import render,redirect
from . models import *
from django.contrib import messages
from shop.form import Customuserform
from django.contrib.auth import authenticate,login,logout
import json
from django.http import JsonResponse


# Create your views here.
def home (request):
    products = Product.objects.filter(trending=1)
    return render(request,"shop/index.html",{"products":products})


def login_page(request):
  if request.user.is_authenticated:
    return redirect("/")
  else:
    if request.method=='POST':
      name=request.POST.get('username')
      pwd=request.POST.get('password')
      user=authenticate(request,username=name,password=pwd)
      if user is not None:
        login(request,user)
        messages.success(request,"Logged in Successfully")
        return redirect("/")
      else:
        messages.error(request,"Invalid User Name or Password")
        return redirect("/login")
    return render(request,"shop/login.html")
  
  
def logout_page(request):
   if request.user.is_authenticated:
      logout(request)
      messages.error(request,"Logged out successfully")
      return redirect("/")

def regester (request):
    form=Customuserform()
    if request.method == 'POST':
       form=Customuserform(request.POST)
       if form.is_valid():
          form.save()
          messages.success(request,"Registration Success You Can Login Now...!")
          return redirect('/login')
    return render(request,"shop/regester.html",{'form':form})

def collections (request):
    category = Category.objects.filter(status=0)
    return render(request,"shop/collections.html",{"category":category})

def collectionsview (request,name):
   if(Category.objects.filter(name=name,status=0)):
       products=Product.objects.filter(category__name=name)
       return render(request,"shop/products/index.html",{"products":products,"category_name":name})
   else:
       messages.warning(request,"NO SUCH CATEGORY FOUND")
       return redirect('collections')
       


def product_details(request,cname,pname):
    if(Category.objects.filter(name=cname,status=0)):
      if(Product.objects.filter(name=pname,status=0)):
        products=Product.objects.filter(name=pname,status=0).first()
        return render(request,"shop/products/product_details.html",{"products":products})
      else:
        messages.error(request,"No Such Produtct Found")
        return redirect('collections')
    else:
      messages.error(request,"No Such Catagory Found")
      return redirect('collections')
    

def add_to_cart (request):
   if request.headers.get('x-requested-with') == 'XMLHttpRequest':
      if request.user.is_authenticated:
         data=json.load(request)
         product_qty=data['product_qty']
         product_id=data['pid']
         #print(request.user.id)
         product_status=Product.objects.get(id=product_id)
         if product_status:
            if cart.objects.filter(user=request.user.id,product_id=product_id):
               return JsonResponse({'status' : 'product already in cart '})
            else:
               if product_status.quantity>=product_qty:
                  cart.objects.create(user=request.user,product_id=product_id,product_qty=product_qty)
                  return JsonResponse({'status' : 'product add to cart '})
               else:
                  return JsonResponse({'status' : 'product stock not available '})
                  
      else:
         return JsonResponse({'status':'Login to add cart'},status=200)
   else:
      return JsonResponse({'status' : 'Invalid Access '},status=200)
   

def cart_page (request):
   if request.user.is_authenticated:
      carts=cart.objects.filter(user=request.user)
      return render(request,"shop/carts.html",{"carts":carts})
   else:
      return redirect("/")
   

def remove_cart(request,cid):
   cartitem=cart.objects.get(id=cid)
   cartitem.delete()
   return redirect("/cart")


def fav_page(request):
   if request.headers.get('x-requested-with')=='XMLHttpRequest':
    if request.user.is_authenticated:
      data=json.load(request)
      product_id=data['pid']
      product_status=Product.objects.get(id=product_id)
      if product_status:
         if Favourite.objects.filter(user=request.user.id,product_id=product_id):
          return JsonResponse({'status':'Product Already in Favourite'}, status=200)
         else:
          Favourite.objects.create(user=request.user,product_id=product_id)
          return JsonResponse({'status':'Product Added to Favourite'}, status=200)
    else:
      return JsonResponse({'status':'Login to Add Favourite'}, status=200)
   else:
    return JsonResponse({'status':'Invalid Access'}, status=200)
  

def favviwepage (request):
     if request.user.is_authenticated:
      fav=Favourite.objects.filter(user=request.user)
      return render(request,"shop/fav.html",{"fav":fav})
     else:
       return redirect("/")
   

def remove_fav(request,fid):
  item=Favourite.objects.get(id=fid)
  item.delete()
  return redirect("/favviwepage")