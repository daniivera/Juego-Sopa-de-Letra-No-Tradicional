import random
import tkinter as tk
from tkinter import messagebox
from collections import defaultdict, deque
import time

class SopaDeLetrasNoTradicional:
    def __init__(self, root):
        self.root = root
        self.root.title("Sopa de Letras No Tradicional")
        
        # Tamaño de la sopa de letras
        self.rows = 5
        self.cols = 6
        self.num_palabras = 7
        self.min_longitud_palabra = 3
        
        # Variables de juego
        self.tiempo_inicio = 0
        self.tiempo_pausado = 0
        self.tiempo_transcurrido = 0
        self.juego_pausado = False
        self.juego_oculto = False
        self.palabras_resueltas = 0
        self.partidas_jugadas = 0
        self.palabras_encontradas_total = 0
        
        # Cargar palabras desde archivo
        self.palabras = self.cargar_palabras()
        self.prefijos = self.construir_arbol_prefijos()
        
        # Variables de control
        self.sopa = []
        self.palabras_encontradas = []
        self.celdas = []
        self.seleccionadas = []
        self.letras_seleccionadas = []
        self.pistas = []
        
        self.crear_interfaz()       # Interfaz gráfica
        self.generar_nueva_sopa()   # Generar nueva sopa de letras al iniciar
        self.iniciar_temporizador()

    def cargar_palabras(self):
        try:
            with open("castellano sin tildes.txt", "r", encoding="utf-8") as f:
                palabras = [line.strip().lower() for line in f if 3 <= len(line.strip()) <= 9]  # Cambiado a 9
            
            return [p.lower() for p in palabras if 3 <= len(p) <= 9]  # Cambiado a 9
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
        
        # Barra de herramientas superior
        self.toolbar_frame = tk.Frame(self.main_frame)
        self.toolbar_frame.pack(fill=tk.X, pady=5)
        
        # Botón de ayuda
        self.btn_ayuda = tk.Menubutton(self.toolbar_frame, text="AYUDA ▼", relief=tk.RAISED)
        self.btn_ayuda.menu = tk.Menu(self.btn_ayuda, tearoff=0)
        self.btn_ayuda["menu"] = self.btn_ayuda.menu
        self.btn_ayuda.menu.add_command(label="Resolver", command=self.resolver_sopa)
        self.btn_ayuda.menu.add_command(label="Reiniciar", command=self.reiniciar_juego)
        self.btn_ayuda.menu.add_command(label="¿Cómo se juega?", command=self.mostrar_ayuda)
        self.btn_ayuda.pack(side=tk.LEFT, padx=5)
        
        # Temporizador
        self.tiempo_label = tk.Label(self.toolbar_frame, text="00:00", font=('Arial', 10, 'bold'))
        self.tiempo_label.pack(side=tk.LEFT, padx=10)
        
        # Botón de pausa/ocultar
        self.btn_pausa = tk.Button(self.toolbar_frame, text="❚❚ Ocultar", command=self.pausar_ocultar)
        self.btn_pausa.pack(side=tk.LEFT, padx=5)
        
        # Botón de estadísticas
        self.btn_stats = tk.Button(self.toolbar_frame, text="Mis estadísticas", command=self.mostrar_estadisticas)
        self.btn_stats.pack(side=tk.LEFT, padx=5)
        
        # Botón de guardar
        self.btn_guardar = tk.Button(self.toolbar_frame, text="Guardar", command=self.guardar_juego)
        self.btn_guardar.pack(side=tk.LEFT, padx=5)
        
        # Botón de salir
        self.btn_salir = tk.Button(self.toolbar_frame, text="→ Salir", command=self.salir)
        self.btn_salir.pack(side=tk.LEFT, padx=5)
        
        # Frame para la sopa de letras
        self.sopa_frame = tk.Frame(self.main_frame)
        self.sopa_frame.pack(pady=10)
        
        # Crear celdas de la sopa de letras
        self.celdas = []
        for i in range(self.rows):
            row = []
            for j in range(self.cols):
                cell = tk.Label(self.sopa_frame, text="", width=3, height=1, 
                              font=('Arial', 16, 'bold'), relief='ridge')
                cell.grid(row=i, column=j, padx=2, pady=2)
                cell.bind("<Button-1>", lambda e, i=i, j=j: self.seleccionar_celda(i, j))
                row.append(cell)
            self.celdas.append(row)
        
        # Frame para letras seleccionadas y botones
        self.seleccion_frame = tk.Frame(self.main_frame)
        self.seleccion_frame.pack(pady=10)
        
        self.letras_label = tk.Label(self.seleccion_frame, text="", font=('Arial', 14), width=30, relief='sunken')
        self.letras_label.pack(side=tk.LEFT, padx=5)
        
        self.btn_borrar = tk.Button(self.seleccion_frame, text="Borrar", command=self.borrar_seleccion)
        self.btn_borrar.pack(side=tk.LEFT, padx=5)
        
        self.btn_aplicar = tk.Button(self.seleccion_frame, text="Aplicar", command=self.aplicar_seleccion)
        self.btn_aplicar.pack(side=tk.LEFT, padx=5)
        
        # Frame para pistas
        self.pistas_frame = tk.Frame(self.main_frame)
        self.pistas_frame.pack(pady=10)
        
        self.pistas_label = tk.Label(self.pistas_frame, text="PISTAS:", font=('Arial', 12, 'bold'))
        self.pistas_label.pack(anchor=tk.W)
        
        self.pistas_texto = tk.Text(self.pistas_frame, height=10, width=30, font=('Arial', 10), wrap=tk.WORD)
        self.pistas_texto.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.pistas_scroll = tk.Scrollbar(self.pistas_frame, command=self.pistas_texto.yview)
        self.pistas_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.pistas_texto.config(yscrollcommand=self.pistas_scroll.set)
        self.pistas_texto.config(state=tk.DISABLED)
    
    def iniciar_temporizador(self):
        self.tiempo_inicio = time.time()
        self.actualizar_temporizador()
    
    def actualizar_temporizador(self):
        if not self.juego_pausado and not self.juego_oculto:
            tiempo_actual = time.time()
            self.tiempo_transcurrido = tiempo_actual - self.tiempo_inicio
            minutos = int(self.tiempo_transcurrido // 60)
            segundos = int(self.tiempo_transcurrido % 60)
            self.tiempo_label.config(text=f"{minutos:02d}:{segundos:02d}")
        self.root.after(1000, self.actualizar_temporizador)
    
    def pausar_ocultar(self):
        if not self.juego_pausado:
            # Pausar el juego
            self.juego_pausado = True
            self.tiempo_pausado = time.time()
            self.btn_pausa.config(text="▶ Mostrar")
            self.ocultar_juego()
        else:
            # Reanudar el juego
            self.juego_pausado = False
            self.tiempo_inicio += (time.time() - self.tiempo_pausado)
            self.btn_pausa.config(text="❚❚ Ocultar")
            self.mostrar_juego()
    
    def ocultar_juego(self):
        self.juego_oculto = True
        self.sopa_frame.pack_forget()
        self.seleccion_frame.pack_forget()
        self.pistas_frame.pack_forget()
    
    def mostrar_juego(self):
        self.juego_oculto = False
        self.sopa_frame.pack(pady=10)
        self.seleccion_frame.pack(pady=10)
        self.pistas_frame.pack(pady=10)
    
    def seleccionar_celda(self, fila, col):
        if self.juego_pausado or self.juego_oculto:
            return
            
        celda = self.celdas[fila][col]
        if (fila, col) in self.seleccionadas:
            # Deseleccionar
            self.seleccionadas.remove((fila, col))
            self.letras_seleccionadas.remove(celda.cget("text").lower())
            celda.config(bg='SystemButtonFace')
        else:
            # Seleccionar
            self.seleccionadas.append((fila, col))
            self.letras_seleccionadas.append(celda.cget("text").lower())
            celda.config(bg='lightblue')
        
        # Actualizar label de letras seleccionadas
        self.letras_label.config(text=" ".join([l.upper() for l in self.letras_seleccionadas]))
    
    def borrar_seleccion(self):
        for fila, col in self.seleccionadas:
            self.celdas[fila][col].config(bg='light gray')
        self.seleccionadas = []
        self.letras_seleccionadas = []
        self.letras_label.config(text="")
    
    def aplicar_seleccion(self):
        palabra = "".join(self.letras_seleccionadas)
        if palabra in self.palabras_encontradas:
            # Marcar como resuelta
            for fila, col in self.seleccionadas:
                self.celdas[fila][col].config(bg='lightgreen')
            
            # Actualizar pistas
            self.actualizar_pistas(palabra)
            
            # Incrementar contador
            self.palabras_resueltas += 1
            self.palabras_encontradas_total += 1
            
            # Verificar si se completó el juego
            if self.palabras_resueltas == len(self.palabras_encontradas):
                self.partidas_jugadas += 1
                messagebox.showinfo("¡Felicidades!", f"¡Has completado la sopa de letras en {self.tiempo_label.cget('text')}!")
        else:
            messagebox.showwarning("Palabra no válida", "La palabra seleccionada no está en la lista.")
        
        self.borrar_seleccion()
    
    def actualizar_pistas(self, palabra_resuelta):
        self.pistas_texto.config(state=tk.NORMAL)
        self.pistas_texto.delete(1.0, tk.END)
        
        # Agrupar palabras por longitud
        palabras_por_longitud = defaultdict(list)
        for palabra in self.palabras_encontradas:
            if palabra != palabra_resuelta:
                palabras_por_longitud[len(palabra)].append(palabra)
        
        # Mostrar pistas
        for longitud in sorted(palabras_por_longitud.keys(), reverse=True):
            palabras = palabras_por_longitud[longitud]
            self.pistas_texto.insert(tk.END, f"{len(palabras)} DE {longitud} LETRAS\n", 'titulo')
            for palabra in palabras:
                pista = f"[ {palabra[0].upper()} ] " + "_ " * (len(palabra)-1) + "\n"
                self.pistas_texto.insert(tk.END, pista)
            self.pistas_texto.insert(tk.END, "\n")
        
        self.pistas_texto.tag_config('titulo', font=('Arial', 10, 'bold'))
        self.pistas_texto.config(state=tk.DISABLED)
    
    def generar_nueva_sopa(self):
        intentos = 0
        while intentos < 20:  # Aumentamos los intentos
            self.generar_sopa_aleatoria()
            self.buscar_palabras_en_sopa()
            
            # Verificar que tengamos palabras de diferentes longitudes
            longitudes = set(len(p) for p in self.palabras_encontradas)
            if len(self.palabras_encontradas) >= self.num_palabras and len(longitudes) >= 3:
                break
            intentos += 1
        # Seleccionar las primeras 7 palabras únicas ordenadas por longitud
        palabras_unicas = list({p.lower() for p in self.palabras_encontradas})
        palabras_unicas.sort(key=lambda x: -len(x))
        self.palabras_encontradas = palabras_unicas[:self.num_palabras]
        
        # Reiniciar estado del juego
        self.palabras_resueltas = 0
        self.seleccionadas = []
        self.letras_seleccionadas = []
        self.letras_label.config(text="")
        
        # Actualizar pistas
        self.actualizar_pistas("")
        
        # Mostrar la sopa en la interfaz
        self.mostrar_sopa()
    
    def generar_sopa_aleatoria(self):
        # Letras con mayor frecuencia en español para palabras más largas
        letras_frecuentes = 'aeiourslnmtcdpbgvhqyfj'
        self.sopa = [[random.choice(letras_frecuentes) for _ in range(self.cols)] 
                    for _ in range(self.rows)]
        
        # Crear caminos más largos (de 6 a 9 letras)
        for _ in range(4):  # Aumentamos el número de caminos
            longitud = random.choice([6, 7, 8, 9])  # Longitudes variadas
            self.crear_camino_aleatorio(longitud)

    def crear_camino_aleatorio(self, longitud):
        fila = random.randint(0, self.rows - 1)
        columna = random.randint(0, self.cols - 1)
        
        # Letras que favorecen la formación de palabras más largas
        letras_comunes = 'aeiourslnmtcdp'
        consonantes_comunes = 'bcdfghjklmnñpqrstvwxyz'
        
        for paso in range(longitud):
            # Alternar entre vocales y consonantes
            if paso % 2 == 0:
                letra = random.choice(letras_comunes)
            else:
                letra = random.choice(consonantes_comunes)
            
            self.sopa[fila][columna] = letra
            
            # Elegir dirección con preferencia por continuar en la misma dirección
            direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            random.shuffle(direcciones)
            
            for dr, dc in direcciones:
                nueva_fila, nueva_col = fila + dr, columna + dc
                if 0 <= nueva_fila < self.rows and 0 <= nueva_col < self.cols:
                    fila, columna = nueva_fila, nueva_col
                    break
    
    def buscar_palabras_en_sopa(self):
        self.palabras_encontradas = []
        
        # Primero buscar palabras largas (7-9 letras)
        for palabra in self.palabras:
            if 7 <= len(palabra) <= 9:
                if self.palabra_en_sopa(palabra):
                    self.palabras_encontradas.append(palabra)
        
        # Luego palabras medias (5-6 letras)
        for palabra in self.palabras:
            if 5 <= len(palabra) <= 6 and palabra not in self.palabras_encontradas:
                if self.palabra_en_sopa(palabra):
                    self.palabras_encontradas.append(palabra)
        
        # Finalmente palabras cortas (3-4 letras) si no hay suficientes
        if len(self.palabras_encontradas) < self.num_palabras:
            for palabra in self.palabras:
                if 3 <= len(palabra) <= 4 and palabra not in self.palabras_encontradas:
                    if self.palabra_en_sopa(palabra):
                        self.palabras_encontradas.append(palabra)
                        if len(self.palabras_encontradas) >= self.num_palabras:
                            break

    def palabra_en_sopa(self, palabra):
        """Verifica si una palabra específica está en la sopa"""
        for i in range(self.rows):
            for j in range(self.cols):
                if self.encontrar_palabra_desde(i, j, palabra):
                    return True
        return False
    
    def mostrar_sopa(self):
        for i in range(self.rows):
            for j in range(self.cols):
                self.celdas[i][j].config(text=self.sopa[i][j].upper(), bg='light gray')
    
    def resolver_sopa(self):
        for palabra in self.palabras_encontradas:
            encontrada = False
            # Buscar la palabra en la sopa
            for i in range(self.rows):
                for j in range(self.cols):
                    if self.encontrar_palabra_desde(i, j, palabra):
                        encontrada = True
                        break
                if encontrada:
                    break
    
    def encontrar_palabra_desde(self, fila, col, palabra):
        """Intenta encontrar la palabra desde una posición específica"""
        visitadas = set()
        direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        def dfs(f, c, indice):
            if indice == len(palabra):
                return True
            if (f, c) in visitadas or not (0 <= f < self.rows and 0 <= c < self.cols):
                return False
            if self.sopa[f][c] != palabra[indice]:
                return False
                
            visitadas.add((f, c))
            for dr, dc in direcciones:
                if dfs(f + dr, c + dc, indice + 1):
                    return True
            visitadas.remove((f, c))
            return False
        
        if dfs(fila, col, 0):
            for f, c in visitadas:
                self.celdas[f][c].config(bg='lightgreen')
            return True
        return False
    
    def reiniciar_juego(self):
        self.generar_nueva_sopa()
        self.tiempo_inicio = time.time()
        self.tiempo_transcurrido = 0
        self.juego_pausado = False
        self.juego_oculto = False
        self.btn_pausa.config(text="❚❚ Ocultar")
        self.mostrar_juego()
    
    def mostrar_ayuda(self):
        ayuda = """
        CÓMO JUGAR:
        
        1. Selecciona letras adyacentes (horizontal o vertical) para formar palabras.
        2. Las letras seleccionadas se mostrarán en la parte inferior.
        3. Presiona 'Aplicar' para verificar si la palabra seleccionada es correcta.
        4. Usa 'Borrar' para deseleccionar todas las letras.
        5. Encuentra todas las palabras para completar el juego.
        
        OPCIONES:
        - Pausar/Ocultar: Pausa el temporizador y oculta el juego.
        - Resolver: Muestra todas las palabras en la sopa.
        - Reiniciar: Genera una nueva sopa de letras.
        """
        messagebox.showinfo("Cómo se juega", ayuda)
    
    def mostrar_estadisticas(self):
        stats = f"""
        ESTADÍSTICAS:
        
        Partidas jugadas: {self.partidas_jugadas}
        Palabras encontradas: {self.palabras_encontradas_total}
        Tiempo promedio: {(self.tiempo_transcurrido / self.partidas_jugadas) if self.partidas_jugadas > 0 else 0:.2f} segundos
        """
        messagebox.showinfo("Mis estadísticas", stats)
    
    def guardar_juego(self):
        # En una implementación real, aquí se guardaría el estado del juego
        messagebox.showinfo("Guardar", "Juego guardado correctamente.")
    
    def salir(self):
        if messagebox.askokcancel("Salir", "¿Estás seguro de que quieres salir?"):
            self.root.destroy()

# Crear y ejecutar la aplicación
if __name__ == "__main__":
    root = tk.Tk()
    app = SopaDeLetrasNoTradicional(root)
    root.mainloop()
