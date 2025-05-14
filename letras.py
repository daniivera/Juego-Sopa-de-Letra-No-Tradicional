import random
import tkinter as tk
from tkinter import messagebox
from collections import defaultdict, deque

class SopaDeLetrasNoTradicional:
    def __init__(self, root):
        self.root = root
        self.root.title("Sopa de Letras No Tradicional")
        
        # Tamaño de la sopa de letras
        self.rows = 5
        self.cols = 6
        self.num_palabras = 7
        self.min_longitud_palabra = 3
        
        # Cargar palabras desde archivo
        self.palabras = self.cargar_palabras()
        self.prefijos = self.construir_arbol_prefijos()
        
        # Variables de control
        self.sopa = []
        self.palabras_encontradas = []
        self.celdas = []
    
        self.crear_interfaz()       # Interfaz gráfica
        self.generar_nueva_sopa()   # Generar nueva sopa de letras al iniciar

    
    def cargar_palabras(self):
        try:
            with open("castellano sin tildes.txt", "r", encoding="utf-8") as f:
                palabras = [line.strip().lower() for line in f if self.min_longitud_palabra <= len(line.strip()) <= 8]
            
            # Filtrar palabras que sean adecuadas para el tamaño de la sopa
            return [p.lower() for p in palabras if self.min_longitud_palabra <= len(p) <= 8]
            
        except FileNotFoundError:
            messagebox.showerror("Error", "Archivo de palabras no encontrado")
            return []
    
    def construir_arbol_prefijos(self):
        """Construye un árbol de prefijos para búsqueda eficiente de palabras"""
        arbol = defaultdict(set)
        for palabra in self.palabras:
            for i in range(1, len(palabra)+1):
                prefijo = palabra[:i]
                arbol[prefijo].add(palabra)
        return arbol
    
    def crear_interfaz(self):
        # Frame principal
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(pady=20)
        
        # Frame para la sopa de letras
        self.sopa_frame = tk.Frame(self.main_frame)
        self.sopa_frame.pack()
        
        # Crear celdas de la sopa de letras
        self.celdas = []
        for i in range(self.rows):
            row = []
            for j in range(self.cols):
                cell = tk.Label(self.sopa_frame, text="", width=3, height=1, 
                                font=('Arial', 16, 'bold'), relief='ridge')
                cell.grid(row=i, column=j, padx=2, pady=2)
                row.append(cell)
            self.celdas.append(row)
        
        # Botón para nueva sopa
        self.btn_nueva = tk.Button(self.main_frame, text="Nueva Sopa", 
                                  command=self.generar_nueva_sopa)
        self.btn_nueva.pack(pady=10)
        
        # Lista de palabras a encontrar
        self.lista_palabras = tk.Listbox(self.main_frame, height=10, width=20)
        self.lista_palabras.pack(pady=10)
    
    def generar_nueva_sopa(self):
        self.generar_sopa_aleatoria()
        self.buscar_palabras_en_sopa()
        
        # Si no encontramos suficientes palabras, regenerar
        intentos = 0
        while len(self.palabras_encontradas) < self.num_palabras and intentos < 10:
            self.generar_sopa_aleatoria()
            self.buscar_palabras_en_sopa()
            intentos += 1
        
        if len(self.palabras_encontradas) < self.num_palabras:
            messagebox.showwarning("Advertencia", 
                                 f"Solo se encontraron {len(self.palabras_encontradas)} palabras")
        
        # Seleccionar las primeras 7 palabras únicas ordenadas por longitud
        palabras_unicas = list({p.lower() for p in self.palabras_encontradas})
        palabras_unicas.sort(key=lambda x: -len(x))
        self.palabras_encontradas = palabras_unicas[:self.num_palabras]
        
        # Actualizar lista de palabras
        self.lista_palabras.delete(0, tk.END)
        for palabra in self.palabras_encontradas:
            self.lista_palabras.insert(tk.END, palabra.upper())
        
        # Mostrar la sopa en la interfaz
        self.mostrar_sopa()
    
    def generar_sopa_aleatoria(self):
        """Genera una sopa de letras con caminos aleatorios de letras conectadas"""
        # Inicializar con letras aleatorias
        letras = 'abcdefghijklmnopqrstuvwxyz'
        self.sopa = [[random.choice(letras) for _ in range(self.cols)] for _ in range(self.rows)]
        
        # Crear algunos caminos más largos para aumentar probabilidad de palabras
        for _ in range(3):
            self.crear_camino_aleatorio(random.randint(4, 6))
    
    def crear_camino_aleatorio(self, longitud):
        """Crea un camino aleatorio de letras conectadas"""
        # Elegir posición inicial aleatoria
        fila = random.randint(0, self.rows - 1)
        columna = random.randint(0, self.cols - 1)
        
        for _ in range(longitud):
            # Elegir una dirección aleatoria (arriba, abajo, izquierda, derecha)
            direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            random.shuffle(direcciones)
            
            for dr, dc in direcciones:
                nueva_fila, nueva_col = fila + dr, columna + dc
                if 0 <= nueva_fila < self.rows and 0 <= nueva_col < self.cols:
                    # Mover a la nueva posición
                    fila, columna = nueva_fila, nueva_col
                    
                    # Poner una letra aleatoria (podría ser la misma)
                    letras_comunes = 'aeiourslnmtcdp'
                    self.sopa[fila][columna] = random.choice(letras_comunes)
                    break
    
    def buscar_palabras_en_sopa(self):
        """Busca todas las palabras del diccionario en la sopa (adyacentes horizontal/vertical)"""
        self.palabras_encontradas = []
        visitadas = set()
        
        def dfs(fila, col, palabra_actual):
            if (fila, col) in visitadas:
                return
            
            palabra_actual += self.sopa[fila][col]
            
            # Si el prefijo no existe, no seguir buscando
            if palabra_actual not in self.prefijos:
                return
            
            # Si es una palabra completa, añadirla
            if palabra_actual in self.prefijos[palabra_actual]:
                if len(palabra_actual) >= self.min_longitud_palabra:
                    self.palabras_encontradas.append(palabra_actual)
            
            # Marcar como visitada
            visitadas.add((fila, col))
            
            # Explorar vecinos
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nueva_fila, nueva_col = fila + dr, col + dc
                if 0 <= nueva_fila < self.rows and 0 <= nueva_col < self.cols:
                    dfs(nueva_fila, nueva_col, palabra_actual)
            
            # Retroceder
            visitadas.remove((fila, col))
        
        # Buscar desde cada celda
        for i in range(self.rows):
            for j in range(self.cols):
                dfs(i, j, "")
    
    def mostrar_sopa(self):
        for i in range(self.rows):
            for j in range(self.cols):
                self.celdas[i][j].config(text=self.sopa[i][j].upper())

# Crear y ejecutar la aplicación
if __name__ == "__main__":
    root = tk.Tk()
    app = SopaDeLetrasNoTradicional(root)
    root.mainloop()