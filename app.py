import sqlite3
import io
from flask import Flask, render_template, request, redirect, url_for, flash, make_response
from datetime import date
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DATABASE = 'C:/Users/amorelli/Desktop/cons/consultorio/clinica.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Rutas Principales
@app.route('/')
def index():
    return redirect(url_for('agenda'))

# Rutas para Pacientes
@app.route('/pacientes')
def list_pacientes():
    conn = get_db_connection()
    pacientes = conn.execute('SELECT * FROM pacientes ORDER BY apellido, nombre').fetchall()
    conn.close()
    return render_template('pacientes/list.html', pacientes=pacientes)

@app.route('/pacientes/new', methods=['GET', 'POST'])
def add_paciente():
    if request.method == 'POST':
        try:
            conn = get_db_connection()
            conn.execute("""
                INSERT INTO pacientes (nombre, apellido, dni, telefono, email, direccion, fecha_nacimiento, numero_afiliado)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                request.form['nombre'], request.form['apellido'], request.form['dni'],
                request.form['telefono'], request.form['email'], request.form['direccion'],
                request.form['fecha_nacimiento'], request.form['numero_afiliado']
            ))
            conn.commit()
            flash('Paciente agregado correctamente.', 'success')
        except sqlite3.IntegrityError:
            flash('Error: El DNI ingresado ya existe.', 'danger')
        except Exception as e:
            flash(f'Ocurrió un error al agregar el paciente: {e}', 'danger')
        finally:
            if conn:
                conn.close()
        return redirect(url_for('list_pacientes'))
    return render_template('pacientes/form.html', action="new", paciente=None)

@app.route('/pacientes/edit/<int:id>', methods=['GET', 'POST'])
def edit_paciente(id):
    conn = get_db_connection()
    paciente = conn.execute('SELECT * FROM pacientes WHERE id = ?', (id,)).fetchone()
    
    if request.method == 'POST':
        try:
            conn.execute("""
                UPDATE pacientes 
                SET nombre=?, apellido=?, dni=?, telefono=?, email=?, direccion=?, fecha_nacimiento=?, numero_afiliado=?
                WHERE id=?
            """, (
                request.form['nombre'], request.form['apellido'], request.form['dni'],
                request.form['telefono'], request.form['email'], request.form['direccion'],
                request.form['fecha_nacimiento'], request.form['numero_afiliado'], id
            ))
            conn.commit()
            flash('Paciente actualizado correctamente.', 'success')
        except sqlite3.IntegrityError:
            flash('Error: El DNI ingresado ya pertenece a otro paciente.', 'danger')
        except Exception as e:
            flash(f'Ocurrió un error al actualizar el paciente: {e}', 'danger')
        finally:
            if conn:
                conn.close()
        return redirect(url_for('list_pacientes'))

    if paciente is None:
        conn.close()
        flash('No se encontró el paciente.', 'warning')
        return redirect(url_for('list_pacientes'))
    
    conn.close()
    return render_template('pacientes/form.html', action="edit", paciente=paciente)

@app.route('/pacientes/delete/<int:id>', methods=['POST'])
def delete_paciente(id):
    try:
        conn = get_db_connection()
        conn.execute('DELETE FROM pacientes WHERE id = ?', (id,))
        conn.commit()
        flash('Paciente eliminado correctamente.', 'success')
    except Exception as e:
        flash(f'Ocurrió un error al eliminar el paciente: {e}', 'danger')
    finally:
        if conn:
            conn.close()
    return redirect(url_for('list_pacientes'))

@app.route('/pacientes/search', methods=['POST'])
def search_paciente():
    search_term = request.form.get('search_term', '')
    if not search_term:
        return redirect(url_for('list_pacientes'))
    
    conn = get_db_connection()
    query = "%" + search_term + "%"
    pacientes = conn.execute(
        'SELECT * FROM pacientes WHERE nombre LIKE ? OR apellido LIKE ? OR dni LIKE ? ORDER BY apellido, nombre',
        (query, query, query)
    ).fetchall()
    conn.close()
    
    if not pacientes:
        flash(f"No se encontraron pacientes con el término '{search_term}'.", 'warning')
        return redirect(url_for('list_pacientes'))

    return render_template('pacientes/list.html', pacientes=pacientes)

# Rutas para Profesionales
@app.route('/profesionales')
def list_profesionales():
    conn = get_db_connection()
    profesionales = conn.execute('SELECT * FROM profesionales ORDER BY apellido, nombre').fetchall()
    conn.close()
    return render_template('profesionales/list.html', profesionales=profesionales)

@app.route('/profesionales/new', methods=['GET', 'POST'])
def add_profesional():
    if request.method == 'POST':
        try:
            conn = get_db_connection()
            conn.execute("""
                INSERT INTO profesionales (nombre, apellido, especialidad, matricula, telefono, email, honorarios)
                VALUES (?, ?, ?, ?, ?, ?, ?)""", 
                (request.form['nombre'], request.form['apellido'], request.form['especialidad'], 
                 request.form['matricula'], request.form['telefono'], request.form['email'], request.form['honorarios']))
            conn.commit()
            flash('Profesional agregado correctamente.', 'success')
        except sqlite3.IntegrityError:
            flash('Error: La matrícula ingresada ya existe.', 'danger')
        except Exception as e:
            flash(f'Ocurrió un error al agregar el profesional: {e}', 'danger')
        finally:
            if conn:
                conn.close()
        return redirect(url_for('list_profesionales'))
    return render_template('profesionales/form.html', action="new", profesional=None)

@app.route('/profesionales/edit/<int:id>', methods=['GET', 'POST'])
def edit_profesional(id):
    conn = get_db_connection()
    profesional = conn.execute('SELECT * FROM profesionales WHERE id = ?', (id,)).fetchone()

    if request.method == 'POST':
        try:
            conn.execute("""
                UPDATE profesionales 
                SET nombre=?, apellido=?, especialidad=?, matricula=?, telefono=?, email=?, honorarios=?
                WHERE id=?""", 
                (request.form['nombre'], request.form['apellido'], request.form['especialidad'], 
                 request.form['matricula'], request.form['telefono'], request.form['email'], 
                 request.form['honorarios'], id))
            conn.commit()
            flash('Profesional actualizado correctamente.', 'success')
        except sqlite3.IntegrityError:
            flash('Error: La matrícula ingresada ya pertenece a otro profesional.', 'danger')
        except Exception as e:
            flash(f'Ocurrió un error al actualizar el profesional: {e}', 'danger')
        finally:
            if conn:
                conn.close()
        return redirect(url_for('list_profesionales'))

    if profesional is None:
        conn.close()
        flash('No se encontró el profesional.', 'warning')
        return redirect(url_for('list_profesionales'))
        
    conn.close()
    return render_template('profesionales/form.html', action="edit", profesional=profesional)

@app.route('/profesionales/delete/<int:id>', methods=['POST'])
def delete_profesional(id):
    try:
        conn = get_db_connection()
        conn.execute('DELETE FROM profesionales WHERE id = ?', (id,))
        conn.commit()
        flash('Profesional eliminado correctamente.', 'success')
    except Exception as e:
        flash(f'Ocurrió un error al eliminar el profesional: {e}', 'danger')
    finally:
        if conn:
            conn.close()
    return redirect(url_for('list_profesionales'))

@app.route('/profesionales/search', methods=['POST'])
def search_profesional():
    search_term = request.form.get('search_term', '')
    if not search_term:
        return redirect(url_for('list_profesionales'))
    
    conn = get_db_connection()
    query = "%" + search_term + "%"
    profesionales = conn.execute("""
        SELECT * FROM profesionales 
        WHERE nombre LIKE ? OR apellido LIKE ? OR especialidad LIKE ? OR matricula LIKE ?
        ORDER BY apellido, nombre""", (query, query, query, query)).fetchall()
    conn.close()
    
    if not profesionales:
        flash(f"No se encontraron profesionales con el término '{search_term}'.", 'warning')
        return redirect(url_for('list_profesionales'))

    return render_template('profesionales/list.html', profesionales=profesionales)

# Rutas para Obras Sociales
@app.route('/obras_sociales')
def list_obras_sociales():
    conn = get_db_connection()
    obras_sociales = conn.execute('SELECT * FROM obras_sociales ORDER BY nombre').fetchall()
    conn.close()
    return render_template('obras_sociales/list.html', obras_sociales=obras_sociales)

@app.route('/obras_sociales/new', methods=['GET', 'POST'])
def add_obra_social():
    if request.method == 'POST':
        try:
            conn = get_db_connection()
            conn.execute("""
                INSERT INTO obras_sociales (nombre, codigo, telefono, email, direccion)
                VALUES (?, ?, ?, ?, ?)""", 
                (request.form['nombre'], request.form['codigo'], request.form['telefono'], 
                 request.form['email'], request.form['direccion']))
            conn.commit()
            flash('Obra Social agregada correctamente.', 'success')
        except sqlite3.IntegrityError:
            flash('Error: El código de la Obra Social ya existe.', 'danger')
        except Exception as e:
            flash(f'Ocurrió un error al agregar la Obra Social: {e}', 'danger')
        finally:
            if conn:
                conn.close()
        return redirect(url_for('list_obras_sociales'))
    return render_template('obras_sociales/form.html', action="new", obra_social=None)

@app.route('/obras_sociales/edit/<int:id>', methods=['GET', 'POST'])
def edit_obra_social(id):
    conn = get_db_connection()
    obra_social = conn.execute('SELECT * FROM obras_sociales WHERE id = ?', (id,)).fetchone()

    if request.method == 'POST':
        try:
            conn.execute("""
                UPDATE obras_sociales 
                SET nombre=?, codigo=?, telefono=?, email=?, direccion=?
                WHERE id=?""", 
                (request.form['nombre'], request.form['codigo'], request.form['telefono'], 
                 request.form['email'], request.form['direccion'], id))
            conn.commit()
            flash('Obra Social actualizada correctamente.', 'success')
        except sqlite3.IntegrityError:
            flash('Error: El código de la Obra Social ya pertenece a otra entidad.', 'danger')
        except Exception as e:
            flash(f'Ocurrió un error al actualizar la Obra Social: {e}', 'danger')
        finally:
            if conn:
                conn.close()
        return redirect(url_for('list_obras_sociales'))

    if obra_social is None:
        conn.close()
        flash('No se encontró la Obra Social.', 'warning')
        return redirect(url_for('list_obras_sociales'))
        
    conn.close()
    return render_template('obras_sociales/form.html', action="edit", obra_social=obra_social)

@app.route('/obras_sociales/delete/<int:id>', methods=['POST'])
def delete_obra_social(id):
    try:
        conn = get_db_connection()
        conn.execute('DELETE FROM obras_sociales WHERE id = ?', (id,))
        conn.commit()
        flash('Obra Social eliminada correctamente.', 'success')
    except Exception as e:
        flash(f'Ocurrió un error al eliminar la Obra Social: {e}', 'danger')
    finally:
        if conn:
            conn.close()
    return redirect(url_for('list_obras_sociales'))

@app.route('/obras_sociales/search', methods=['POST'])
def search_obra_social():
    search_term = request.form.get('search_term', '')
    if not search_term:
        return redirect(url_for('list_obras_sociales'))
    
    conn = get_db_connection()
    query = "%" + search_term + "%"
    obras_sociales = conn.execute(
        'SELECT * FROM obras_sociales WHERE nombre LIKE ? OR codigo LIKE ? ORDER BY nombre',
        (query, query)
    ).fetchall()
    conn.close()
    
    if not obras_sociales:
        flash(f"No se encontraron Obras Sociales con el término '{search_term}'.", 'warning')
        return redirect(url_for('list_obras_sociales'))

    return render_template('obras_sociales/list.html', obras_sociales=obras_sociales)

# Rutas para Servicios
@app.route('/servicios')
def list_servicios():
    conn = get_db_connection()
    servicios = conn.execute("""
        SELECT s.id, s.codigo, s.descripcion, s.precio, COALESCE(os.nombre, 'N/A') as obra_social_nombre
        FROM servicios s
        LEFT JOIN obras_sociales os ON s.obra_social_id = os.id
        ORDER BY s.descripcion
    """).fetchall()
    conn.close()
    return render_template('servicios/list.html', servicios=servicios)

@app.route('/servicios/new', methods=['GET', 'POST'])
def add_servicio():
    conn = get_db_connection()
    obras_sociales = conn.execute('SELECT * FROM obras_sociales ORDER BY nombre').fetchall()
    
    if request.method == 'POST':
        try:
            obra_social_id = request.form.get('obra_social_id')
            if not obra_social_id or obra_social_id == 'None':
                obra_social_id = None

            conn.execute("""
                INSERT INTO servicios (codigo, descripcion, precio, obra_social_id)
                VALUES (?, ?, ?, ?)""", 
                (request.form['codigo'], request.form['descripcion'], request.form['precio'], obra_social_id))
            conn.commit()
            flash('Servicio agregado correctamente.', 'success')
        except sqlite3.IntegrityError:
            flash('Error: El código del servicio ya existe.', 'danger')
        except Exception as e:
            flash(f'Ocurrió un error al agregar el servicio: {e}', 'danger')
        finally:
            if conn:
                conn.close()
        return redirect(url_for('list_servicios'))

    conn.close()
    return render_template('servicios/form.html', action="new", servicio=None, obras_sociales=obras_sociales)

@app.route('/servicios/edit/<int:id>', methods=['GET', 'POST'])
def edit_servicio(id):
    conn = get_db_connection()
    servicio = conn.execute('SELECT * FROM servicios WHERE id = ?', (id,)).fetchone()
    obras_sociales = conn.execute('SELECT * FROM obras_sociales ORDER BY nombre').fetchall()

    if request.method == 'POST':
        try:
            obra_social_id = request.form.get('obra_social_id')
            if not obra_social_id or obra_social_id == 'None':
                obra_social_id = None

            conn.execute("""
                UPDATE servicios SET codigo=?, descripcion=?, precio=?, obra_social_id=?
                WHERE id=?""", 
                (request.form['codigo'], request.form['descripcion'], request.form['precio'], obra_social_id, id))
            conn.commit()
            flash('Servicio actualizado correctamente.', 'success')
        except sqlite3.IntegrityError:
            flash('Error: El código del servicio ya pertenece a otro servicio.', 'danger')
        except Exception as e:
            flash(f'Ocurrió un error al actualizar el servicio: {e}', 'danger')
        finally:
            if conn:
                conn.close()
        return redirect(url_for('list_servicios'))

    if servicio is None:
        conn.close()
        flash('No se encontró el servicio.', 'warning')
        return redirect(url_for('list_servicios'))
        
    conn.close()
    return render_template('servicios/form.html', action="edit", servicio=servicio, obras_sociales=obras_sociales)

@app.route('/servicios/delete/<int:id>', methods=['POST'])
def delete_servicio(id):
    try:
        conn = get_db_connection()
        conn.execute('DELETE FROM servicios WHERE id = ?', (id,))
        conn.commit()
        flash('Servicio eliminado correctamente.', 'success')
    except Exception as e:
        flash(f'Ocurrió un error al eliminar el servicio: {e}', 'danger')
    finally:
        if conn:
            conn.close()
    return redirect(url_for('list_servicios'))

@app.route('/servicios/search', methods=['POST'])
def search_servicio():
    search_term = request.form.get('search_term', '')
    if not search_term:
        return redirect(url_for('list_servicios'))
    
    conn = get_db_connection()
    query = "%" + search_term + "%"
    servicios = conn.execute("""
        SELECT s.id, s.codigo, s.descripcion, s.precio, COALESCE(os.nombre, 'N/A') as obra_social_nombre
        FROM servicios s
        LEFT JOIN obras_sociales os ON s.obra_social_id = os.id
        WHERE s.descripcion LIKE ? OR s.codigo LIKE ?
        ORDER BY s.descripcion
    """, (query, query)).fetchall()
    conn.close()
    
    if not servicios:
        flash(f"No se encontraron servicios con el término '{search_term}'.", 'warning')
        return redirect(url_for('list_servicios'))

    return render_template('servicios/list.html', servicios=servicios)

# Rutas para Turnos
@app.route('/turnos')
def list_turnos():
    conn = get_db_connection()
    turnos = conn.execute("""
        SELECT t.id, t.fecha, t.hora, t.estado, t.observaciones,
               p.nombre as paciente_nombre, p.apellido as paciente_apellido,
               pr.nombre as profesional_nombre, pr.apellido as profesional_apellido
        FROM turnos t
        JOIN pacientes p ON t.paciente_id = p.id
        JOIN profesionales pr ON t.profesional_id = pr.id
        ORDER BY t.fecha, t.hora
    """).fetchall()
    conn.close()
    return render_template('turnos/list.html', turnos=turnos)

@app.route('/turnos/new', methods=['GET', 'POST'])
def add_turno():
    conn = get_db_connection()
    pacientes = conn.execute('SELECT id, nombre, apellido FROM pacientes ORDER BY apellido, nombre').fetchall()
    profesionales = conn.execute('SELECT id, nombre, apellido FROM profesionales ORDER BY apellido, nombre').fetchall()

    if request.method == 'POST':
        try:
            profesional_id = request.form['profesional_id']
            fecha = request.form['fecha']
            hora = request.form['hora']

            # Validar duplicados
            existe = conn.execute(
                'SELECT id FROM turnos WHERE profesional_id = ? AND fecha = ? AND hora = ?',
                (profesional_id, fecha, hora)
            ).fetchone()

            if existe:
                flash('Error: Ya existe un turno para este profesional en la misma fecha y hora.', 'danger')
                conn.close()
                return render_template('turnos/form.html', action="new", turno=None, pacientes=pacientes, profesionales=profesionales)
            else:
                conn.execute("""
                    INSERT INTO turnos (paciente_id, profesional_id, fecha, hora, estado, observaciones)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    (request.form['paciente_id'], profesional_id, fecha, hora, 
                     request.form['estado'], request.form['observaciones']))
                conn.commit()
                flash('Turno agregado correctamente.', 'success')
                conn.close()
                return redirect(url_for('list_turnos'))

        except Exception as e:
            flash(f'Ocurrió un error al agregar el turno: {e}', 'danger')
            if conn:
                conn.close()
        return redirect(url_for('add_turno'))

    conn.close()
    return render_template('turnos/form.html', action="new", turno=None, pacientes=pacientes, profesionales=profesionales)

@app.route('/turnos/edit/<int:id>', methods=['GET', 'POST'])
def edit_turno(id):
    conn = get_db_connection()
    turno = conn.execute('SELECT * FROM turnos WHERE id = ?', (id,)).fetchone()
    pacientes = conn.execute('SELECT id, nombre, apellido FROM pacientes ORDER BY apellido, nombre').fetchall()
    profesionales = conn.execute('SELECT id, nombre, apellido FROM profesionales ORDER BY apellido, nombre').fetchall()

    if request.method == 'POST':
        try:
            profesional_id = request.form['profesional_id']
            fecha = request.form['fecha']
            hora = request.form['hora']

            # Validar duplicados (excluyendo el turno actual)
            existe = conn.execute(
                'SELECT id FROM turnos WHERE profesional_id = ? AND fecha = ? AND hora = ? AND id != ?',
                (profesional_id, fecha, hora, id)
            ).fetchone()

            if existe:
                flash('Error: Ya existe otro turno para este profesional en la misma fecha y hora.', 'danger')
                conn.close()
                return render_template('turnos/form.html', action="edit", turno=turno, pacientes=pacientes, profesionales=profesionales)
            else:
                conn.execute("""
                    UPDATE turnos SET paciente_id=?, profesional_id=?, fecha=?, hora=?, estado=?, observaciones=?
                    WHERE id=?""",
                    (request.form['paciente_id'], profesional_id, fecha, hora, 
                     request.form['estado'], request.form['observaciones'], id))
                conn.commit()
                flash('Turno actualizado correctamente.', 'success')
                conn.close()
                return redirect(url_for('list_turnos'))

        except Exception as e:
            flash(f'Ocurrió un error al actualizar el turno: {e}', 'danger')
            if conn:
                conn.close()
        return redirect(url_for('edit_turno', id=id))

    if turno is None:
        conn.close()
        flash('No se encontró el turno.', 'warning')
        return redirect(url_for('list_turnos'))

    conn.close()
    return render_template('turnos/form.html', action="edit", turno=turno, pacientes=pacientes, profesionales=profesionales)

@app.route('/turnos/delete/<int:id>', methods=['POST'])
def delete_turno(id):
    try:
        conn = get_db_connection()
        conn.execute('DELETE FROM turnos WHERE id = ?', (id,))
        conn.commit()
        flash('Turno eliminado correctamente.', 'success')
    except Exception as e:
        flash(f'Ocurrió un error al eliminar el turno: {e}', 'danger')
    finally:
        if conn:
            conn.close()
    return redirect(url_for('list_turnos'))

# Rutas para Agenda
@app.route('/agenda', methods=['GET', 'POST'])
def agenda():
    conn = get_db_connection()
    
    if request.method == 'POST':
        selected_date = request.form.get('selected_date')
    else:
        selected_date = date.today().isoformat()

    turnos = conn.execute("""
        SELECT t.id, t.fecha, t.hora, t.estado, t.observaciones,
               p.nombre as paciente_nombre, p.apellido as paciente_apellido,
               pr.nombre as profesional_nombre, pr.apellido as profesional_apellido
        FROM turnos t
        JOIN pacientes p ON t.paciente_id = p.id
        JOIN profesionales pr ON t.profesional_id = pr.id
        WHERE t.fecha = ?
        ORDER BY t.hora
    """, (selected_date,)).fetchall()
    
    conn.close()
    return render_template('agenda/view.html', turnos=turnos, selected_date=selected_date)

# Rutas para Facturas
@app.route('/facturas')
def list_facturas():
    conn = get_db_connection()
    facturas = conn.execute("""
        SELECT f.id, f.numero, f.fecha, f.total, f.estado,
               p.nombre as paciente_nombre, p.apellido as paciente_apellido
        FROM facturas f
        JOIN pacientes p ON f.paciente_id = p.id
        ORDER BY f.numero DESC
    """).fetchall()
    conn.close()
    return render_template('facturas/list.html', facturas=facturas)

@app.route('/facturas/view/<int:id>')
def view_factura(id):
    conn = get_db_connection()
    factura = conn.execute("""
        SELECT f.*, p.nombre as paciente_nombre, p.apellido as paciente_apellido, p.dni, p.direccion,
               COALESCE(os.nombre, 'Particular') as obra_social_nombre
        FROM facturas f
        JOIN pacientes p ON f.paciente_id = p.id
        LEFT JOIN obras_sociales os ON f.obra_social_id = os.id
        WHERE f.id = ?
    """, (id,)).fetchone()
    
    detalles = conn.execute("""
        SELECT d.id, d.cantidad, d.precio_unitario, d.subtotal, s.descripcion
        FROM detalle_facturas d
        JOIN servicios s ON d.servicio_id = s.id
        WHERE d.factura_id = ?
    """, (id,)).fetchall()
    conn.close()

    if factura is None:
        flash('Factura no encontrada.', 'warning')
        return redirect(url_for('list_facturas'))

    return render_template('facturas/view.html', factura=factura, detalles=detalles)

@app.route('/facturas/new', methods=['GET', 'POST'])
def new_factura():
    conn = get_db_connection()
    if request.method == 'POST':
        try:
            paciente_id = request.form['paciente_id']
            obra_social_id = request.form.get('obra_social_id')
            if not obra_social_id or obra_social_id == 'None':
                obra_social_id = None

            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO facturas (numero, paciente_id, obra_social_id, fecha, total, estado)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (request.form['numero'], paciente_id, obra_social_id, date.today().isoformat(), 0, 'Pendiente'))
            
            factura_id = cursor.lastrowid
            conn.commit()
            flash('Factura creada. Ahora puede agregar servicios.', 'success')
            return redirect(url_for('edit_factura', id=factura_id))
        except sqlite3.IntegrityError:
            flash('Error: El número de factura ya existe.', 'danger')
        except Exception as e:
            flash(f'Ocurrió un error al crear la factura: {e}', 'danger')
        finally:
            if conn:
                conn.close()
        return redirect(url_for('new_factura'))

    pacientes = conn.execute('SELECT * FROM pacientes ORDER BY apellido, nombre').fetchall()
    obras_sociales = conn.execute('SELECT * FROM obras_sociales ORDER BY nombre').fetchall()
    conn.close()
    return render_template('facturas/form.html', pacientes=pacientes, obras_sociales=obras_sociales)


@app.route('/facturas/edit/<int:id>', methods=['GET', 'POST'])
def edit_factura(id):
    conn = get_db_connection()
    
    if request.method == 'POST': # Actualizar estado
        try:
            nuevo_estado = request.form.get('estado')
            conn.execute('UPDATE facturas SET estado = ? WHERE id = ?', (nuevo_estado, id))
            conn.commit()
            flash('Estado de la factura actualizado.', 'success')
        except Exception as e:
            flash(f'Error al actualizar el estado: {e}', 'danger')
        finally:
            if conn:
                conn.close()
        return redirect(url_for('edit_factura', id=id))

    factura = conn.execute('SELECT * FROM facturas WHERE id = ?', (id,)).fetchone()
    detalles = conn.execute("""
        SELECT d.id, d.cantidad, d.precio_unitario, d.subtotal, s.descripcion
        FROM detalle_facturas d JOIN servicios s ON d.servicio_id = s.id
        WHERE d.factura_id = ?
    """, (id,)).fetchall()
    servicios = conn.execute('SELECT * FROM servicios ORDER BY descripcion').fetchall()
    conn.close()

    if factura is None:
        flash('Factura no encontrada.', 'warning')
        return redirect(url_for('list_facturas'))

    return render_template('facturas/edit.html', factura=factura, detalles=detalles, servicios=servicios)


@app.route('/facturas/<int:id>/add_item', methods=['POST'])
def add_item_to_factura(id):
    try:
        conn = get_db_connection()
        servicio_id = request.form['servicio_id']
        cantidad = int(request.form['cantidad'])
        
        servicio = conn.execute('SELECT * FROM servicios WHERE id = ?', (servicio_id,)).fetchone()
        precio_unitario = servicio['precio']
        subtotal = cantidad * precio_unitario

        conn.execute("""
            INSERT INTO detalle_facturas (factura_id, servicio_id, cantidad, precio_unitario, subtotal)
            VALUES (?, ?, ?, ?, ?)
        """, (id, servicio_id, cantidad, precio_unitario, subtotal))
        
        conn.execute('UPDATE facturas SET total = total + ? WHERE id = ?', (subtotal, id))
        conn.commit()
        flash('Servicio agregado a la factura.', 'success')
    except Exception as e:
        flash(f'Error al agregar el servicio: {e}', 'danger')
    finally:
        if conn:
            conn.close()
    return redirect(url_for('edit_factura', id=id))

@app.route('/facturas/delete_item/<int:item_id>', methods=['POST'])
def delete_item_from_factura(item_id):
    factura_id = None
    try:
        conn = get_db_connection()
        item = conn.execute('SELECT * FROM detalle_facturas WHERE id = ?', (item_id,)).fetchone()
        if item:
            factura_id = item['factura_id']
            subtotal = item['subtotal']

            conn.execute('DELETE FROM detalle_facturas WHERE id = ?', (item_id,))
            conn.execute('UPDATE facturas SET total = total - ? WHERE id = ?', (subtotal, factura_id))
            conn.commit()
            flash('Servicio eliminado de la factura.', 'success')
    except Exception as e:
        flash(f'Error al eliminar el servicio: {e}', 'danger')
    finally:
        if conn:
            conn.close()
    
    if factura_id:
        return redirect(url_for('edit_factura', id=factura_id))
    return redirect(url_for('list_facturas'))

@app.route('/facturas/<int:id>/pdf')
def generate_factura_pdf(id):
    conn = get_db_connection()
    factura = conn.execute("""
        SELECT f.*, p.nombre as paciente_nombre, p.apellido as paciente_apellido, p.dni, p.direccion,
               COALESCE(os.nombre, 'Particular') as obra_social_nombre
        FROM facturas f
        JOIN pacientes p ON f.paciente_id = p.id
        LEFT JOIN obras_sociales os ON f.obra_social_id = os.id
        WHERE f.id = ?
    """, (id,)).fetchone()
    
    detalles = conn.execute("""
        SELECT d.cantidad, d.precio_unitario, d.subtotal, s.descripcion
        FROM detalle_facturas d
        JOIN servicios s ON d.servicio_id = s.id
        WHERE d.factura_id = ?
    """, (id,)).fetchall()
    conn.close()

    if not factura:
        flash('Factura no encontrada.', 'warning')
        return redirect(url_for('list_facturas'))

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Contenido del PDF
    c.setFont("Helvetica-Bold", 16)
    c.drawString(250, height - 50, "FACTURA")

    c.setFont("Helvetica", 10)
    c.drawString(50, height - 80, f"Fecha: {factura['fecha']}")
    c.drawString(400, height - 80, f"Factura N°: {factura['numero']}")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 120, "Paciente:")
    c.setFont("Helvetica", 10)
    c.drawString(70, height - 135, f"{factura['paciente_apellido']}, {factura['paciente_nombre']}")
    c.drawString(70, height - 150, f"DNI: {factura['dni']}")
    c.drawString(70, height - 165, f"Dirección: {factura['direccion']}")
    c.drawString(70, height - 180, f"Obra Social: {factura['obra_social_nombre']}")

    y = height - 220
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y, "Descripción")
    c.drawString(300, y, "Cantidad")
    c.drawString(400, y, "P. Unitario")
    c.drawString(500, y, "Subtotal")
    c.line(50, y - 5, width - 50, y - 5)
    y -= 20

    c.setFont("Helvetica", 10)
    for item in detalles:
        c.drawString(50, y, item['descripcion'])
        c.drawString(300, y, str(item['cantidad']))
        c.drawString(400, y, f"${item['precio_unitario']:.2f}")
        c.drawString(500, y, f"${item['subtotal']:.2f}")
        y -= 15

    c.line(400, y, width - 50, y)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(400, y - 20, "TOTAL:")
    c.drawString(500, y - 20, f"${factura['total']:.2f}")

    c.save()
    buffer.seek(0)

    response = make_response(buffer.getvalue())
    response.mimetype = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=factura_{factura["numero"]}.pdf'
    return response

if __name__ == '__main__':
    app.run(debug=True)