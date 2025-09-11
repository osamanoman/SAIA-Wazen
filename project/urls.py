from django.urls import include, path

from project import views


urlpatterns = [
    path("ai-assistant/", include("django_ai_assistant.urls")),
    path("", views.HomeView.as_view(), name="home"),
    path("chat/", views.AIAssistantChatHomeView.as_view(), name="chat_home"),
    path("thread/<int:thread_id>/",views.AIAssistantChatThreadView.as_view(),name="chat_thread",),


]