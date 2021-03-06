from flask import Flask, render_template, request, session, redirect, url_for, g, flash, abort, Blueprint
import functools
from portal.db import get_db
import psycopg2
import psycopg2.extras
from .auth import login_required, teacher_required

bp = Blueprint('assign', __name__)


@bp.route('/assignments', methods=['GET', 'POST'])
@login_required
def assignment_page():
    student_assignments = []
    teach_assignments = []
    with get_db() as con:
        with con.cursor() as cur:
            this_teach = g.user[0]
            cur.execute("SELECT course_id, course_name FROM courses WHERE teacher_id = %s;", (this_teach,))
            thier_classes = cur.fetchall()
            cur.execute("SELECT student_id,session_id FROM user_sessions WHERE student_id = %s;", (this_teach,))
            students_classes = cur.fetchall()
            for tc in students_classes:
                with get_db() as con:
                    with con.cursor() as cur:
                        cur.execute("SELECT assignment_name, points_earned, points_available, instructions, due_date, sesh_id FROM assignments WHERE sesh_id  = %s", (tc[1],))
                        student_assignments = cur.fetchall()
            session_list = {}
            class_list = []
            for cl in thier_classes:
                with get_db() as con:
                    with con.cursor() as cur:
                        cur.execute("SELECT * FROM course_sessions where course_id = %s;", (cl[0],))
                        thier_sessions = cur.fetchall()
                        tostring = str(cl[0])
                        oneout = tostring.replace('[', '')
                        twoout= oneout.replace(']', '')
                        class_list.append(twoout)
                        session_list.update( {twoout : thier_sessions})
                        for sesh in thier_sessions:
                            sesh.append(cl[1])
                        teach_assignments = teachers_assignments(class_list)

    if request.method== 'POST':
        assign_name = request.form['assign-name']
        points_ttl = request.form['points-avb']
        instructions = request.form['instructions']
        session = request.form['session_id']
        duedate = request.form['due_date']
        with get_db() as con:
            with con.cursor() as cur:
                cur.execute("INSERT INTO assignments (assignment_name, points_available, instructions, due_date, sesh_id) VALUES (%s,%s,%s,%s,%s);", (assign_name, points_ttl, instructions, duedate, session ))
                con.commit()
                cur.execute("SELECT assignment_id FROM assignments WHERE assignment_name = %s", (assign_name,))
                aid = cur.fetchall()
                cur.execute("SELECT student_id FROM user_sessions WHERE session_id = %s;", (session))
                students_assigned = cur.fetchall()
        for students in students_assigned:
            with get_db() as con:
                 with con.cursor() as cur:
                    cur.execute("INSERT INTO user_assignments (point_earned , assignment_id,student_id) VALUES (%s,%s,%s);", (0, aid[0][0], students[0]))
                    con.commit()
        return redirect(url_for('assign.assignment_page'))
    return render_template('assignments.html', teach_assignments = teach_assignments, student_assignments = student_assignments, classes=class_list, sessions=session_list)

def get_assignment(id):
    with get_db() as con:
        with con.cursor() as cur:
            cur.execute('SELECT assignment_name , points_available, instructions, due_date FROM assignments WHERE assignment_id = %s', [id])
            assignment = cur.fetchone()
    return assignment

@bp.route('/<id>/assignment-delete', methods=('POST','GET'))
@login_required
@teacher_required
def delete_assignment(id):
    get_assignment(id)
    with get_db() as con:
        with con.cursor() as cur:
            cur.execute('DELETE FROM user_assignments WHERE assignment_id = %s',[id])
            con.commit()
            cur.execute('DELETE FROM assignments WHERE assignment_id = %s',[id])
            con.commit()
    return redirect(url_for('assign.assignment_page'))

@bp.route('/<id>/assignment-update', methods=['GET', 'POST'])
@login_required
@teacher_required
def update_assignment(id):
    assignment = get_assignment(id)
    grades = {}
    with get_db() as con:
        with con.cursor() as cur:
            cur.execute('SELECT point_earned, assignment_id, student_id FROM user_assignments WHERE assignment_id = %s;', [id])
            yes = cur.fetchall()
            cur.execute('SELECT points_available FROM assignments WHERE assignment_id = %s;', [id])
            possible = cur.fetchone()
    for students in yes:
        with get_db() as con:
            with con.cursor() as cur:
                cur.execute("SELECT first_name, last_name FROM users where id = %s;", (students[2],))
                people = cur.fetchone()
                cur.execute('SELECT point_earned FROM user_assignments WHERE student_id = %s', (students[2],))
                earned = cur.fetchone()
                people.extend(earned)
                people.extend(possible)
                grades[f'{students[2]}'] = people
    if assignment is None:
        print(f"User {g.user[0]} is attempting to edit an assignment that doesn't exist.")
        return abort(404)
    if request.method== 'POST':
        assign_name = request.form['assign-name']
        points_ttl = request.form['points-avb']
        instructions = request.form['instructions']
        duedate = request.form['due_date']
        with get_db() as con:
            with con.cursor() as cur:
                cur.execute("UPDATE assignments SET assignment_name = %s, points_available = %s, instructions = %s, due_date = %s WHERE assignment_id  = %s", (assign_name,points_ttl,instructions,duedate,id, ))
                con.commit()
            input_grades(id)
        return redirect(url_for('assign.assignment_page'))
    return render_template('update-assignment.html', assignment=assignment, grades = grades)

def teachers_assignments(class_list):
    for cla in class_list:
        with get_db() as con:
            with con.cursor() as cur:
                cur.execute("SELECT assignment_id, assignment_name, points_earned, points_available, instructions, due_date, sesh_id FROM assignments WHERE sesh_id  = %s", (cla,))
                teach_assignment = cur.fetchall()
                return teach_assignment

def input_grades(id):
    points_earned = request.form['earned']
    student = request.form['student']
    with get_db() as con:
        with con.cursor() as cur:
            print(student)
            cur.execute("UPDATE user_assignments SET point_earned = %s  WHERE student_id = %s AND assignment_id  = %s", (points_earned,student,id, ))
            con.commit()
