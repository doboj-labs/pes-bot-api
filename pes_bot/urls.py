from django.conf.urls import url, include
from django.contrib import admin
from rest_framework import routers
from api import views

router = routers.DefaultRouter()
router.register(r'Tournament', views.TournamentViewSet)
router.register(r'Match', views.MatchViewSet)

urlpatterns = [

    url(r'^web/tables', views.table),
    url(r'^web/matches', views.show_all_matches),
    url(r'^web/', views.main_web),
    url(r'^admin/', admin.site.urls),
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^get-next-match$', views.get_next_match),
    url(r'^start-stop-match', views.start_stop_match),
    url(r'^increment-decrement-score', views.increment_decrement_score),
]
