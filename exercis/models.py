from django.db import models
# from django.contrib.auth.models import User
from student.models import Student
from mentor.models import Mentor

# class ExerciseModel(models.Model):
#     exercise_name = models.CharField(max_length=200)
#     caption = models.TextField()
#     # exercise_file = models.FileField(upload_to='exercise/', blank=True, null=True)
#     exercise_file = models.FileField(max_length=200, blank=True, null=True)
#     # mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE)
#     # Students = models.ManyToManyField(Student, through='StudentExerciseModel')
#     students = models.ManyToManyField(Student)
#     """ through?"""


class StudentExerciseModel(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    # caption = models.CharField(max_length=500)
    # exercises = models.ForeignKey(ExerciseModel, on_delete=models.CASCADE)
    exercise_text = models.TextField(blank=True, null=True)
    
    # exercise_file = models.ForeignKey(ExerciseModel,on_delete=models.CASCADE)
    exercise_file = models.FileField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_seen = models.BooleanField(default=False)
    done_exercise = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.exercise_text


# class MentorExerciseModel(models.Model):
#     mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE)
#     # student_name = models.ForeignKey(Student, on_delete=models.CASCADE)
#     student_name = models.ManyToManyField(Student)
#     send_to_all = models.BooleanField(default=False)

#     # exercise_name = models.ForeignKey(ExerciseModel,on_delete=models.CASCADE)
#     exercise_name = models.CharField(max_length=200)
#     is_seen_by_mentor = models.BooleanField(default=False)
#     data_submitted = models.DateField(auto_now_add=True)
#     caption = models.TextField()
#     exercise_file = models.FileField(max_length=200, blank=True, null=True)


class MentorExerciseModel(models.Model):
    mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE)
    send_to_all = models.BooleanField(default=False)
    student_name = models.ManyToManyField(Student, blank=True)
    exercise_name = models.CharField(max_length=200)
    is_seen_by_mentor = models.BooleanField(default=False)
    data_submitted = models.DateField(auto_now_add=True)
    caption = models.TextField()
    exercise_file = models.FileField(max_length=200, blank=True, null=True)


    