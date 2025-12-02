
# assignments/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Assignment
from .serializers import AssignmentSerializer

class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.select_related('asset','employee').all()
    serializer_class = AssignmentSerializer

    def perform_create(self, serializer):
        serializer.save(assigned_by=self.request.user, active=True)

    @action(detail=True, methods=['post'])
    def return_asset(self, request, pk=None):
        assignment = self.get_object()
        if not assignment.active:
            return Response({'detail':'Already returned'}, status=status.HTTP_400_BAD_REQUEST)
        assignment.mark_returned()
        return Response({'detail':'Asset returned'}, status=status.HTTP_200_OK)
