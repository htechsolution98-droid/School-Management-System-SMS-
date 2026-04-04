from rest_framework_simplejwt.authentication import JWTAuthentication

class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        access_token = request.COOKIEES.get('access_token')
        
        if not access_token:
            return None
        
        validate_token = self.get_validated_token(access_token)
        user = self.get_user(validate_token)
        
        return (user,validate_token)