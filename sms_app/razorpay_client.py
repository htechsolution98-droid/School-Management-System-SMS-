from django.conf import settings
import razorpay  
import random

 
client = razorpay.Client(auth=(settings.RAZOR_PAY_KEY_ID,settings.RAZOR_PAY_SECRET_KEY))