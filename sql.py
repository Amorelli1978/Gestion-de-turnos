import sqlite3
from datetime import datetime, date, timedelta

def insert_sample_data():
    """Inserta datos de ejemplo en la base de datos"""
    conn = sqlite3.connect("clinica.db")
    cursor = conn.cursor()
    
    try:
        # Obras Sociales
        obras_sociales = [
            ("OSDE", "OSDE001", "011-4444-5555", "info@osde.com.ar", "Av. Corrientes 1234"),
            ("Swiss Medical", "SM002", "011-5555-6666", "contacto@swissmedical.com.ar", "Av. Santa Fe 5678"),
            ("Galeno", "GAL003", "011-6666-7777", "info@galeno.com.ar", "Av. Rivadavia 9012"),
            ("IOMA", "IOMA004", "011-7777-8888", "consultas@ioma.gba.gov.ar", "Calle 7 N° 877")
        ]
        
        for obra in obras_sociales:
            cursor.execute('''
                INSERT OR IGNORE INTO obras_sociales (nombre, codigo, telefono, email, direccion)
                VALUES (?, ?, ?, ?, ?)
            ''', obra)
        
        # Profesionales
        profesionales = [
            ("Juan", "Pérez", "Cardiología", "MP12345", "011-1111-2222", "jperez@email.com", 15000.00),
            ("María", "González", "Dermatología", "MP23456", "011-2222-3333", "mgonzalez@email.com", 12000.00),
            ("Carlos", "Rodríguez", "Traumatología", "MP34567", "011-3333-4444", "crodriguez@email.com", 18000.00),
            ("Ana", "Martínez", "Pediatría", "MP45678", "011-4444-5555", "amartinez@email.com", 14000.00),
            ("Luis", "López", "Neurología", "MP56789", "011-5555-6666", "llopez@email.com", 20000.00)
        ]
        
        for prof in profesionales:
            cursor.execute('''
                INSERT OR IGNORE INTO profesionales (nombre, apellido, especialidad, matricula, telefono, email, honorarios)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', prof)
        
        # Pacientes
        pacientes = [
            ("Roberto", "Silva", "12345678", "011-1234-5678", "rsilva@email.com", "Av. Libertador 1234", "1980-05-15", 1, "123456"),
            ("Laura", "Fernández", "23456789", "011-2345-6789", "lfernandez@email.com", "Calle Falsa 123", "1975-08-22", 2, "234567"),
            ("Miguel", "Torres", "34567890", "011-3456-7890", "mtorres@email.com", "Av. Corrientes 5678", "1990-12-10", 1, "345678"),
            ("Carmen", "Ruiz", "45678901", "011-4567-8901", "cruiz@email.com", "San Martín 987", "1985-03-18", 3, "456789"),
            ("Diego", "Morales", "56789012", "011-5678-9012", "dmorales@email.com", "Belgrano 456", "1992-07-25", None, None),
            ("Sofía", "Herrera", "67890123", "011-6789-0123", "sherrera@email.com", "Rivadavia 789", "1988-11-30", 2, "567890")
        ]
        
        for pac in pacientes:
            cursor.execute('''
                INSERT OR IGNORE INTO pacientes (nombre, apellido, dni, telefono, email, direccion, fecha_nacimiento, obra_social_id, numero_afiliado)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', pac)
        
        # Servicios
        servicios = [
            ("CONS001", "Consulta Cardiológica", 8000.00, 1),
            ("CONS002", "Consulta Dermatológica", 6000.00, 1),
            ("CONS003", "Consulta Traumatológica", 7000.00, 2),
            ("CONS004", "Consulta Pediátrica", 5500.00, 2),
            ("ECG001", "Electrocardiograma", 3000.00, 1),
            ("ECO001", "Ecocardiograma", 12000.00, 1),
            ("RX001", "Radiografía Simple", 4000.00, None),
            ("LAB001", "Análisis de Sangre Completo", 5000.00, None),
            ("CONS005", "Consulta Neurológica", 9000.00, 3),
            ("RMN001", "Resonancia Magnética", 25000.00, 3)
        ]
        
        for serv in servicios:
            cursor.execute('''
                INSERT OR IGNORE INTO servicios (codigo, descripcion, precio, obra_social_id)
                VALUES (?, ?, ?, ?)
            ''', serv)
        
        # Turnos (próximos días)
        today = date.today()
        turnos = [
            (1, 1, today + timedelta(days=1), "09:00", "Programado", "Control rutinario"),
            (2, 2, today + timedelta(days=1), "10:30", "Confirmado", "Revisión lunar"),
            (3, 3, today + timedelta(days=2), "14:00", "Programado", "Dolor en rodilla"),
            (4, 4, today + timedelta(days=2), "16:30", "Programado", "Control niño sano"),
            (5, 5, today + timedelta(days=3), "11:00", "Confirmado", "Seguimiento neurológico"),
            (6, 1, today + timedelta(days=3), "15:00", "Programado", "Consulta por hipertensión"),
            (1, 2, today + timedelta(days=4), "09:30", "Programado", "Consulta dermatológica"),
            (2, 3, today + timedelta(days=4), "11:30", "Confirmado", "Rehabilitación"),
            (3, 4, today + timedelta(days=5), "10:00", "Programado", "Vacunación"),
            (4, 5, today + timedelta(days=5), "14:30", "Programado", "Consulta neurológica")
        ]
        
        for turno in turnos:
            cursor.execute('''
                INSERT OR IGNORE INTO turnos (paciente_id, profesional_id, fecha, hora, estado, observaciones)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', turno)
        
        # Facturas de ejemplo
        facturas = [
            ("FAC001", 1, 1, today - timedelta(days=5), 11000.00, "Pagada"),
            ("FAC002", 2, 2, today - timedelta(days=3), 6000.00, "Pendiente"),
            ("FAC003", 3, 1, today - timedelta(days=2), 15000.00, "Pagada"),
            ("FAC004", 5, None, today - timedelta(days=1), 9000.00, "Pendiente")
        ]
        
        for fact in facturas:
            cursor.execute('''
                INSERT OR IGNORE INTO facturas (numero, paciente_id, obra_social_id, fecha, total, estado)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', fact)
        
        # Detalles de facturas
        detalles = [
            (1, 1, 1, 8000.00, 8000.00),  # FAC001: Consulta Cardiológica
            (1, 5, 1, 3000.00, 3000.00),  # FAC001: ECG
            (2, 2, 1, 6000.00, 6000.00),  # FAC002: Consulta Dermatológica
            (3, 1, 1, 8000.00, 8000.00),  # FAC003: Consulta Cardiológica
            (3, 6, 1, 12000.00, 12000.00), # FAC003: Ecocardiograma (error en total, debería ser 20000)
            (4, 9, 1, 9000.00, 9000.00)   # FAC004: Consulta Neurológica
        ]
        
        for det in detalles:
            cursor.execute('''
                INSERT OR IGNORE INTO detalle_facturas (factura_id, servicio_id, cantidad, precio_unitario, subtotal)
                VALUES (?, ?, ?, ?, ?)
            ''', det)
        
        # Corregir el total de la factura 3
        cursor.execute("UPDATE facturas SET total = 20000.00 WHERE id = 3")
        
        conn.commit()
        print("Datos de ejemplo insertados correctamente")
        
    except Exception as e:
        print(f"Error al insertar datos de ejemplo: {e}")
        conn.rollback()
    
    finally:
        conn.close()

if __name__ == "__main__":
    insert_sample_data()