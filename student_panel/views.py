from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from django.db.models import F
from django.db.models import Sum
import requests
from .serializers import ReportSerializer
from .tasks import (
    max_amount_of_study,
    min_amount_of_study,
    expected_hour,
    sum_of_report,
    punishment_for_fraction_of_hour,
    average_of_amount_of_report
)
from .models import Report
from rest_framework import authentication, permissions, generics

from rest_framework_simplejwt.views import TokenObtainPairView

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, login

from .models import Student
from admin_panel.models import Admin
from .serializers import StudentSerializer, StudentTokenObtainPairSerializer, LoginViewAsStudentSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime


class DailyReportView(generics.CreateAPIView):
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        report = serializer.create(serializer.validated_data)
        return Response({
            'message': "Report Created successfully",
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)

    # def post(self, request):
    #     serializer = ReportSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save(user=request.user)
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UnsubmittedReportsView(APIView):
    def get(self, request):
        user = request.user
        report_count = Report.objects.filter(user=user).count()
        submitted_count = Report.objects.filter(user=user, created_at__lte=F('deadline')).count()
        unsubmitted_count = report_count - submitted_count
        return Response({'unsubmitted_count': unsubmitted_count, 'total_count': report_count})


class DelayedReportsView(APIView):
    def get(self, request):
        user = request.user
        delayed_reports = Report.objects.filter(user=user, delayed=True)
        serializer = ReportSerializer(delayed_reports, many=True)
        return Response(serializer.data)


class ReportSummaryView(APIView):
    def get(self, request):
        user = request.user
        amount = Report.objects.filter(user=user).values('report_number').annotate(
            total_study=Sum('study_amount'))
        return Response(amount)


class SomeOtherClass(APIView):
    def some_method(self, request):
        user = self.request.user
        report_summary_response = requests.get('http://localhost:8000/reports/summery/',
                                               auth=(user.username, user.password))
        report_summary = report_summary_response.json()
        # do something with the report_summary list here
        return report_summary


class ReportView(APIView):

    def get(self, request, *args, **kwargs):
        max_amount_of_study.apply_async(args="amount")
        min_amount_of_study.apply_async(args="amount")
        expected_hour.apply_async(args="amount")
        sum_of_report.apply_async(args="amount")
        punishment_for_fraction_of_hour.apply_async(args="amount")
        average_of_amount_of_report.apply_async(args="amount")


class CreateStudentView(APIView):
    @method_decorator(login_required)
    def post(self, request):
        # Check if the user is an admin
        if not request.user.is_staff:
            return Response({'error': 'You do not have permission to create a student account.'},
                            status=status.HTTP_403_FORBIDDEN)

        # Get the request data and create the new student account
        try:
            admin = Admin.objects.get(user=request.user)
            student_firstname = request.data['first_name']
            student_lastname = request.data['last_name']
            student_phone_number = request.data['phone_number']
            student_birthday = request.data['date_of_birth']
            student_identity_code = request.data['identity_code']
            student_personality = request.data['personality']
            student_avatar = request.data['avatar']
            student = admin.create_student_account(student_firstname, student_lastname, student_phone_number,
                                                   student_birthday, student_identity_code, student_personality,
                                                   student_avatar)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Return the new student object
        serializer = StudentSerializer(student)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class StudentLoginView(TokenObtainPairView):
    serializer_class = StudentTokenObtainPairSerializer


class LoginViewAsStudent(APIView):

    def post(self, request):
        # Get the username and password from the request data
        username = request.data.get('username')
        password = request.data.get('password')

        # Authenticate the user using Django's built-in function
        student = authenticate(request, username=username, password=password)

        # Check if authentication was using
        if student is not None:
            # Log the user in using Django's built-in function
            login(request, student)

            serializer = LoginViewAsStudentSerializer(student)
            # token, _ = Token.objects.get_or_create(user=student)

            # return redirect('detail', pk=student.pk)
            # else:
            #     return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
            # Return a success response with the user's information
            return Response(serializer.data, status=status.HTTP_200_OK)



        else:
            # Return an error response if authentication failed
            return Response({"error": "Invalid username  or password"}, status=status.HTTP_401_UNAUTHORIZED)


class StudentDetails(APIView):
    authentication_classes = [authentication.SessionAuthentication, authentication.BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = StudentSerializer(request.user)
        return Response(serializer.data)


class StudentDetailView(generics.RetrieveAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

    def get_object(self):
        user_id = self.request.user.id
        return Student.objects.get(user=user_id)

# {"username": "student_09109232094", "password": "0020064586"}