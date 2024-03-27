from datetime import datetime
import sqlite3
from sqlite3 import Error

class Producto:
  def __init__(self, nombre, cantidad, fecha_caducidad):
    self.nombre = nombre
    self.cantidad = cantidad
    self.fecha_caducidad = datetime.strptime(fecha_caducidad, '%Y-%m-%d')

class Pedido:
  def __init__(self, nombre_producto, cantidad):
    self.nombre_producto = nombre_producto
    self.cantidad = cantidad

class Inventario:
  def __init__(self, db_file):
    self.conn = self.create_connection(db_file)
    with self.conn:
      self.create_table()

  def create_connection(self, db_file):
    conn = None
    try:
      conn = sqlite3.connect(db_file)
    except Error as e:
      print(e)
    return conn

  def create_table(self):
    try:
      self.conn.execute("""
        CREATE TABLE IF NOT EXISTS productos (
          nombre text PRIMARY KEY,
          cantidad integer NOT NULL,
          fecha_caducidad text NOT NULL
        );
      """)
    except Error as e:
      print(e)

  def close_connection(self):
    self.conn.close()

  def agregar_producto(self, producto):
    try:
      self.conn.execute("""
        INSERT INTO productos(nombre, cantidad, fecha_caducidad)
        VALUES(?,?,?)
      """, (producto.nombre, producto.cantidad, producto.fecha_caducidad.strftime('%Y-%m-%d')))
      self.conn.commit()
    except Error as e:
      print(e)

  def quitar_producto(self, nombre):
    try:
      self.conn.execute("""
        DELETE FROM productos WHERE nombre = ?
      """, (nombre,))
      self.conn.commit()
    except Error as e:
      print(e)

  def actualizar_cantidad(self, nombre, cantidad):
    try:
      self.conn.execute("""
        UPDATE productos SET cantidad = ? WHERE nombre = ?
      """, (cantidad, nombre))
      self.conn.commit()
    except Error as e:
      print(e)

  def buscar_producto(self, nombre):
    cur = self.conn.cursor()
    cur.execute("SELECT * FROM productos WHERE nombre=?", (nombre,))
    rows = cur.fetchall()
    for row in rows:
      print(row)

  def buscar_por_nombre_parcial(self, nombre_parcial):
    cur = self.conn.cursor()
    cur.execute("SELECT * FROM productos WHERE nombre LIKE ?", (f'{nombre_parcial}%',))
    rows = cur.fetchall()
    for row in rows:
      print(row)

  def buscar_por_fecha_caducidad(self, fecha):
    fecha = datetime.strptime(fecha, '%Y-%m-%d')
    cur = self.conn.cursor()
    cur.execute("SELECT * FROM productos WHERE fecha_caducidad <= ?", (fecha.strftime('%Y-%m-%d'),))
    rows = cur.fetchall()
    for row in rows:
      print(row)

  def listar_productos(self):
    cur = self.conn.cursor()
    cur.execute("SELECT * FROM productos")
    rows = cur.fetchall()
    for row in rows:
      print(row)

  def agregar_pedido(self, pedido):
    producto = self.buscar_producto(pedido.nombre_producto)
    if producto and producto.cantidad >= pedido.cantidad:
      producto.cantidad -= pedido.cantidad
      self.actualizar_cantidad(producto.nombre, producto.cantidad)
    else:
      print(f"No hay suficiente cantidad de {pedido.nombre_producto} en el inventario.")

  def generar_informe(self):
    informe = "Informe de Inventario:\n"
    for producto in self.productos.values():
      informe += f"- {producto.nombre}: {producto.cantidad} en stock, caduca el {producto.fecha_caducidad}\n"
    return informe

# Crear inventario
inventario = Inventario(r"pythonsqlite.db")

# Crear productos
producto1 = Producto('Manzanas', 100, '2024-12-01')
producto2 = Producto('Naranjas', 50, '2024-11-01')

# Agregar productos al inventario
inventario.agregar_producto(producto1)
inventario.agregar_producto(producto2)

# Listar productos en el inventario
inventario.listar_productos()

# Buscar productos que caducan en o antes de una fecha específica
inventario.buscar_por_fecha_caducidad('2024-11-30')

# Buscar productos por nombre parcial
inventario.buscar_por_nombre_parcial('Man')

# Agregar un pedido
pedido = Pedido('Manzanas', 50)
inventario.agregar_pedido(pedido)

# Generar un informe
print(inventario.generar_informe())

# Cerrar la conexión a la base de datos
inventario.close_connection()