from rest_framework_simplejwt.tokens import RefreshToken

def get_tokens_for_user(user, device_id):
    refresh = RefreshToken.for_user(user)
    refresh['device_id'] = device_id
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
