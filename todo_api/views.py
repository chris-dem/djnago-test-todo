from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from pipe import where

from .models import Todo
from .serializers import TodoSerializer


class TodoListApiView(APIView):
    # 1. List all
    def get(self, _request: Request, *args, **kwargs):
        """
        List all the todo items
        """
        todo = Todo.objects.all()
        serializer = TodoSerializer(todo, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 2. Create
    def post(self, request: Request, *args, **kwargs):
        """
        Create the Todo with given todo data
        """
        data = {
            "title": request.data.get("title"),
            "description": request.data.get("description"),
            "status": request.data.get("status"),
        }
        serializer = TodoSerializer(data=data)
        if serializer.is_valid():  # Ensure data are valid
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TodoDetailApiView(APIView):
    def get_object(self, todo_id: int):
        """
        Helper method to get the object with the given todo_id
        """
        try:
            return Todo.objects.get(id=todo_id)
        except:
            return None

    def get(self, _request: Request, todo_id: int, *args, **kwargs):
        """
        Retrieve the Todo with the given todo_id
        """
        todo_instance = self.get_object(todo_id)
        if not todo_instance:  # If the object does not exist
            return Response(
                {"res": "Object does not exist"}, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = TodoSerializer(todo_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request: Request, todo_id: int, *args, **kwargs):
        todo_instance = self.get_object(todo_id)
        if not todo_instance:
            return Response(
                {"res": "Object with todo id does not exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = dict(
            (
                ("description", request.data.get("description")),
                ("title", request.data.get("title")),
                ("status", request.data.get("status")),
            )
            | where(
                lambda x: x[1] is not None
            )  # If any of the attributes does not exist, remove them from the dict
        )
        serializer = TodoSerializer(
            instance=todo_instance, data=data, partial=True
        )  # partially update the instance with the new data
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, _request: Request, todo_id: int, *args, **kwargs):
        """
        Deletes the todo item with given todo_id if exists
        """
        todo_instance = self.get_object(todo_id)
        if not todo_instance:
            return Response(
                {"res": "Object with todo id does not exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        todo_instance.delete()
        return Response({"res": "Object deleted!"}, status=status.HTTP_200_OK)
