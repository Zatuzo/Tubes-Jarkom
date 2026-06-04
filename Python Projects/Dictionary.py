student_scores = {
    'Harry': 88,
    'Ron': 78,
    'Hermione': 95,
    'Draco': 75,
    'Neville': 60
}

student_grades = {}

for students in student_scores:
    grade = student_scores[students]
    if grade > 90:
        Grade = "Outstanding"
    elif grade > 80 and grade <= 90:
        Grade = "Exceeds Expectations"
    elif grade > 70 and grade <= 80:
        Grade = "Acceptable"
    else:
        Grade = "Fail"
    
    student_grades[students] = Grade
    
print(student_grades)