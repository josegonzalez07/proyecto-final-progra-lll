from flask import jsonify, Flask, render_template, session, request, redirect, url_for, flash
import conexion
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'vacio'  

@app.route('/')
def formulario_registro():
    return render_template('registro.html')

@app.route('/registrar', methods=['POST'])
def registrar_usuario():
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    telefono = request.form['telefono']
    email = request.form['email']
    password = request.form['password']

    try:
        conn = conexion.conectar()
        cursor = conn.cursor()

        # Verificar si el usuario ya está registrado
        cursor.execute("SELECT * FROM registros WHERE email = %s", (email,))
        usuario = cursor.fetchone()

        if usuario:
            return jsonify({"message": "Usuario ya registrado"})

        # Insertar el nuevo usuario en la base de datos
        query = """
        INSERT INTO registros (nombre, apellido, telefono, email, password)
        VALUES (%s, %s, %s, %s, %s)
        """
        valores = (nombre, apellido, telefono, email, password)
        cursor.execute(query, valores)
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({"message": "Registro exitoso"})
    except Exception as e:
        print("Error al registrar usuario:", e)
        return jsonify({"message": "Error en el registro"})

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nombre = request.form['nombre']
        password = request.form['password']

        conn = conexion.conectar()
        cursor = conn.cursor()

        # Verificar las credenciales del usuario
        cursor.execute("SELECT * FROM registros WHERE nombre = %s AND password = %s", (nombre, password))
        usuario = cursor.fetchone()

        cursor.close()
        conn.close()

        if usuario:
            return jsonify({"message": "Inicio de sesión exitoso"})
        else:
            return jsonify({"message": "Usuario o contraseña incorrectos"})

    return render_template('login.html')

@app.route('/bienvenida')
def bienvenida():
    return render_template('bienvenida.html')  

@app.route('/inicio')
def inicio():
    return render_template('inicio.html')  

@app.route('/reseñas', methods=['GET', 'POST'])
def reseñas():
    if request.method == 'POST':
        usuario = session.get('nombre', 'Anónimo')  # Nombre del usuario logueado desde el campo 'nombre' en sesión
        comentario = request.form['comentario']
        fecha = datetime.now().strftime('%Y-%m-%d %H:%M')

        conn = conexion.conectar()
        cursor = conn.cursor()
        
        query = "INSERT INTO comentarios (usuario, comentario, fecha) VALUES (%s, %s, %s)"
        cursor.execute(query, (usuario, comentario, fecha))
        conn.commit()
        
        cursor.close()
        conn.close()

        return redirect(url_for('reseñas'))

    conn = conexion.conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM comentarios ORDER BY fecha DESC")
    comentarios = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('reseñas.html', comentarios=comentarios)

@app.route('/portafolio')
def portafolio():
    return render_template('portafolio.html') 
@app.route('/usuarios')
def usuarios():
    conn = conexion.conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, nombre, apellido, telefono, email FROM registros")
    usuarios = cursor.fetchall()
    cursor.close()
    conn.close()  # Asegúrate de cerrar la conexión
    return render_template('usuarios.html', usuarios=usuarios) 

@app.route('/usuarios/editar', methods=['POST'])
def editar_usuario():
    data = request.json
    id = data.get('id')
    nombre = data.get('nombre')
    apellido = data.get('apellido')
    telefono = data.get('telefono')
    email = data.get('email')

    conn = conexion.conectar()
    cursor = conn.cursor()

    query = """
    UPDATE registros 
    SET nombre = %s, apellido = %s, telefono = %s, email = %s 
    WHERE id = %s
    """
    cursor.execute(query, (nombre, apellido, telefono, email, id))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Usuario actualizado con éxito"})

@app.route('/usuarios/eliminar', methods=['POST'])
def eliminar_usuario():
    data = request.json
    id = data.get('id')

    conn = conexion.conectar()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM registros WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Usuario eliminado con éxito"})

@app.route('/detalles')
def detalles():
    return render_template('detalles.html')  

from flask import redirect, url_for

@app.route('/reservar', methods=['POST'])
def reservar():
    nombre = request.form['nombre']
    correo = request.form['correo']
    fecha = request.form['fecha']
    hora = request.form['hora']
    servicio = request.form['servicio']
    nota = request.form.get('nota')  # Recoger la nota (puede ser vacía si no se envía)

    try:
        conn = conexion.conectar()
        cursor = conn.cursor()

        query = """
        INSERT INTO reservas (nombre, correo, fecha, hora, servicio, nota)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (nombre, correo, fecha, hora, servicio, nota))
        conn.commit()

        cursor.close()
        conn.close()

        # Redirigir a la página de inicio con un parámetro de éxito
        return redirect(url_for('inicio', mensaje='Cita reservada con éxito', tipo='success'))
    
    except Exception as e:
        print(f"Error al guardar la reserva: {e}")
        # Redirigir a la página de inicio con un mensaje de error
        return redirect(url_for('inicio', mensaje='Error al agendar la cita', tipo='error'))

if __name__ == '__main__':
    app.run(debug=True)
