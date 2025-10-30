from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.http import HttpResponse
from .models import Student, Teacher, HealthRecord, DoctorNote
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

#new imports
from django.shortcuts import render     
from .models import Student, Teacher, HealthRecord, DoctorNote  
from django.shortcuts import render, redirect, get_object_or_404    
from django.contrib import messages   
from .models import Student, Teacher, HealthRecord, DoctorNote     

# Doctor login (fixed for now)
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if username == "Rama" and password == "12345":
            request.session["doctor"] = username
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid credentials")
    return render(request, "login.html")


# Logout
def logout_view(request):
    logout(request)
    request.session.flush()
    return redirect("login")


# ✅ Dashboard view
def dashboard(request):
    if "doctor" not in request.session:
        return redirect("login")

    record = None
    category = None
    health_records = None
    notes = None

    # ✅ Add new patient
    if request.method == "POST" and "add_patient_btn" in request.POST:
        patient_type = request.POST.get("patient_type")
        patient_id = request.POST.get("patient_id")
        name = request.POST.get("name")

        if patient_type == "Student":
            branch = request.POST.get("branch")
            year = request.POST.get("year")
            if not Student.objects.filter(usn=patient_id).exists():
                Student.objects.create(usn=patient_id, name=name, branch=branch, year=year)
                messages.success(request, f"Student {name} added successfully.")
            else:
                messages.info(request, f"Student with USN {patient_id} already exists.")
        elif patient_type == "Teacher":
            dept = request.POST.get("dept")
            if not Teacher.objects.filter(isn=patient_id).exists():
                Teacher.objects.create(isn=patient_id, name=name, dept=dept)
                messages.success(request, f"Teacher {name} added successfully.")
            else:
                messages.info(request, f"Teacher with ISN {patient_id} already exists.")

    # ✅ Fetch patient details
    elif request.method == "POST" and "fetch_btn" in request.POST:
        category = request.POST.get("category")
        id_value = request.POST.get("id_value")

        if category == "Student":
            record = Student.objects.filter(usn=id_value).first()
            if record:
                health_records = HealthRecord.objects.filter(usn=record)
                notes = DoctorNote.objects.filter(record__in=health_records)
            else:
                messages.warning(request, f"No student found with USN: {id_value}")

        elif category == "Teacher":
            record = Teacher.objects.filter(isn=id_value).first()
            if record:
                health_records = HealthRecord.objects.filter(isn=record)
                notes = DoctorNote.objects.filter(record__in=health_records)
            else:
                messages.warning(request, f"No teacher found with ISN: {id_value}")

    # ✅ Add health record
    elif request.method == "POST" and "add_health_btn" in request.POST:
        category = request.POST.get("category")
        id_value = request.POST.get("id_value")
        condition = request.POST.get("condition")

        if category == "Student":
            student = Student.objects.filter(usn=id_value).first()
            if student:
                HealthRecord.objects.create(condition_details=condition, patient_type="Student", usn=student)
                messages.success(request, "Health record added successfully.")
        elif category == "Teacher":
            teacher = Teacher.objects.filter(isn=id_value).first()
            if teacher:
                HealthRecord.objects.create(condition_details=condition, patient_type="Teacher", isn=teacher)
                messages.success(request, "Health record added successfully.")

    # ✅ Add doctor note
    elif request.method == "POST" and "add_note_btn" in request.POST:
        patient_type = request.POST.get("patient_type")
        patient_name = request.POST.get("patient_name")
        note_text = request.POST.get("note")

        if patient_type == "Student":
            student = Student.objects.filter(name=patient_name).first()
            if student:
                last_record = HealthRecord.objects.filter(usn=student).order_by('-date_recorded').first()
                if last_record:
                    DoctorNote.objects.create(record=last_record, note_text=note_text)
                    messages.success(request, "Note added successfully.")
        elif patient_type == "Teacher":
            teacher = Teacher.objects.filter(name=patient_name).first()
            if teacher:
                last_record = HealthRecord.objects.filter(isn=teacher).order_by('-date_recorded').first()
                if last_record:
                    DoctorNote.objects.create(record=last_record, note_text=note_text)
                    messages.success(request, "Note added successfully.")

    # ✅ Export data to Excel
    if request.method == "GET" and request.GET.get("export") == "excel":
        students = Student.objects.all().values()
        teachers = Teacher.objects.all().values()
        records = HealthRecord.objects.all().values()
        notes = DoctorNote.objects.all().values()

        df_students = pd.DataFrame(students)
        df_teachers = pd.DataFrame(teachers)
        df_records = pd.DataFrame(records)
        df_notes = pd.DataFrame(notes)

        with BytesIO() as b:
            writer = pd.ExcelWriter(b, engine="openpyxl")
            df_students.to_excel(writer, index=False, sheet_name="Students")
            df_teachers.to_excel(writer, index=False, sheet_name="Teachers")
            df_records.to_excel(writer, index=False, sheet_name="HealthRecords")
            df_notes.to_excel(writer, index=False, sheet_name="DoctorNotes")
            writer.close()
            response = HttpResponse(
                b.getvalue(),
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            response["Content-Disposition"] = 'attachment; filename="All_Patient_Data.xlsx"'
            return response

    # ✅ Export data to PDF
    if request.method == "GET" and request.GET.get("export") == "pdf":
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        y = 800
        p.setFont("Helvetica", 12)
        p.drawString(200, y, "All Patient Records")
        y -= 30

        for s in Student.objects.all():
            p.drawString(50, y, f"Student: {s.name} ({s.usn}) - {s.branch}, Year {s.year}")
            y -= 20
            for rec in HealthRecord.objects.filter(usn=s):
                p.drawString(80, y, f"Condition: {rec.condition_details}")
                y -= 20
                for note in DoctorNote.objects.filter(record=rec):
                    p.drawString(100, y, f"Note: {note.note_text}")
                    y -= 20
            y -= 15
            if y < 100:
                p.showPage()
                y = 800

        for t in Teacher.objects.all():
            p.drawString(50, y, f"Teacher: {t.name} ({t.isn}) - {t.dept}")
            y -= 20
            for rec in HealthRecord.objects.filter(isn=t):
                p.drawString(80, y, f"Condition: {rec.condition_details}")
                y -= 20
                for note in DoctorNote.objects.filter(record=rec):
                    p.drawString(100, y, f"Note: {note.note_text}")
                    y -= 20
            y -= 15
            if y < 100:
                p.showPage()
                y = 800

        p.save()
        pdf = buffer.getvalue()
        buffer.close()
        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="All_Patient_Data.pdf"'
        return response

    # For dropdowns
    students = Student.objects.all()
    teachers = Teacher.objects.all()
    all_records = HealthRecord.objects.all().order_by("-date_recorded")

    return render(request, "dashboard.html", {
        "record": record,
        "category": category,
        "health_records": health_records,
        "notes": notes,
        "students": students,
        "teachers": teachers,
        "records": all_records,
    })

#new features
#view all patients
def view_all_patients(request):
    # Fetch all students and teachers from the database
    all_students = Student.objects.all()
    all_teachers = Teacher.objects.all()
    
    # Pass them to the template
    context = {
        'students': all_students,
        'teachers': all_teachers,
    }
    return render(request, 'view_all_patients.html', context)

def delete_student(request, usn):
    # Only allow POST requests to prevent accidental deletion
    if request.method == 'POST':
        # Find the student by their USN, or show a 404 page if not found
        student = get_object_or_404(Student, usn=usn)
        student_name = student.name
        student.delete()
        
        # Send a success message back to the user
        messages.success(request, f"Student '{student_name}' has been deleted successfully.")
        
    # Redirect back to the all patients list, no matter what
    return redirect('view_all_patients')


def delete_teacher(request, isn):
    # Only allow POST requests
    if request.method == 'POST':
        # Find the teacher by their ISN
        teacher = get_object_or_404(Teacher, isn=isn)
        teacher_name = teacher.name
        teacher.delete()
        
        # Send a success message
        messages.success(request, f"Teacher '{teacher_name}' has been deleted successfully.")
        
    # Redirect back to the all patients list
    return redirect('view_all_patients')