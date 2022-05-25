from flask import Flask, jsonify, request, make_response
from flask_mysqldb import MySQL
from datetime import datetime
from threading import Thread
from win10toast import ToastNotifier

application = Flask(__name__)
application.config['MYSQL_HOST'] = 'localhost'
application.config['MYSQL_USER'] = 'root'
application.config['MYSQL_PASSWORD'] = ''
application.config['MYSQL_DB'] = 'memo'
mysql = MySQL(application)
    

@application.route('/', methods=['GET', 'POST', 'PUT', 'DELETE'])
def index():
    try:
        thread = Thread(target=showNotify)
        thread.start()
        if request.method == 'GET':
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM note WHERE active = 1 ORDER BY pin, tgl DESC")
            data = cursor.fetchall()
            cursor.close()
        elif request.method == 'POST' :
            judul = request.form['judul']
            isi = request.form['isi']
            pin = request.form['pin']
            tgl = datetime.now()
            active = 1;
            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO note(judul,isi,pin,tgl,active) VALUES('%s', '%s', '%d', '%s', '%d');" % (
                judul, isi, pin, tgl, active))
            mysql.connection.commit()
            cursor.close()
        elif request.method == 'PUT' :
            id = request.form['id']
            judul = request.form['judul']
            isi = request.form['isi']
            pin = request.form['pin']
            tgl = datetime.now()
            active = 1;
            cursor = mysql.connection.cursor()
            cursor.execute("UPDATE note SET judul = %s, isi = %s, pin = %d, tgl = %s, active = %s WHERE id = %d;" % (
                judul, isi, pin, tgl, active, id))
            mysql.connection.commit()
            cursor.close()
        else :
            id = request.form['id']
            cursor = mysql.connection.cursor()
            cursor.execute("UPDATE note SET active = 0 WHERE id = %d;" % (id))
            cursor.close()
    except Exception as e:
        return make_response(jsonify({'error': str(e)}))
    return make_response(jsonify({'data': data}))

@application.route('/reminder', methods=['GET', 'POST', 'PUT', 'DELETE'])
def remind():
    try:
        if request.method == 'GET':
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM reminder ORDER BY pin, tgl DESC")
            data = cursor.fetchall()
            cursor.close()
        elif request.method == 'POST' :
            judul = request.form['judul']
            isi = request.form['isi']
            pin = request.form['pin']
            tgl = datetime.now()
            waktu = request.form['waktu']
            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO reminder(judul,isi,pin,tgl,waktu) VALUES('%s', '%s', '%d', '%s', '%s');" % (
                judul, isi, pin, tgl, waktu))
            mysql.connection.commit()
            cursor.close()
        elif request.method == 'PUT' :
            id = request.form['id']
            judul = request.form['judul']
            isi = request.form['isi']
            pin = request.form['pin']
            tgl = datetime.now()
            waktu = request.form['waktu']
            cursor = mysql.connection.cursor()
            cursor.execute("UPDATE reminder SET judul = %s, isi = %s, pin = %d, tgl = %s, waktu = %s WHERE id = %d;" % (
                judul, isi, pin, tgl, waktu, id))
            mysql.connection.commit()
            cursor.close()
        else :
            id = request.form['id']
            cursor = mysql.connection.cursor()
            cursor.execute("DELETE FROM reminder WHERE id = %d;" % (id))
            mysql.connection.commit()
            cursor.close()
    except Exception as e:
        return make_response(jsonify({'error': str(e)}))
    return make_response(jsonify({'data': data}))

@application.route('/archive', methods=['GET', 'DELETE'])
def archive():
    try:
        if request.method == 'GET':
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM note WHERE active = 0 ORDER BY pin, tgl DESC")
            data = cursor.fetchall()
            cursor.close()
        else :
            id = request.form['id']
            cursor = mysql.connection.cursor()
            cursor.execute("DELETE FROM note WHERE id = %d;" % (id))
            mysql.connection.commit()
            cursor.close()
    except Exception as e:
        return make_response(jsonify({'error': str(e)}))
    return make_response(jsonify({'data': data}))

def notify(judul, isi, waktu):
    notify = ToastNotifier()
    notify.show_toast(judul, f"""Alarm akan disetel {waktu} detik lagi.""", duration=waktu)
    notify.show_toast(judul, isi, duration=5)

def showNotify():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM reminder")
    for each in cursor.fetchall():
        waktu = int(each[5].timestamp() - datetime.now().timestamp())
        notify(each[1], each[2], waktu)
        cursor.execute("DELETE FROM reminder WHERE id = %d" % (each[0]))
    cursor.close()

if __name__ == '__main__':
    application.run(debug=True)
