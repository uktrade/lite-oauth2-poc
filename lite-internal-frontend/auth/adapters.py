from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def complete_login(self, request, app, token, response):
        request.session['jwt'] = response['id_token']
        return super().complete_login(request, app, token, response)
