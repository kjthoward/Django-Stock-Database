from django.urls import re_path
from . import views

app_name = 'stock_web'

urlpatterns = [
    re_path(r'^recipes/$', views.recipes, name='recipes'),
    re_path(r'^prime/$', views.prime, name='prime'),
    re_path(r'^newinv/(.*)/$', views.newinv, name='newinv'),
    re_path(r'^search/$', views.search, name='search'),
    re_path(r'^valdates/$', views.valdates, name='valdates'),
    re_path(r'^createnewsol/(.*)$', views.createnewsol, name='createnewsol'),
    re_path(r'^newsup/$', views.newsup, name='newsup'),
    re_path(r'^newrecipe/$', views.newrecipe, name='newrecipe'),
    re_path(r'^newreagent/$', views.newreagent, name='newreagent'),
    re_path(r'^inventory/(.*)/(.*)/(.*)/(.*)/$', views.inventory, name='inventory'),
    re_path(r'^listinv/$', views.listinv, name='listinv'),
    re_path(r'^item/(.*)/$', views.item, name='item'),
    re_path(r'^recipe/(.*)/$', views.recipe, name='recipe'),
    re_path(r'^openitem/(.*)/$', views.openitem, name='openitem'),
    re_path(r'^useitem/(.*)/$', views.useitem, name='useitem'),
    re_path(r'^valitem/(.*)/$', views.valitem, name='valitem'),
    re_path(r'^finishitem/(.*)/$', views.finishitem, name='finishitem'),
    re_path(r"^loginview/$", views.loginview, name="loginview"),
    re_path(r"^change_password/$", views.change_password, name="change_password"),
    re_path(r"^activsup/$", views.activsup, name="activsup"),
    re_path(r"^activreag/$", views.activreag, name="activreag"),
    re_path(r"^changedef/(.*)/$", views.changedef, name="changedef"),
    re_path(r"^changemin/(.*)/$", views.changemin, name="changemin"),
    re_path(r"^removesup/$", views.removesup, name="removesup"),
    re_path(r"^editinv/(.*)/$", views.editinv, name="editinv"),
    re_path(r"^stockreport/(.*)/(.*)/$", views.stockreport, name="stockreport"),
    re_path(r"^invreport/(.*)/(.*)/$", views.invreport, name="invreport"),
    re_path(r"^undoitem/(.*)/(.*)/$", views.undoitem, name="undoitem"),
    re_path(r"^resetpw/$", views.resetpw, name="resetpw"),
    re_path(r"^forcereset/$", views.forcereset, name="forcereset"),
    re_path(r"^unauth/$", views.unauth, name="unauth"),
]
