from authservice import views
from django.conf.urls import url


urlpatterns = [
    url(r'^register$', views.RegisterView.as_view()),
    url(r'^login$', views.LoginView.as_view()),
    url(r'^loginuuid$', views.LoginWithUUIDView.as_view()),
    url(r'^logout$', views.LogoutView.as_view()),
    url(r'^check$', views.CheckView.as_view()),
    url(r'^checkzero$', views.CheckZeroView.as_view()),
    url(r'^check/(?P<actiontype>(prescription|fulfil))$', views.CheckView.as_view()),
    url(r'^getsecret$', views.GetSecretView.as_view()),
    url(r'^forgotpw$', views.ForgotPasswordView.as_view()),
    url(r'^resetpw$', views.ResetPasswordView.as_view()),
    url(r'^resetpw/validate$', views.ResetPasswordValidateView.as_view()),
    url(r'^changepassword$', views.ChangePasswordView.as_view()),
]
