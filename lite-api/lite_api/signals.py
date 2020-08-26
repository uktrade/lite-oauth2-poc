from allauth.exceptions import ImmediateHttpResponse

from django.shortcuts import redirect


import python_jwt as jwt, jwcrypto.jwk as jwk

key = jwk.JWK.generate(kty='RSA', size=2048)

#http://localhost:8000/allauth-accounts/auth0/login/?next=/helloworld/
def generate_jwt(user):
    payload = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
    }
    return jwt.generate_jwt(payload, key, 'PS256')



def redirect_with_jwt(request, sociallogin, **kwargs):
    jwt = generate_jwt(request.user)
    url = sociallogin.state['next'] + f'?jwt={jwt}'

    response = redirect(url)
    raise ImmediateHttpResponse(response)
