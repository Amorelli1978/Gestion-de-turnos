import sys
import sqlite3
from datetime import datetime, date, time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QTabWidget, QTableWidget, QTableWidgetItem,
                           QPushButton, QLineEdit, QLabel, QFormLayout, QMessageBox,
                           QDateEdit, QTimeEdit, QComboBox, QTextEdit, QSpinBox,
                           QDoubleSpinBox, QHeaderView, QDialog, QDialogButtonBox,
                           QCalendarWidget, QListWidget, QGroupBox, QGridLayout)
from PyQt5.QtCore import Qt, QDate, QTime, QTimer
from PyQt5.QtGui import QFont, QIcon

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QDateEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox,
    QTextEdit, QSpinBox
)
from PyQt5.QtCore import QDate
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os


class DatabaseManager:
    def __init__(self, db_name="clinica.db"):
        self.db_name = db_name
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_name)
    
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabla Pacientes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pacientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                apellido TEXT NOT NULL,
                dni TEXT UNIQUE NOT NULL,
                telefono TEXT,
                email TEXT,
                direccion TEXT,
                fecha_nacimiento DATE,
                obra_social_id INTEGER,
                numero_afiliado TEXT,
                FOREIGN KEY (obra_social_id) REFERENCES obras_sociales (id)
            )
        ''')
        
        # Tabla Profesionales
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS profesionales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                apellido TEXT NOT NULL,
                especialidad TEXT NOT NULL,
                matricula TEXT UNIQUE NOT NULL,
                telefono TEXT,
                email TEXT,
                honorarios REAL DEFAULT 0
            )
        ''')
        
        # Tabla Obras Sociales
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS obras_sociales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                codigo TEXT UNIQUE,
                telefono TEXT,
                email TEXT,
                direccion TEXT
            )
        ''')
        
        # Tabla Servicios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS servicios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT UNIQUE NOT NULL,
                descripcion TEXT NOT NULL,
                precio REAL NOT NULL,
                obra_social_id INTEGER,
                FOREIGN KEY (obra_social_id) REFERENCES obras_sociales (id)
            )
        ''')
        
        # Tabla Turnos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS turnos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paciente_id INTEGER NOT NULL,
                profesional_id INTEGER NOT NULL,
                fecha DATE NOT NULL,
                hora TIME NOT NULL,
                estado TEXT DEFAULT 'Programado',
                observaciones TEXT,
                FOREIGN KEY (paciente_id) REFERENCES pacientes (id),
                FOREIGN KEY (profesional_id) REFERENCES profesionales (id)
            )
        ''')
        
        # Tabla Facturas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS facturas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero TEXT UNIQUE NOT NULL,
                paciente_id INTEGER NOT NULL,
                obra_social_id INTEGER,
                fecha DATE NOT NULL,
                total REAL NOT NULL,
                estado TEXT DEFAULT 'Pendiente',
                FOREIGN KEY (paciente_id) REFERENCES pacientes (id),
                FOREIGN KEY (obra_social_id) REFERENCES obras_sociales (id)
            )
        ''')
        
        # Tabla Detalle Facturas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detalle_facturas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                factura_id INTEGER NOT NULL,
                servicio_id INTEGER NOT NULL,
                cantidad INTEGER DEFAULT 1,
                precio_unitario REAL NOT NULL,
                subtotal REAL NOT NULL,
                FOREIGN KEY (factura_id) REFERENCES facturas (id),
                FOREIGN KEY (servicio_id) REFERENCES servicios (id)
            )
        ''')
        
        conn.commit()
        conn.close()

class PacientesTab(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Formulario
        form_layout = QFormLayout()
        self.nombre_edit = QLineEdit()
        self.apellido_edit = QLineEdit()
        self.dni_edit = QLineEdit()
        self.telefono_edit = QLineEdit()
        self.email_edit = QLineEdit()
        self.direccion_edit = QLineEdit()
        self.fecha_nacimiento_edit = QDateEdit()
        self.fecha_nacimiento_edit.setDate(QDate.currentDate())
        self.obra_social_combo = QComboBox()
        self.numero_afiliado_edit = QLineEdit()
        
        form_layout.addRow("Nombre:", self.nombre_edit)
        form_layout.addRow("Apellido:", self.apellido_edit)
        form_layout.addRow("DNI:", self.dni_edit)
        form_layout.addRow("Teléfono:", self.telefono_edit)
        form_layout.addRow("Email:", self.email_edit)
        form_layout.addRow("Dirección:", self.direccion_edit)
        form_layout.addRow("Fecha Nacimiento:", self.fecha_nacimiento_edit)
        form_layout.addRow("Obra Social:", self.obra_social_combo)
        form_layout.addRow("Número Afiliado:", self.numero_afiliado_edit)
        
        # Botones
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Agregar")
        self.update_button = QPushButton("Actualizar")
        self.delete_button = QPushButton("Eliminar")
        self.clear_button = QPushButton("Limpiar")
        
        self.add_button.clicked.connect(self.add_paciente)
        self.update_button.clicked.connect(self.update_paciente)
        self.delete_button.clicked.connect(self.delete_paciente)
        self.clear_button.clicked.connect(self.clear_form)
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.clear_button)
        
        # Tabla
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nombre", "Apellido", "DNI", "Teléfono", 
            "Email", "Fecha Nac.", "Obra Social", "Nº Afiliado"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.cellClicked.connect(self.load_selected_paciente)
        
        layout.addLayout(form_layout)
        layout.addLayout(button_layout)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
        self.load_obras_sociales()
    
    def load_obras_sociales(self):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre FROM obras_sociales")
        obras_sociales = cursor.fetchall()
        
        self.obra_social_combo.clear()
        self.obra_social_combo.addItem("Sin Obra Social", 0)
        for obra in obras_sociales:
            self.obra_social_combo.addItem(obra[1], obra[0])
        
        conn.close()
    
    def add_paciente(self):
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            obra_social_id = self.obra_social_combo.currentData()
            if obra_social_id == 0:
                obra_social_id = None
            
            cursor.execute('''
                INSERT INTO pacientes (nombre, apellido, dni, telefono, email, 
                                     direccion, fecha_nacimiento, obra_social_id, numero_afiliado)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.nombre_edit.text(),
                self.apellido_edit.text(),
                self.dni_edit.text(),
                self.telefono_edit.text(),
                self.email_edit.text(),
                self.direccion_edit.text(),
                self.fecha_nacimiento_edit.date().toString("yyyy-MM-dd"),
                obra_social_id,
                self.numero_afiliado_edit.text()
            ))
            
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "Éxito", "Paciente agregado correctamente")
            self.load_data()
            self.clear_form()
            
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "El DNI ya existe")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al agregar paciente: {str(e)}")
    
    def load_data(self):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p.id, p.nombre, p.apellido, p.dni, p.telefono, p.email,
                   p.fecha_nacimiento, COALESCE(os.nombre, 'Sin Obra Social'), p.numero_afiliado
            FROM pacientes p
            LEFT JOIN obras_sociales os ON p.obra_social_id = os.id
        ''')
        
        data = cursor.fetchall()
        self.table.setRowCount(len(data))
        
        for row, item in enumerate(data):
            for col, value in enumerate(item):
                self.table.setItem(row, col, QTableWidgetItem(str(value) if value else ""))
        
        conn.close()
    
    def load_selected_paciente(self, row, col):
        paciente_id = self.table.item(row, 0).text()
        
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pacientes WHERE id = ?", (paciente_id,))
        paciente = cursor.fetchone()
        
        if paciente:
            self.nombre_edit.setText(paciente[1])
            self.apellido_edit.setText(paciente[2])
            self.dni_edit.setText(paciente[3])
            self.telefono_edit.setText(paciente[4] or "")
            self.email_edit.setText(paciente[5] or "")
            self.direccion_edit.setText(paciente[6] or "")
            if paciente[7]:
                self.fecha_nacimiento_edit.setDate(QDate.fromString(paciente[7], "yyyy-MM-dd"))
            
            # Seleccionar obra social
            obra_social_id = paciente[8] or 0
            for i in range(self.obra_social_combo.count()):
                if self.obra_social_combo.itemData(i) == obra_social_id:
                    self.obra_social_combo.setCurrentIndex(i)
                    break
            
            self.numero_afiliado_edit.setText(paciente[9] or "")
        
        conn.close()
    
    def update_paciente(self):
        if not self.dni_edit.text():
            QMessageBox.warning(self, "Error", "Seleccione un paciente para actualizar")
            return
        
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            obra_social_id = self.obra_social_combo.currentData()
            if obra_social_id == 0:
                obra_social_id = None
            
            cursor.execute('''
                UPDATE pacientes SET nombre=?, apellido=?, telefono=?, email=?,
                                   direccion=?, fecha_nacimiento=?, obra_social_id=?, numero_afiliado=?
                WHERE dni=?
            ''', (
                self.nombre_edit.text(),
                self.apellido_edit.text(),
                self.telefono_edit.text(),
                self.email_edit.text(),
                self.direccion_edit.text(),
                self.fecha_nacimiento_edit.date().toString("yyyy-MM-dd"),
                obra_social_id,
                self.numero_afiliado_edit.text(),
                self.dni_edit.text()
            ))
            
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "Éxito", "Paciente actualizado correctamente")
            self.load_data()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al actualizar paciente: {str(e)}")
    
    def delete_paciente(self):
        if not self.dni_edit.text():
            QMessageBox.warning(self, "Error", "Seleccione un paciente para eliminar")
            return
        
        reply = QMessageBox.question(self, "Confirmar", "¿Está seguro de eliminar este paciente?")
        if reply == QMessageBox.Yes:
            try:
                conn = self.db_manager.get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM pacientes WHERE dni=?", (self.dni_edit.text(),))
                conn.commit()
                conn.close()
                
                QMessageBox.information(self, "Éxito", "Paciente eliminado correctamente")
                self.load_data()
                self.clear_form()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al eliminar paciente: {str(e)}")
    
    def clear_form(self):
        self.nombre_edit.clear()
        self.apellido_edit.clear()
        self.dni_edit.clear()
        self.telefono_edit.clear()
        self.email_edit.clear()
        self.direccion_edit.clear()
        self.fecha_nacimiento_edit.setDate(QDate.currentDate())
        self.obra_social_combo.setCurrentIndex(0)
        self.numero_afiliado_edit.clear()

class ProfesionalesTab(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Formulario
        form_layout = QFormLayout()
        self.nombre_edit = QLineEdit()
        self.apellido_edit = QLineEdit()
        self.especialidad_edit = QLineEdit()
        self.matricula_edit = QLineEdit()
        self.telefono_edit = QLineEdit()
        self.email_edit = QLineEdit()
        self.honorarios_edit = QDoubleSpinBox()
        self.honorarios_edit.setMaximum(999999.99)
        self.honorarios_edit.setPrefix("$ ")
        
        form_layout.addRow("Nombre:", self.nombre_edit)
        form_layout.addRow("Apellido:", self.apellido_edit)
        form_layout.addRow("Especialidad:", self.especialidad_edit)
        form_layout.addRow("Matrícula:", self.matricula_edit)
        form_layout.addRow("Teléfono:", self.telefono_edit)
        form_layout.addRow("Email:", self.email_edit)
        form_layout.addRow("Honorarios:", self.honorarios_edit)
        
        # Botones
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Agregar")
        self.update_button = QPushButton("Actualizar")
        self.delete_button = QPushButton("Eliminar")
        self.clear_button = QPushButton("Limpiar")
        
        self.add_button.clicked.connect(self.add_profesional)
        self.update_button.clicked.connect(self.update_profesional)
        self.delete_button.clicked.connect(self.delete_profesional)
        self.clear_button.clicked.connect(self.clear_form)
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.clear_button)
        
        # Tabla
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nombre", "Apellido", "Especialidad", "Matrícula", "Teléfono", "Honorarios"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.cellClicked.connect(self.load_selected_profesional)
        
        layout.addLayout(form_layout)
        layout.addLayout(button_layout)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def add_profesional(self):
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO profesionales (nombre, apellido, especialidad, matricula, 
                                         telefono, email, honorarios)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.nombre_edit.text(),
                self.apellido_edit.text(),
                self.especialidad_edit.text(),
                self.matricula_edit.text(),
                self.telefono_edit.text(),
                self.email_edit.text(),
                self.honorarios_edit.value()
            ))
            
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "Éxito", "Profesional agregado correctamente")
            self.load_data()
            self.clear_form()
            
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "La matrícula ya existe")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al agregar profesional: {str(e)}")
    
    def load_data(self):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM profesionales")
        
        data = cursor.fetchall()
        self.table.setRowCount(len(data))
        
        for row, item in enumerate(data):
            for col, value in enumerate(item):
                if col == 7:  # Honorarios
                    self.table.setItem(row, col, QTableWidgetItem(f"${value:.2f}"))
                else:
                    self.table.setItem(row, col, QTableWidgetItem(str(value) if value else ""))
        
        conn.close()
    
    def load_selected_profesional(self, row, col):
        profesional_id = self.table.item(row, 0).text()
        
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM profesionales WHERE id = ?", (profesional_id,))
        profesional = cursor.fetchone()
        
        if profesional:
            self.nombre_edit.setText(profesional[1])
            self.apellido_edit.setText(profesional[2])
            self.especialidad_edit.setText(profesional[3])
            self.matricula_edit.setText(profesional[4])
            self.telefono_edit.setText(profesional[5] or "")
            self.email_edit.setText(profesional[6] or "")
            self.honorarios_edit.setValue(profesional[7] or 0)
        
        conn.close()
    
    def update_profesional(self):
        if not self.matricula_edit.text():
            QMessageBox.warning(self, "Error", "Seleccione un profesional para actualizar")
            return
        
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE profesionales SET nombre=?, apellido=?, especialidad=?, 
                                       telefono=?, email=?, honorarios=?
                WHERE matricula=?
            ''', (
                self.nombre_edit.text(),
                self.apellido_edit.text(),
                self.especialidad_edit.text(),
                self.telefono_edit.text(),
                self.email_edit.text(),
                self.honorarios_edit.value(),
                self.matricula_edit.text()
            ))
            
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "Éxito", "Profesional actualizado correctamente")
            self.load_data()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al actualizar profesional: {str(e)}")
    
    def delete_profesional(self):
        if not self.matricula_edit.text():
            QMessageBox.warning(self, "Error", "Seleccione un profesional para eliminar")
            return
        
        reply = QMessageBox.question(self, "Confirmar", "¿Está seguro de eliminar este profesional?")
        if reply == QMessageBox.Yes:
            try:
                conn = self.db_manager.get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM profesionales WHERE matricula=?", (self.matricula_edit.text(),))
                conn.commit()
                conn.close()
                
                QMessageBox.information(self, "Éxito", "Profesional eliminado correctamente")
                self.load_data()
                self.clear_form()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al eliminar profesional: {str(e)}")
    
    def clear_form(self):
        self.nombre_edit.clear()
        self.apellido_edit.clear()
        self.especialidad_edit.clear()
        self.matricula_edit.clear()
        self.telefono_edit.clear()
        self.email_edit.clear()
        self.honorarios_edit.setValue(0)

class ObrasSocialesTab(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Formulario
        form_layout = QFormLayout()
        self.nombre_edit = QLineEdit()
        self.codigo_edit = QLineEdit()
        self.telefono_edit = QLineEdit()
        self.email_edit = QLineEdit()
        self.direccion_edit = QLineEdit()
        
        form_layout.addRow("Nombre:", self.nombre_edit)
        form_layout.addRow("Código:", self.codigo_edit)
        form_layout.addRow("Teléfono:", self.telefono_edit)
        form_layout.addRow("Email:", self.email_edit)
        form_layout.addRow("Dirección:", self.direccion_edit)
        
        # Botones
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Agregar")
        self.update_button = QPushButton("Actualizar")
        self.delete_button = QPushButton("Eliminar")
        self.clear_button = QPushButton("Limpiar")
        
        self.add_button.clicked.connect(self.add_obra_social)
        self.update_button.clicked.connect(self.update_obra_social)
        self.delete_button.clicked.connect(self.delete_obra_social)
        self.clear_button.clicked.connect(self.clear_form)
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.clear_button)
        
        # Tabla
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nombre", "Código", "Teléfono", "Email", "Dirección"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.cellClicked.connect(self.load_selected_obra_social)
        
        layout.addLayout(form_layout)
        layout.addLayout(button_layout)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def add_obra_social(self):
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO obras_sociales (nombre, codigo, telefono, email, direccion)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                self.nombre_edit.text(),
                self.codigo_edit.text(),
                self.telefono_edit.text(),
                self.email_edit.text(),
                self.direccion_edit.text()
            ))
            
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "Éxito", "Obra Social agregada correctamente")
            self.load_data()
            self.clear_form()
            
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "El código ya existe")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al agregar obra social: {str(e)}")
    
    def load_data(self):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM obras_sociales")
        
        data = cursor.fetchall()
        self.table.setRowCount(len(data))
        
        for row, item in enumerate(data):
            for col, value in enumerate(item):
                self.table.setItem(row, col, QTableWidgetItem(str(value) if value else ""))
        
        conn.close()
    
    def load_selected_obra_social(self, row, col):
        obra_social_id = self.table.item(row, 0).text()
        
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM obras_sociales WHERE id = ?", (obra_social_id,))
        obra_social = cursor.fetchone()
        
        if obra_social:
            self.nombre_edit.setText(obra_social[1])
            self.codigo_edit.setText(obra_social[2] or "")
            self.telefono_edit.setText(obra_social[3] or "")
            self.email_edit.setText(obra_social[4] or "")
            self.direccion_edit.setText(obra_social[5] or "")
        
        conn.close()
    
    def update_obra_social(self):
        if not self.nombre_edit.text():
            QMessageBox.warning(self, "Error", "Seleccione una obra social para actualizar")
            return
        
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Buscar por nombre para actualizar
            cursor.execute('''
                UPDATE obras_sociales SET codigo=?, telefono=?, email=?, direccion=?
                WHERE nombre=?
            ''', (
                self.codigo_edit.text(),
                self.telefono_edit.text(),
                self.email_edit.text(),
                self.direccion_edit.text(),
                self.nombre_edit.text()
            ))
            
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "Éxito", "Obra Social actualizada correctamente")
            self.load_data()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al actualizar obra social: {str(e)}")
    
    def delete_obra_social(self):
        if not self.nombre_edit.text():
            QMessageBox.warning(self, "Error", "Seleccione una obra social para eliminar")
            return
        
        reply = QMessageBox.question(self, "Confirmar", "¿Está seguro de eliminar esta obra social?")
        if reply == QMessageBox.Yes:
            try:
                conn = self.db_manager.get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM obras_sociales WHERE nombre=?", (self.nombre_edit.text(),))
                conn.commit()
                conn.close()
                
                QMessageBox.information(self, "Éxito", "Obra Social eliminada correctamente")
                self.load_data()
                self.clear_form()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al eliminar obra social: {str(e)}")
    
    def clear_form(self):
        self.nombre_edit.clear()
        self.codigo_edit.clear()
        self.telefono_edit.clear()
        self.email_edit.clear()
        self.direccion_edit.clear()

class ServiciosTab(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Formulario
        form_layout = QFormLayout()
        self.codigo_edit = QLineEdit()
        self.descripcion_edit = QLineEdit()
        self.precio_edit = QDoubleSpinBox()
        self.precio_edit.setMaximum(999999.99)
        self.precio_edit.setPrefix("$ ")
        self.obra_social_combo = QComboBox()
        
        form_layout.addRow("Código:", self.codigo_edit)
        form_layout.addRow("Descripción:", self.descripcion_edit)
        form_layout.addRow("Precio:", self.precio_edit)
        form_layout.addRow("Obra Social:", self.obra_social_combo)
        
        # Botones
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Agregar")
        self.update_button = QPushButton("Actualizar")
        self.delete_button = QPushButton("Eliminar")
        self.clear_button = QPushButton("Limpiar")
        
        self.add_button.clicked.connect(self.add_servicio)
        self.update_button.clicked.connect(self.update_servicio)
        self.delete_button.clicked.connect(self.delete_servicio)
        self.clear_button.clicked.connect(self.clear_form)
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.clear_button)
        
        # Tabla
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "ID", "Código", "Descripción", "Precio", "Obra Social"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.cellClicked.connect(self.load_selected_servicio)
        
        layout.addLayout(form_layout)
        layout.addLayout(button_layout)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
        self.load_obras_sociales()
    
    def load_obras_sociales(self):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre FROM obras_sociales")
        obras_sociales = cursor.fetchall()
        
        self.obra_social_combo.clear()
        self.obra_social_combo.addItem("General", None)
        for obra in obras_sociales:
            self.obra_social_combo.addItem(obra[1], obra[0])
        
        conn.close()
    
    def add_servicio(self):
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            obra_social_id = self.obra_social_combo.currentData()
            
            cursor.execute('''
                INSERT INTO servicios (codigo, descripcion, precio, obra_social_id)
                VALUES (?, ?, ?, ?)
            ''', (
                self.codigo_edit.text(),
                self.descripcion_edit.text(),
                self.precio_edit.value(),
                obra_social_id
            ))
            
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "Éxito", "Servicio agregado correctamente")
            self.load_data()
            self.clear_form()
            
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "El código ya existe")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al agregar servicio: {str(e)}")
    
    def load_data(self):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT s.id, s.codigo, s.descripcion, s.precio, 
                   COALESCE(os.nombre, 'General') as obra_social
            FROM servicios s
            LEFT JOIN obras_sociales os ON s.obra_social_id = os.id
        ''')
        
        data = cursor.fetchall()
        self.table.setRowCount(len(data))
        
        for row, item in enumerate(data):
            for col, value in enumerate(item):
                if col == 3:  # Precio
                    self.table.setItem(row, col, QTableWidgetItem(f"${value:.2f}"))
                else:
                    self.table.setItem(row, col, QTableWidgetItem(str(value) if value else ""))
        
        conn.close()
    
    def load_selected_servicio(self, row, col):
        servicio_id = self.table.item(row, 0).text()
        
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM servicios WHERE id = ?", (servicio_id,))
        servicio = cursor.fetchone()
        
        if servicio:
            self.codigo_edit.setText(servicio[1])
            self.descripcion_edit.setText(servicio[2])
            self.precio_edit.setValue(servicio[3])
            
            # Seleccionar obra social
            obra_social_id = servicio[4]
            for i in range(self.obra_social_combo.count()):
                if self.obra_social_combo.itemData(i) == obra_social_id:
                    self.obra_social_combo.setCurrentIndex(i)
                    break
        
        conn.close()
    
    def update_servicio(self):
        if not self.codigo_edit.text():
            QMessageBox.warning(self, "Error", "Seleccione un servicio para actualizar")
            return
        
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            obra_social_id = self.obra_social_combo.currentData()
            
            cursor.execute('''
                UPDATE servicios SET descripcion=?, precio=?, obra_social_id=?
                WHERE codigo=?
            ''', (
                self.descripcion_edit.text(),
                self.precio_edit.value(),
                obra_social_id,
                self.codigo_edit.text()
            ))
            
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "Éxito", "Servicio actualizado correctamente")
            self.load_data()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al actualizar servicio: {str(e)}")
    
    def delete_servicio(self):
        if not self.codigo_edit.text():
            QMessageBox.warning(self, "Error", "Seleccione un servicio para eliminar")
            return
        
        reply = QMessageBox.question(self, "Confirmar", "¿Está seguro de eliminar este servicio?")
        if reply == QMessageBox.Yes:
            try:
                conn = self.db_manager.get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM servicios WHERE codigo=?", (self.codigo_edit.text(),))
                conn.commit()
                conn.close()
                
                QMessageBox.information(self, "Éxito", "Servicio eliminado correctamente")
                self.load_data()
                self.clear_form()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al eliminar servicio: {str(e)}")
    
    def clear_form(self):
        self.codigo_edit.clear()
        self.descripcion_edit.clear()
        self.precio_edit.setValue(0)
        self.obra_social_combo.setCurrentIndex(0)

class TurnosTab(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Formulario
        form_layout = QFormLayout()
        self.paciente_combo = QComboBox()
        self.profesional_combo = QComboBox()
        self.fecha_edit = QDateEdit()
        self.fecha_edit.setDate(QDate.currentDate())
        self.hora_edit = QTimeEdit()
        self.hora_edit.setTime(QTime.currentTime())
        self.estado_combo = QComboBox()
        self.estado_combo.addItems(["Programado", "Confirmado", "Atendido", "Cancelado", "No Asistió"])
        self.observaciones_edit = QTextEdit()
        self.observaciones_edit.setMaximumHeight(80)
        
        form_layout.addRow("Paciente:", self.paciente_combo)
        form_layout.addRow("Profesional:", self.profesional_combo)
        form_layout.addRow("Fecha:", self.fecha_edit)
        form_layout.addRow("Hora:", self.hora_edit)
        form_layout.addRow("Estado:", self.estado_combo)
        form_layout.addRow("Observaciones:", self.observaciones_edit)
        
        # Botones
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Agregar")
        self.update_button = QPushButton("Actualizar")
        self.delete_button = QPushButton("Eliminar")
        self.clear_button = QPushButton("Limpiar")
        
        self.add_button.clicked.connect(self.add_turno)
        self.update_button.clicked.connect(self.update_turno)
        self.delete_button.clicked.connect(self.delete_turno)
        self.clear_button.clicked.connect(self.clear_form)
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.clear_button)
        
        # Tabla
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Paciente", "Profesional", "Fecha", "Hora", "Estado", "Observaciones"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.cellClicked.connect(self.load_selected_turno)
        
        layout.addLayout(form_layout)
        layout.addLayout(button_layout)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
        self.load_combos()
    
    def load_combos(self):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        # Cargar pacientes
        cursor.execute("SELECT id, nombre, apellido FROM pacientes ORDER BY apellido, nombre")
        pacientes = cursor.fetchall()
        self.paciente_combo.clear()
        for paciente in pacientes:
            self.paciente_combo.addItem(f"{paciente[2]} {paciente[1]}", paciente[0])
        
        # Cargar profesionales
        cursor.execute("SELECT id, nombre, apellido, especialidad FROM profesionales ORDER BY apellido, nombre")
        profesionales = cursor.fetchall()
        self.profesional_combo.clear()
        for profesional in profesionales:
            self.profesional_combo.addItem(f"Dr. {profesional[2]} {profesional[1]} - {profesional[3]}", profesional[0])
        
        conn.close()
    
    def add_turno(self):
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            profesional_id = self.profesional_combo.currentData()
            fecha = self.fecha_edit.date().toString("yyyy-MM-dd")
            hora = self.hora_edit.time().toString("HH:mm")

            # 🔍 Verificar si ya existe un turno con el mismo profesional en esa fecha y hora
            cursor.execute('''
                SELECT COUNT(*) FROM turnos
                WHERE profesional_id = ? AND fecha = ? AND hora = ?
            ''', (profesional_id, fecha, hora))
            existe = cursor.fetchone()[0]

            if existe > 0:
                QMessageBox.warning(self, "Conflicto",
                                    "Este profesional ya tiene un turno en la misma fecha y hora.")
                conn.close()
                return

            # Si no hay conflicto, insertar
            cursor.execute('''
                INSERT INTO turnos (paciente_id, profesional_id, fecha, hora, estado, observaciones)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                self.paciente_combo.currentData(),
                profesional_id,
                fecha,
                hora,
                self.estado_combo.currentText(),
                self.observaciones_edit.toPlainText()
            ))

            conn.commit()
            conn.close()

            QMessageBox.information(self, "Éxito", "Turno agregado correctamente")
            self.load_data()
            self.clear_form()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al agregar turno: {str(e)}")

    def load_data(self):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT t.id, 
                   p.apellido || ', ' || p.nombre as paciente,
                   pr.apellido || ', ' || pr.nombre as profesional,
                   t.fecha, t.hora, t.estado, t.observaciones
            FROM turnos t
            JOIN pacientes p ON t.paciente_id = p.id
            JOIN profesionales pr ON t.profesional_id = pr.id
            ORDER BY t.fecha DESC, t.hora DESC
        ''')
        
        data = cursor.fetchall()
        self.table.setRowCount(len(data))
        
        for row, item in enumerate(data):
            for col, value in enumerate(item):
                self.table.setItem(row, col, QTableWidgetItem(str(value) if value else ""))
        
        conn.close()
    
    def load_selected_turno(self, row, col):
        turno_id = self.table.item(row, 0).text()
        
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM turnos WHERE id = ?", (turno_id,))
        turno = cursor.fetchone()
        
        if turno:
            # Seleccionar paciente
            for i in range(self.paciente_combo.count()):
                if self.paciente_combo.itemData(i) == turno[1]:
                    self.paciente_combo.setCurrentIndex(i)
                    break
            
            # Seleccionar profesional
            for i in range(self.profesional_combo.count()):
                if self.profesional_combo.itemData(i) == turno[2]:
                    self.profesional_combo.setCurrentIndex(i)
                    break
            
            self.fecha_edit.setDate(QDate.fromString(turno[3], "yyyy-MM-dd"))
            self.hora_edit.setTime(QTime.fromString(turno[4], "HH:mm"))
            
            # Seleccionar estado
            estado_index = self.estado_combo.findText(turno[5])
            if estado_index >= 0:
                self.estado_combo.setCurrentIndex(estado_index)
            
            self.observaciones_edit.setPlainText(turno[6] or "")
        
        conn.close()
    
    def update_turno(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Error", "Seleccione un turno de la tabla")
            return

        turno_id = self.table.item(current_row, 0).text()

        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            profesional_id = self.profesional_combo.currentData()
            fecha = self.fecha_edit.date().toString("yyyy-MM-dd")
            hora = self.hora_edit.time().toString("HH:mm")

            # 🔍 Verificar conflictos (excluyendo el turno actual)
            cursor.execute('''
                SELECT COUNT(*) FROM turnos
                WHERE profesional_id = ? AND fecha = ? AND hora = ? AND id != ?
            ''', (profesional_id, fecha, hora, turno_id))
            existe = cursor.fetchone()[0]

            if existe > 0:
                QMessageBox.warning(self, "Conflicto",
                                    "Este profesional ya tiene un turno en la misma fecha y hora.")
                conn.close()
                return

            # Si no hay conflicto, actualizar
            cursor.execute('''
                UPDATE turnos
                SET paciente_id=?, profesional_id=?, fecha=?, hora=?, estado=?, observaciones=?
                WHERE id=?
            ''', (
                self.paciente_combo.currentData(),
                profesional_id,
                fecha,
                hora,
                self.estado_combo.currentText(),
                self.observaciones_edit.toPlainText(),
                turno_id
            ))

            conn.commit()
            conn.close()

            QMessageBox.information(self, "Éxito", "Turno actualizado correctamente")
            self.load_data()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al actualizar turno: {str(e)}")

    
    def delete_turno(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Error", "Seleccione un turno para eliminar")
            return
        
        reply = QMessageBox.question(self, "Confirmar", "¿Está seguro de eliminar este turno?")
        if reply == QMessageBox.Yes:
            try:
                turno_id = self.table.item(current_row, 0).text()
                
                conn = self.db_manager.get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM turnos WHERE id=?", (turno_id,))
                conn.commit()
                conn.close()
                
                QMessageBox.information(self, "Éxito", "Turno eliminado correctamente")
                self.load_data()
                self.clear_form()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al eliminar turno: {str(e)}")
    
    def clear_form(self):
        self.paciente_combo.setCurrentIndex(0)
        self.profesional_combo.setCurrentIndex(0)
        self.fecha_edit.setDate(QDate.currentDate())
        self.hora_edit.setTime(QTime.currentTime())
        self.estado_combo.setCurrentIndex(0)
        self.observaciones_edit.clear()

class AgendaTab(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()
        self.load_agenda()
    
    def init_ui(self):
        layout = QHBoxLayout()
        
        # Panel izquierdo - Calendario
        left_panel = QVBoxLayout()
        
        self.calendar = QCalendarWidget()
        self.calendar.clicked.connect(self.date_selected)
        
        # Filtros
        filter_group = QGroupBox("Filtros")
        filter_layout = QFormLayout()
        
        self.profesional_filter = QComboBox()
        self.profesional_filter.addItem("Todos los profesionales", None)
        self.estado_filter = QComboBox()
        self.estado_filter.addItems(["Todos", "Programado", "Confirmado", "Atendido", "Cancelado", "No Asistió"])
        
        filter_layout.addRow("Profesional:", self.profesional_filter)
        filter_layout.addRow("Estado:", self.estado_filter)
        
        self.profesional_filter.currentTextChanged.connect(self.load_agenda)
        self.estado_filter.currentTextChanged.connect(self.load_agenda)
        
        filter_group.setLayout(filter_layout)
        
        left_panel.addWidget(self.calendar)
        left_panel.addWidget(filter_group)
        
        # Panel derecho - Lista de turnos
        right_panel = QVBoxLayout()
        
        self.fecha_label = QLabel(f"Turnos del {QDate.currentDate().toString('dd/MM/yyyy')}")
        self.fecha_label.setFont(QFont("Arial", 12, QFont.Bold))
        
        self.turnos_list = QListWidget()
        self.turnos_list.itemDoubleClicked.connect(self.edit_turno)
        
        # Botones de acción rápida
        action_layout = QHBoxLayout()
        self.confirmar_button = QPushButton("Confirmar")
        self.atender_button = QPushButton("Atender")
        self.cancelar_button = QPushButton("Cancelar")
        
        self.confirmar_button.clicked.connect(lambda: self.cambiar_estado("Confirmado"))
        self.atender_button.clicked.connect(lambda: self.cambiar_estado("Atendido"))
        self.cancelar_button.clicked.connect(lambda: self.cambiar_estado("Cancelado"))
        
        action_layout.addWidget(self.confirmar_button)
        action_layout.addWidget(self.atender_button)
        action_layout.addWidget(self.cancelar_button)
        
        right_panel.addWidget(self.fecha_label)
        right_panel.addWidget(self.turnos_list)
        right_panel.addLayout(action_layout)
        
        # Agregar paneles al layout principal
        left_widget = QWidget()
        left_widget.setLayout(left_panel)
        left_widget.setMaximumWidth(350)
        
        right_widget = QWidget()
        right_widget.setLayout(right_panel)
        
        layout.addWidget(left_widget)
        layout.addWidget(right_widget)
        
        self.setLayout(layout)
        self.load_profesionales()
    
    def load_profesionales(self):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, apellido FROM profesionales ORDER BY apellido, nombre")
        profesionales = cursor.fetchall()
        
        self.profesional_filter.clear()
        self.profesional_filter.addItem("Todos los profesionales", None)
        for profesional in profesionales:
            self.profesional_filter.addItem(f"Dr. {profesional[2]} {profesional[1]}", profesional[0])
        
        conn.close()
    
    def date_selected(self, date):
        self.fecha_label.setText(f"Turnos del {date.toString('dd/MM/yyyy')}")
        self.load_agenda()
    
    def load_agenda(self):
        selected_date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        profesional_id = self.profesional_filter.currentData()
        estado = self.estado_filter.currentText()
        
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT t.id, t.hora, 
                   p.apellido || ', ' || p.nombre as paciente,
                   pr.apellido || ', ' || pr.nombre as profesional,
                   t.estado, t.observaciones
            FROM turnos t
            JOIN pacientes p ON t.paciente_id = p.id
            JOIN profesionales pr ON t.profesional_id = pr.id
            WHERE t.fecha = ?
        '''
        params = [selected_date]
        
        if profesional_id:
            query += " AND t.profesional_id = ?"
            params.append(profesional_id)
        
        if estado != "Todos":
            query += " AND t.estado = ?"
            params.append(estado)
        
        query += " ORDER BY t.hora"
        
        cursor.execute(query, params)
        turnos = cursor.fetchall()
        
        self.turnos_list.clear()
        for turno in turnos:
            hora = turno[1]
            paciente = turno[2]
            profesional = turno[3]
            estado = turno[4]
            observaciones = turno[5] or ""
            
            item_text = f"{hora} - {paciente} | Dr. {profesional} | {estado}"
            if observaciones:
                item_text += f" | {observaciones[:30]}..."
            
            item = self.turnos_list.addItem(item_text)
            # Guardar el ID del turno en el item
            self.turnos_list.item(self.turnos_list.count() - 1).setData(Qt.UserRole, turno[0])
        
        conn.close()
    
    def cambiar_estado(self, nuevo_estado):
        current_item = self.turnos_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Error", "Seleccione un turno")
            return
        
        turno_id = current_item.data(Qt.UserRole)
        
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE turnos SET estado = ? WHERE id = ?", (nuevo_estado, turno_id))
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "Éxito", f"Estado cambiado a {nuevo_estado}")
            self.load_agenda()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cambiar estado: {str(e)}")
    
    def edit_turno(self, item):
        # Esta función podría abrir un diálogo para editar el turno
        QMessageBox.information(self, "Info", "Funcionalidad de edición rápida - Por implementar")

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QFormLayout, QLineEdit, QComboBox, QDateEdit,
    QSpinBox, QPushButton, QLabel, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QMessageBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QDate
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import sqlite3
import os


from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sqlite3
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

import sys
import sqlite3
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

class FacturasTab(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.servicios_factura = []  # Lista temporal de servicios
        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout()

        # Formulario principal
        form_group = QGroupBox("Datos de la Factura")
        form_layout = QFormLayout()

        self.numero_edit = QLineEdit()
        self.paciente_combo = QComboBox()
        self.obra_social_combo = QComboBox()
        self.fecha_edit = QDateEdit()
        self.fecha_edit.setDate(QDate.currentDate())
        self.estado_combo = QComboBox()
        self.estado_combo.addItems(["Pendiente", "Pagada", "Anulada"])

        form_layout.addRow("Número:", self.numero_edit)
        form_layout.addRow("Paciente:", self.paciente_combo)
        form_layout.addRow("Obra Social:", self.obra_social_combo)
        form_layout.addRow("Fecha:", self.fecha_edit)
        form_layout.addRow("Estado:", self.estado_combo)
        form_group.setLayout(form_layout)

        # Sección de servicios
        servicios_group = QGroupBox("Servicios")
        servicios_layout = QVBoxLayout()

        add_servicio_layout = QHBoxLayout()
        self.servicio_combo = QComboBox()
        self.cantidad_spin = QSpinBox()
        self.cantidad_spin.setMinimum(1)
        self.cantidad_spin.setValue(1)
        self.add_servicio_button = QPushButton("Agregar Servicio")
        self.add_servicio_button.clicked.connect(self.add_servicio_to_factura)

        add_servicio_layout.addWidget(QLabel("Servicio:"))
        add_servicio_layout.addWidget(self.servicio_combo)
        add_servicio_layout.addWidget(QLabel("Cantidad:"))
        add_servicio_layout.addWidget(self.cantidad_spin)
        add_servicio_layout.addWidget(self.add_servicio_button)

        # Tabla de servicios
        self.servicios_table = QTableWidget()
        self.servicios_table.setColumnCount(5)
        self.servicios_table.setHorizontalHeaderLabels([
            "Servicio", "Cantidad", "Precio Unit.", "Subtotal", "Acción"
        ])

        total_layout = QHBoxLayout()
        self.total_label = QLabel("Total: $0.00")
        self.total_label.setFont(QFont("Arial", 12, QFont.Bold))
        total_layout.addStretch()
        total_layout.addWidget(self.total_label)

        servicios_layout.addLayout(add_servicio_layout)
        servicios_layout.addWidget(self.servicios_table)
        servicios_layout.addLayout(total_layout)
        servicios_group.setLayout(servicios_layout)

        # Botones principales - AQUÍ ESTÁ EL BOTÓN PDF CORREGIDO
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Guardar Factura")
        self.update_button = QPushButton("Actualizar")
        self.delete_button = QPushButton("Eliminar")
        self.clear_button = QPushButton("Nueva Factura")
        self.pdf_button = QPushButton("Generar PDF")  # Botón PDF agregado

        self.save_button.clicked.connect(self.save_factura)
        self.update_button.clicked.connect(self.update_factura)
        self.delete_button.clicked.connect(self.delete_factura)
        self.clear_button.clicked.connect(self.clear_form)
        self.pdf_button.clicked.connect(self.generate_pdf)  # Conectado a función PDF

        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(self.pdf_button)  # Botón PDF añadido al layout

        # Tabla de facturas
        self.facturas_table = QTableWidget()
        self.facturas_table.setColumnCount(6)
        self.facturas_table.setHorizontalHeaderLabels([
            "ID", "Número", "Paciente", "Fecha", "Total", "Estado"
        ])
        self.facturas_table.horizontalHeader().setStretchLastSection(True)
        self.facturas_table.cellClicked.connect(self.load_selected_factura)

        layout.addWidget(form_group)
        layout.addWidget(servicios_group)
        layout.addLayout(button_layout)
        layout.addWidget(self.facturas_table)

        self.setLayout(layout)
        self.load_combos()

    def load_combos(self):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        # Cargar pacientes
        cursor.execute("SELECT id, nombre, apellido FROM pacientes ORDER BY apellido, nombre")
        pacientes = cursor.fetchall()
        self.paciente_combo.clear()
        for p in pacientes:
            self.paciente_combo.addItem(f"{p[2]} {p[1]}", p[0])

        # Cargar obras sociales
        cursor.execute("SELECT id, nombre FROM obras_sociales ORDER BY nombre")
        obras = cursor.fetchall()
        self.obra_social_combo.clear()
        self.obra_social_combo.addItem("Particular", None)
        for o in obras:
            self.obra_social_combo.addItem(o[1], o[0])

        # Cargar servicios
        cursor.execute("SELECT id, codigo, descripcion, precio FROM servicios ORDER BY descripcion")
        servicios = cursor.fetchall()
        self.servicio_combo.clear()
        for s in servicios:
            self.servicio_combo.addItem(f"{s[1]} - {s[2]} (${s[3]:.2f})", s[0])

        conn.close()

    def add_servicio_to_factura(self):
        servicio_id = self.servicio_combo.currentData()
        if not servicio_id:
            return

        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT codigo, descripcion, precio FROM servicios WHERE id = ?", (servicio_id,))
        servicio = cursor.fetchone()
        conn.close()

        if servicio:
            cantidad = self.cantidad_spin.value()
            precio_unitario = servicio[2]
            subtotal = cantidad * precio_unitario
            servicio_data = {
                'id': servicio_id,
                'codigo': servicio[0],
                'descripcion': servicio[1],
                'cantidad': cantidad,
                'precio_unitario': precio_unitario,
                'subtotal': subtotal
            }
            self.servicios_factura.append(servicio_data)
            self.update_servicios_table()
            self.calculate_total()

    def update_servicios_table(self):
        self.servicios_table.setRowCount(len(self.servicios_factura))
        for row, s in enumerate(self.servicios_factura):
            self.servicios_table.setItem(row, 0, QTableWidgetItem(f"{s['codigo']} - {s['descripcion']}"))
            self.servicios_table.setItem(row, 1, QTableWidgetItem(str(s['cantidad'])))
            self.servicios_table.setItem(row, 2, QTableWidgetItem(f"${s['precio_unitario']:.2f}"))
            self.servicios_table.setItem(row, 3, QTableWidgetItem(f"${s['subtotal']:.2f}"))

            btn = QPushButton("Eliminar")
            btn.clicked.connect(lambda checked, r=row: self.remove_servicio(r))
            self.servicios_table.setCellWidget(row, 4, btn)

    def remove_servicio(self, row):
        if 0 <= row < len(self.servicios_factura):
            self.servicios_factura.pop(row)
            self.update_servicios_table()
            self.calculate_total()

    def calculate_total(self):
        total = sum(s['subtotal'] for s in self.servicios_factura)
        self.total_label.setText(f"Total: ${total:.2f}")
        return total

    # FUNCIÓN PDF CORREGIDA Y COMPLETA
    def generate_pdf(self):
        if not self.numero_edit.text():
            QMessageBox.warning(self, "Error", "Seleccione una factura para generar PDF")
            return

        numero = self.numero_edit.text()
        paciente = self.paciente_combo.currentText()
        obra_social = self.obra_social_combo.currentText()
        fecha = self.fecha_edit.date().toString("yyyy-MM-dd")
        estado = self.estado_combo.currentText()
        total = self.calculate_total()
        servicios = self.servicios_factura

        # Crear nombre de archivo
        filename = f"Factura_{numero}_{paciente.replace(' ', '_')}_{fecha}.pdf"
        filepath = os.path.join(os.getcwd(), filename)

        # Crear PDF
        c = canvas.Canvas(filepath, pagesize=A4)
        width, height = A4

        # Encabezado
        c.setFont("Helvetica-Bold", 18)
        c.drawString(200, height - 50, "FACTURA MÉDICA")
        
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 100, f"Número: {numero}")
        c.drawString(50, height - 120, f"Paciente: {paciente}")
        c.drawString(50, height - 140, f"Obra Social: {obra_social}")
        c.drawString(50, height - 160, f"Fecha: {fecha}")
        c.drawString(50, height - 180, f"Estado: {estado}")

        # Línea separadora
        c.line(50, height - 200, width - 50, height - 200)

        # Encabezados de tabla
        y = height - 230
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "Código")
        c.drawString(120, y, "Descripción")
        c.drawString(350, y, "Cantidad")
        c.drawString(420, y, "Precio Unit.")
        c.drawString(500, y, "Subtotal")

        # Línea bajo encabezados
        c.line(50, y - 10, width - 50, y - 10)

        # Servicios
        c.setFont("Helvetica", 10)
        y -= 30
        for s in servicios:
            c.drawString(50, y, str(s['codigo']))
            c.drawString(120, y, s['descripcion'][:25])  # Limitar descripción
            c.drawString(350, y, str(s['cantidad']))
            c.drawString(420, y, f"${s['precio_unitario']:.2f}")
            c.drawString(500, y, f"${s['subtotal']:.2f}")
            y -= 20

        # Total
        c.line(400, y - 10, width - 50, y - 10)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(420, y - 30, "TOTAL:")
        c.drawString(500, y - 30, f"${total:.2f}")

        # Pie de página
        c.setFont("Helvetica", 8)
        c.drawString(50, 50, "Documento generado automáticamente por el sistema de facturación")

        c.save()
        QMessageBox.information(self, "PDF Generado", f"Factura exportada como:\n{filepath}")

    def save_factura(self):
        if not self.numero_edit.text() or not self.servicios_factura:
            QMessageBox.warning(self, "Error", "Complete todos los campos y agregue al menos un servicio")
            return

        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            total = self.calculate_total()
            obra_social_id = self.obra_social_combo.currentData()

            cursor.execute('''
                INSERT INTO facturas (numero, paciente_id, obra_social_id, fecha, total, estado)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                self.numero_edit.text(),
                self.paciente_combo.currentData(),
                obra_social_id,
                self.fecha_edit.date().toString("yyyy-MM-dd"),
                total,
                self.estado_combo.currentText()
            ))
            factura_id = cursor.lastrowid

            for s in self.servicios_factura:
                cursor.execute('''
                    INSERT INTO detalle_facturas (factura_id, servicio_id, cantidad, precio_unitario, subtotal)
                    VALUES (?, ?, ?, ?, ?)
                ''', (factura_id, s['id'], s['cantidad'], s['precio_unitario'], s['subtotal']))

            conn.commit()
            conn.close()
            QMessageBox.information(self, "Éxito", "Factura guardada correctamente")
            self.load_data()
            self.clear_form()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "El número de factura ya existe")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al guardar factura: {str(e)}")

    def load_data(self):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT f.id, f.numero, p.apellido || ', ' || p.nombre as paciente,
                   f.fecha, f.total, f.estado
            FROM facturas f
            JOIN pacientes p ON f.paciente_id = p.id
            ORDER BY f.fecha DESC
        ''')
        data = cursor.fetchall()
        self.facturas_table.setRowCount(len(data))
        for row, item in enumerate(data):
            for col, value in enumerate(item):
                if col == 4:
                    self.facturas_table.setItem(row, col, QTableWidgetItem(f"${value:.2f}"))
                else:
                    self.facturas_table.setItem(row, col, QTableWidgetItem(str(value) if value else ""))
        conn.close()

    def load_selected_factura(self, row, col):
        factura_id = self.facturas_table.item(row, 0).text()
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM facturas WHERE id = ?", (factura_id,))
        factura = cursor.fetchone()
        if factura:
            self.numero_edit.setText(factura[1])

            for i in range(self.paciente_combo.count()):
                if self.paciente_combo.itemData(i) == factura[2]:
                    self.paciente_combo.setCurrentIndex(i)
                    break

            for i in range(self.obra_social_combo.count()):
                if self.obra_social_combo.itemData(i) == factura[3]:
                    self.obra_social_combo.setCurrentIndex(i)
                    break

            self.fecha_edit.setDate(QDate.fromString(factura[4], "yyyy-MM-dd"))

            estado_index = self.estado_combo.findText(factura[6])
            if estado_index >= 0:
                self.estado_combo.setCurrentIndex(estado_index)

            cursor.execute('''
                SELECT s.id, s.codigo, s.descripcion, df.cantidad, df.precio_unitario, df.subtotal
                FROM detalle_facturas df
                JOIN servicios s ON df.servicio_id = s.id
                WHERE df.factura_id = ?
            ''', (factura_id,))
            servicios = cursor.fetchall()
            self.servicios_factura = []
            for s in servicios:
                self.servicios_factura.append({
                    'id': s[0], 'codigo': s[1], 'descripcion': s[2],
                    'cantidad': s[3], 'precio_unitario': s[4], 'subtotal': s[5]
                })
            self.update_servicios_table()
            self.calculate_total()
        conn.close()

    def update_factura(self):
        if not self.numero_edit.text():
            QMessageBox.warning(self, "Error", "Seleccione una factura para actualizar")
            return
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM facturas WHERE numero = ?", (self.numero_edit.text(),))
            result = cursor.fetchone()
            if not result:
                QMessageBox.warning(self, "Error", "Factura no encontrada")
                return
            factura_id = result[0]
            total = self.calculate_total()
            obra_social_id = self.obra_social_combo.currentData()
            cursor.execute('''
                UPDATE facturas SET paciente_id=?, obra_social_id=?, fecha=?, total=?, estado=?
                WHERE id=?
            ''', (
                self.paciente_combo.currentData(), obra_social_id,
                self.fecha_edit.date().toString("yyyy-MM-dd"),
                total, self.estado_combo.currentText(), factura_id
            ))
            cursor.execute("DELETE FROM detalle_facturas WHERE factura_id = ?", (factura_id,))
            for s in self.servicios_factura:
                cursor.execute('''
                    INSERT INTO detalle_facturas (factura_id, servicio_id, cantidad, precio_unitario, subtotal)
                    VALUES (?, ?, ?, ?, ?)
                ''', (factura_id, s['id'], s['cantidad'], s['precio_unitario'], s['subtotal']))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Éxito", "Factura actualizada correctamente")
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al actualizar factura: {str(e)}")

    def delete_factura(self):
        if not self.numero_edit.text():
            QMessageBox.warning(self, "Error", "Seleccione una factura para eliminar")
            return
        reply = QMessageBox.question(self, "Confirmar", "¿Está seguro de eliminar esta factura?")
        if reply == QMessageBox.Yes:
            try:
                conn = self.db_manager.get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM facturas WHERE numero = ?", (self.numero_edit.text(),))
                result = cursor.fetchone()
                if result:
                    factura_id = result[0]
                    cursor.execute("DELETE FROM detalle_facturas WHERE factura_id = ?", (factura_id,))
                    cursor.execute("DELETE FROM facturas WHERE id = ?", (factura_id,))
                    conn.commit()
                    conn.close()
                    QMessageBox.information(self, "Éxito", "Factura eliminada correctamente")
                    self.load_data()
                    self.clear_form()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al eliminar factura: {str(e)}")

    def clear_form(self):
        self.numero_edit.clear()
        self.paciente_combo.setCurrentIndex(0)
        self.obra_social_combo.setCurrentIndex(0)
        self.fecha_edit.setDate(QDate.currentDate())
        self.estado_combo.setCurrentIndex(0)
        self.servicios_factura = []
        self.update_servicios_table()
        self.calculate_total()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Sistema de Gestión Médica")
        self.setGeometry(100, 100, 1200, 800)
        
        # Widget central con pestañas
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # Crear pestañas
        self.tab_widget = QTabWidget()
        
        # Agregar pestañas
        self.pacientes_tab = PacientesTab(self.db_manager)
        self.profesionales_tab = ProfesionalesTab(self.db_manager)
        self.obras_sociales_tab = ObrasSocialesTab(self.db_manager)
        self.servicios_tab = ServiciosTab(self.db_manager)
        self.turnos_tab = TurnosTab(self.db_manager)
        self.agenda_tab = AgendaTab(self.db_manager)
        self.facturas_tab = FacturasTab(self.db_manager)
        
        self.tab_widget.addTab(self.pacientes_tab, "Pacientes")
        self.tab_widget.addTab(self.profesionales_tab, "Profesionales")
        self.tab_widget.addTab(self.obras_sociales_tab, "Obras Sociales")
        self.tab_widget.addTab(self.servicios_tab, "Servicios")
        self.tab_widget.addTab(self.turnos_tab, "Turnos")
        self.tab_widget.addTab(self.agenda_tab, "Agenda")
        self.tab_widget.addTab(self.facturas_tab, "Facturas")
        
        layout.addWidget(self.tab_widget)
        central_widget.setLayout(layout)
        
        # Barra de estado
        self.statusBar().showMessage("Sistema de Gestión Médica - Listo")
        
        # Timer para actualizar la hora
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(1000)  # Actualizar cada segundo
    
    def update_status(self):
        current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.statusBar().showMessage(f"Sistema de Gestión Médica - {current_time}")

def main():
    app = QApplication(sys.argv)
    
    # Configurar estilo de la aplicación
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
