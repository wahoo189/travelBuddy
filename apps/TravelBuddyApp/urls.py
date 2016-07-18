from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.main)
    , url(r'^register$', views.register)
    , url(r'^login$', views.login)
    , url(r'^logout$', views.logout)
    , url(r'^travels$', views.travels)
    , url(r'^listUsers$', views.listUsers)
    , url(r'^add$', views.add)
    , url(r'^addTravel$', views.addTravel)
    , url(r'^join/(?P<id>\d+)$', views.join)
    , url(r'^tripDetail/(?P<id>\d+)$', views.tripDetail)
]
