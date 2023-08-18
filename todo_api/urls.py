from django.urls import path, include

from .views import TodoListApiView, TodoDetailApiView

urlpatterns = [ # Access paths to the two points
    path("api", TodoListApiView.as_view()), 
    path("api/<int:todo_id>", TodoDetailApiView.as_view()),
]
