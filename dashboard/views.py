from django.shortcuts import render
from rest_framework.views import APIView

class DashboardView(APIView):
    def get(self, request, *args, **kwargs):
        # "Dashboard/dashboard.html" assumes your template is inside
        # templates/Dashboard/dashboard.html
        return render(request, "Dashboard/dashboard.html")