from abc import ABC, abstractmethod

# SRP: User Authentication
class AuthenticationService:
  def authenticate(self, username: str, password: str) -> bool:
    # Simulated authentication logic
    users_database = {"john_henry": "henry548", "jane_smith": "securepass"}
    return users_database.get(username) == password

# SRP: Course Management
class CourseManager:
  def __init__(self):
    self.enrolled_students = {}
    
  def enroll_student(self, student_id: int, course_id: int) -> bool:
    # Simulated course enrollment logic
    if course_id not in self.enrolled_students:
      self.enrolled_students[course_id] = []
    if student_id not in self.enrolled_students[course_id]:
      self.enrolled_students[course_id].append(student_id)
      return True
    return False
    
# SRP: Progress Tracking
class ProgressTracker:
  def track_progress(self, student_id: int, course_id: int, progress: float) -> None:
    # Simulated progress tracking logic
    print(f"Student {student_id} made {progress*100}% progress in Course {course_id}")
    
# OCP: Extensible Course Modules
class CourseModule(ABC):
  @abstractmethod
  def display_content(self) -> str:
    pass
    
class TextCourseModule(CourseModule):
  def __init__(self, content: str):
    self.content = content

  def display_content(self) -> str:
    return f"Text Module: {self.content}"
    
class VideoCourseModule(CourseModule):
  def __init__(self, video_url: str):
    self.video_url = video_url
  def display_content(self) -> str:
    return f"Video Module: {self.video_url}"
    
class InteractiveCourseModule(CourseModule):
  def __init__(self, interactions: list):
    self.interactions = interactions
  def display_content(self) -> str:
    return f"Interactive Module: {self.interactions}"
    
# LSP: Hierarchy of Course Modules
def play_module(course_module: CourseModule) -> None:
  print(course_module.display_content())
    
# ISP: Separate Interfaces for User Roles
class StudentFunctionality(ABC):
  @abstractmethod
  def view_courses(self) -> None:
    pass
  @abstractmethod
  def take_quiz(self, quiz_id: int) -> None:
    pass
    
class InstructorFunctionality(ABC):
  @abstractmethod
  def create_course(self, course_name: str) -> None:
    pass
  @abstractmethod
  def grade_quiz(self, student_id: int, quiz_id: int, grade: float) -> None:
    pass
    
class AdministratorFunctionality(ABC):
  @abstractmethod
  def manage_users(self) -> None:
    pass
  @abstractmethod
  def generate_reports(self) -> None:
    pass
    
class Student(StudentFunctionality):
  def view_courses(self) -> None:
    print("Viewing available courses")
    
  def take_quiz(self, quiz_id: int) -> None:
    print(f"Taking quiz {quiz_id}")
    
class Instructor(InstructorFunctionality):
  def create_course(self, course_name: str) -> None:
    print(f"Creating a new course: {course_name}")
    
  def grade_quiz(self, student_id: int, quiz_id: int, grade: float) -> None:
    print(f"Grading quiz {quiz_id} for student {student_id} with grade {grade}")
    
class Administrator(AdministratorFunctionality):
  def manage_users(self) -> None:
    print("Managing users")
  def generate_reports(self) -> None:
    print("Generating reports")
    
# DIP: Dependency Injection
class ElearningPlatform:
  def __init__(self, auth_service, course_manager, progress_tracker):
    self.auth_service = auth_service
    self.course_manager = course_manager
    self.progress_tracker = progress_tracker
  def authenticate_user(self, username: str, password: str) -> bool:
    return self.auth_service.authenticate(username, password)
  def enroll_student(self, student_id: int, course_id: int) -> bool:
    return self.course_manager.enroll_student(student_id, course_id)
  def track_progress(self, student_id: int, course_id: int, progress: float) -> None:
    self.progress_tracker.track_progress(student_id, course_id, progress)

# Dependency injection example
if __name__ == "__main__":
auth_service = AuthenticationService()
course_manager = CourseManager()
progress_tracker = ProgressTracker()
elearning_platform = ElearningPlatform(auth_service, course_manager, progress_tracker)

# Simulate student actions
student = Student()
student.view_courses()
student.take_quiz(1)

# Simulate instructor actions
instructor = Instructor()
instructor.create_course("Python Programming")
instructor.grade_quiz(2, 1, 90.5)

# Simulate administrator actions
administrator = Administrator()
administrator.manage_users()
administrator.generate_reports()

# Simulate e-learning platform usage
username = "john_henry"
password = "henry548"
student_id = 1
course_id = 101
progress = 0.75

if elearning_platform.authenticate_user(username, password):
  if elearning_platform.enroll_student(student_id, course_id):
    elearning_platform.track_progress(student_id, course_id,progress)
