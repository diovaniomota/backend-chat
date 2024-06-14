from accounts.models import User
from django.contrib.auth.hashers import check_password, make_password
from typing import Union

class Authentication:
    def signin(self, email: str, password: str) -> Union[User, bool]:
        try:
            user = User.objects.get(email=email)
            if check_password(password, user.password):
                return user
        except User.DoesNotExist:
            return False

        return False
    
    def signup(self, name: str, email: str, password: str) -> Union[User, bool]:
        if User.objects.filter(email=email).exists():
            return False
        
        user = User.objects.create(
            name=name,
            email=email,
            password=make_password(password)
        )

        return user
