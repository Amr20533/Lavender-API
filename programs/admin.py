from django.contrib import admin
from .models import *

admin.site.register(MusicCard)
admin.site.register(PsychoMeasurementQuiz)
admin.site.register(QuizQuestion)
admin.site.register(QuizAnswer)
admin.site.register(UserAnswer)
admin.site.register(QuizResultCategory)
admin.site.register(QuizResult)


admin.site.register(Course)
admin.site.register(CourseVideo)
admin.site.register(Enrollment)


admin.site.register(FreeProgram)
admin.site.register(ProgramSession)
admin.site.register(ProgramCategory)
admin.site.register(SessionItem)
