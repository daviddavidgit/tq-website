from django.apps import AppConfig


class CoursesConfig(AppConfig):
    name = "courses"
    verbose_name = "Course Administration"

    def ready(self):
        import courses.signals