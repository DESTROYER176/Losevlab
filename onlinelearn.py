import json
import xml.etree.ElementTree as ET

class StudentNotFoundError(Exception):
    pass


class CourseNotFoundError(Exception):
    pass


class EnrollmentError(Exception):
    pass


class Person:
    def __init__(self, name, email, person_id):
        self.name = name
        self.email = email
        self.person_id = person_id

    def __str__(self):
        return f"{self.name} ({self.email})"


class Student(Person):
    def __init__(self, name, email, student_id):
        super().__init__(name, email, student_id)
        self.courses = []  # упрощенный список курсов

    def enroll(self, course):
        try:
            if course in self.courses:
                raise EnrollmentError(f"Студент уже записан на курс {course.title}")

            if course.add_student(self):
                self.courses.append(course)
                print(f"Студент {self.name} записан на курс {course.title}")
                return True
            return False
        except EnrollmentError as e:
            print(f"Ошибка: {e}")
            return False


class Instructor(Person):
    def __init__(self, name, email, instructor_id):
        super().__init__(name, email, instructor_id)
        self.courses = []

    def create_course(self, title, description, course_id):
        course = Course(title, description, course_id, self)
        self.courses.append(course)
        return course


class Course:
    def __init__(self, title, description, course_id, instructor):
        self.title = title
        self.description = description
        self.course_id = course_id
        self.instructor = instructor
        self.students = []
        self.grades = {}

    def add_student(self, student):
        try:
            if student in self.students:
                raise EnrollmentError(f"Студент {student.name} уже в курсе")

            self.students.append(student)
            return True
        except EnrollmentError as e:
            print(f"Ошибка: {e}")
            return False

    def add_grade(self, student, grade):
        try:
            if student not in self.students:
                raise StudentNotFoundError("Студент не найден в курсе")

            if grade < 0 or grade > 100:
                raise ValueError("Оценка должна быть от 0 до 100")

            self.grades[student.person_id] = grade
            print(f"Оценка {grade} добавлена для {student.name}")
            return True
        except (StudentNotFoundError, ValueError) as e:
            print(f"Ошибка: {e}")
            return False


class LearningPlatform:
    def __init__(self):
        self.students = {}
        self.instructors = {}
        self.courses = {}

    def add_student(self, student):
        self.students[student.person_id] = student

    def add_instructor(self, instructor):
        self.instructors[instructor.person_id] = instructor

    def add_course(self, course):
        self.courses[course.course_id] = course

class FileManager:
    @staticmethod
    def save_to_json(platform, filename):
        """Сохранить данные в JSON"""
        try:
            data = {
                "students": [
                    {
                        "id": s.person_id,
                        "name": s.name,
                        "email": s.email,
                        "courses": [c.course_id for c in s.courses]
                    } for s in platform.students.values()
                ],
                "instructors": [
                    {
                        "id": i.person_id,
                        "name": i.name,
                        "email": i.email,
                        "courses": [c.course_id for c in i.courses]
                    } for i in platform.instructors.values()
                ],
                "courses": [
                    {
                        "id": c.course_id,
                        "title": c.title,
                        "description": c.description,
                        "instructor_id": c.instructor.person_id,
                        "students": [s.person_id for s in c.students],
                        "grades": c.grades
                    } for c in platform.courses.values()
                ]
            }

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            print(f" Данные сохранены в {filename}")
            return True

        except Exception as e:
            print(f" Ошибка сохранения JSON: {e}")
            return False

    @staticmethod
    def load_from_json(filename):
        """Загрузить данные из JSON"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)

            platform = LearningPlatform()

            for i_data in data.get("instructors", []):
                instructor = Instructor(
                    i_data["name"],
                    i_data["email"],
                    i_data["id"]
                )
                platform.add_instructor(instructor)

            for s_data in data.get("students", []):
                student = Student(
                    s_data["name"],
                    s_data["email"],
                    s_data["id"]
                )
                platform.add_student(student)

            for c_data in data.get("courses", []):
                instructor_id = c_data["instructor_id"]
                if instructor_id in platform.instructors:
                    instructor = platform.instructors[instructor_id]
                    course = Course(
                        c_data["title"],
                        c_data["description"],
                        c_data["id"],
                        instructor
                    )
                    platform.add_course(course)
                    instructor.courses.append(course)

            for s_data in data.get("students", []):
                student_id = s_data["id"]
                if student_id in platform.students:
                    student = platform.students[student_id]
                    for course_id in s_data.get("courses", []):
                        if course_id in platform.courses:
                            course = platform.courses[course_id]
                            student.courses.append(course)
                            course.students.append(student)

            for c_data in data.get("courses", []):
                course_id = c_data["id"]
                if course_id in platform.courses:
                    course = platform.courses[course_id]
                    course.grades = {int(k): v for k, v in c_data.get("grades", {}).items()}

            print(f" Данные загружены из {filename}")
            return platform

        except Exception as e:
            print(f" Ошибка загрузки JSON: {e}")
            return None

    @staticmethod
    def save_to_xml(platform, filename):
        """Сохранить данные в XML"""
        try:
            root = ET.Element("learning_platform")

            students_elem = ET.SubElement(root, "students")
            for student in platform.students.values():
                s_elem = ET.SubElement(students_elem, "student")
                ET.SubElement(s_elem, "id").text = str(student.person_id)
                ET.SubElement(s_elem, "name").text = student.name
                ET.SubElement(s_elem, "email").text = student.email

                courses_elem = ET.SubElement(s_elem, "courses")
                for course in student.courses:
                    ET.SubElement(courses_elem, "course_id").text = str(course.course_id)

            instructors_elem = ET.SubElement(root, "instructors")
            for instructor in platform.instructors.values():
                i_elem = ET.SubElement(instructors_elem, "instructor")
                ET.SubElement(i_elem, "id").text = str(instructor.person_id)
                ET.SubElement(i_elem, "name").text = instructor.name
                ET.SubElement(i_elem, "email").text = instructor.email

            courses_elem = ET.SubElement(root, "courses")
            for course in platform.courses.values():
                c_elem = ET.SubElement(courses_elem, "course")
                ET.SubElement(c_elem, "id").text = str(course.course_id)
                ET.SubElement(c_elem, "title").text = course.title
                ET.SubElement(c_elem, "description").text = course.description
                ET.SubElement(c_elem, "instructor_id").text = str(course.instructor.person_id)

                students_elem = ET.SubElement(c_elem, "students")
                for student in course.students:
                    ET.SubElement(students_elem, "student_id").text = str(student.person_id)

                grades_elem = ET.SubElement(c_elem, "grades")
                for student_id, grade in course.grades.items():
                    grade_elem = ET.SubElement(grades_elem, "grade")
                    ET.SubElement(grade_elem, "student_id").text = str(student_id)
                    ET.SubElement(grade_elem, "value").text = str(grade)

            tree = ET.ElementTree(root)
            tree.write(filename, encoding='utf-8', xml_declaration=True)
            print(f" Данные сохранены в {filename}")
            return True

        except Exception as e:
            print(f" Ошибка сохранения XML: {e}")
            return False


def main():
    print("ПЛАТФОРМА ОНЛАЙН-ОБУЧЕНИЯ")
    print("=" * 40)

    platform = LearningPlatform()

    instructor1 = Instructor("Анна Иванова", "anna@university.ru", 1)
    instructor2 = Instructor("Петр Сидоров", "petr@university.ru", 2)
    platform.add_instructor(instructor1)
    platform.add_instructor(instructor2)

    course1 = instructor1.create_course("Python для начинающих", "Основы Python", 101)
    course2 = instructor2.create_course("Веб-разработка", "HTML, CSS, JavaScript", 102)
    platform.add_course(course1)
    platform.add_course(course2)

    student1 = Student("Иван Петров", "ivan@student.ru", 1001)
    student2 = Student("Мария Козлова", "maria@student.ru", 1002)
    platform.add_student(student1)
    platform.add_student(student2)

    print("\n ЗАПИСЬ НА КУРСЫ:")
    student1.enroll(course1)
    student1.enroll(course2)
    student2.enroll(course1)

    student1.enroll(course1)

    print("\n ВЫСТАВЛЕНИЕ ОЦЕНОК:")
    course1.add_grade(student1, 85)
    course1.add_grade(student2, 92)
    course2.add_grade(student1, 78)

    course1.add_grade(student1, 150)

    print("\n ИНФОРМАЦИЯ О ПЛАТФОРМЕ:")
    print(f"Студентов: {len(platform.students)}")
    print(f"Преподавателей: {len(platform.instructors)}")
    print(f"Курсов: {len(platform.courses)}")

    for course in platform.courses.values():
        print(f"\nКурс: {course.title}")
        print(f"Студентов: {len(course.students)}")
        if course.grades:
            avg_grade = sum(course.grades.values()) / len(course.grades)
            print(f"Средняя оценка: {avg_grade:.1f}")

    print("\n СОХРАНЕНИЕ ДАННЫХ:")
    FileManager.save_to_json(platform, "learning_data.json")
    FileManager.save_to_xml(platform, "learning_data.xml")

    print("\n ЗАГРУЗКА ДАННЫХ:")
    loaded_platform = FileManager.load_from_json("learning_data.json")

    if loaded_platform:
        print(f"Загружено: {len(loaded_platform.students)} студентов, "
              f"{len(loaded_platform.courses)} курсов")


if __name__ == "__main__":
    main()