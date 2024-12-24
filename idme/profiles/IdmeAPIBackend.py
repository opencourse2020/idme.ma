from allauth.account.auth_backends import AuthenticationBackend


class MyAuthenticationBackend(AuthenticationBackend):
    def authenticate(self, request, **credentials):
        user = super().authenticate(request, **credentials)
        if user is not None:
            if user.mfa_enabled and user.mfa_checked:
                return user
            elif not user.mfa_enabled:
                return user
            else:
                return None
        else:
            return None