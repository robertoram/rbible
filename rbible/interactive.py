#!/usr/bin/env python3
"""
Interactive mode for rbible
"""

import curses
from curses import wrapper
from rbible.bible_data import get_available_versions, load_bible_version
from rbible.verse_operations import parse_reference, get_verse, search_bible
from rbible.user_data import save_to_history, save_to_favorites, show_favorites

class InteractiveRBible:
    def __init__(self, stdscr, version=None):
        self.stdscr = stdscr
        self.version = version
        self.current_book = "Génesis"
        self.current_chapter = 1
        self.current_verse = 1
        self.bible_conn = None
        
    def setup(self):
        """Setup the screen and load Bible version"""
        curses.curs_set(0)  # Hide cursor
        self.stdscr.clear()
        
        # Set up colors
        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)  # Header
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Selected item
        curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_BLACK)    # Palabras de Jesús
        
        # Load Bible version
        if not self.version:
            try:
                # Intentar cargar la versión por defecto
                from rbible.user_data import get_default_version
                self.version = get_default_version()
                
                # Si aún no hay versión, intentar obtener la primera disponible
                if not self.version:
                    available_versions = get_available_versions()
                    if available_versions:
                        self.version = available_versions[0]
                    else:
                        self.show_message("No Bible versions found. Please add Bible SQLite files.")
                        return False
            except Exception as e:
                # Capturar cualquier error y mostrar un mensaje
                self.show_message(f"Error loading Bible version: {e}")
                
                # Intentar obtener cualquier versión disponible como último recurso
                try:
                    available_versions = get_available_versions()
                    if available_versions:
                        self.version = available_versions[0]
                    else:
                        return False
                except:
                    return False
        
        # Intentar cargar la versión seleccionada
        try:
            self.bible_conn = load_bible_version(self.version)
            return True
        except Exception as e:
            self.show_message(f"Error loading Bible version '{self.version}': {e}")
            return False
    
    def main_menu(self):
        """Display the main menu and handle user input"""
        menu_items = [
            "Read Bible [r]",
            "Search Text [s]",
            "View Favorites [f]",
            "View History [h]",
            "Change Version [v]",
            "Exit [q]"
        ]
        
        # ASCII art logo for rbible
        logo = [
            "    ____  __    _ __    __     ",
            "   / __ \\/ /_  (_) /_  / /__   ",
            "  / /_/ / __ \\/ / __ \\/ / _ \\  ",
            " / _, _/ /_/ / / /_/ / /  __/  ",
            "/_/ |_/_.___/_/_.___/_/\\___/   ",
            "                               ",
            "  Command-line Bible Reader    ",
            "  Created by Roberto Ramirez   "
        ]
        
        current_row = 0
        
        while True:
            self.stdscr.clear()
            h, w = self.stdscr.getmaxyx()
            
            # Draw header
            header = f" rbible Interactive Mode - {self.version} "
            header = header.center(w-1)  # Adjust to prevent writing to last column
            self.stdscr.attron(curses.color_pair(1))
            self.stdscr.addstr(0, 0, header[:w-1])  # Prevent writing to last column
            self.stdscr.attroff(curses.color_pair(1))
            
            # Draw logo
            logo_start_y = 2
            for i, line in enumerate(logo):
                if logo_start_y + i < h-1:
                    x = w//2 - len(line)//2
                    self.stdscr.addstr(logo_start_y + i, x, line[:w-x-1])
            
            # Draw menu items with more spacing
            menu_start_y = logo_start_y + len(logo) + 2  # Start menu after logo with some space
            for idx, item in enumerate(menu_items):
                # Make menu items bigger
                display_item = f"   {item}   "
                x = w//2 - len(display_item)//2
                y = menu_start_y + (idx * 2)  # Double spacing between items
                
                if y >= h-1:
                    break
                    
                if idx == current_row:
                    self.stdscr.attron(curses.color_pair(2))
                    self.stdscr.addstr(y, x, display_item[:w-x-1])  # Prevent overflow
                    self.stdscr.attroff(curses.color_pair(2))
                else:
                    self.stdscr.addstr(y, x, display_item[:w-x-1])  # Prevent overflow
            
            # Draw footer - avoid writing to the bottom-right corner
            footer = " Use arrow keys to navigate, Enter to select "
            footer = footer.center(w-1)  # Adjust to prevent writing to last column
            if h > 1:  # Make sure we have enough space
                self.stdscr.addstr(h-1, 0, footer[:w-1])  # Prevent writing to last column
            
            # Handle key presses
            key = self.stdscr.getch()
            
            if key == curses.KEY_UP and current_row > 0:
                current_row -= 1
            elif key == curses.KEY_DOWN and current_row < len(menu_items) - 1:
                current_row += 1
            elif key == curses.KEY_ENTER or key in [10, 13]:
                # Handle menu selection
                if current_row == 0:  # Read Bible
                    self.read_bible()
                elif current_row == 1:  # Search Text
                    self.search_text()
                elif current_row == 2:  # View Favorites
                    self.view_favorites()
                elif current_row == 3:  # View History
                    self.view_history()
                elif current_row == 4:  # Change Version
                    self.change_version()
                elif current_row == 5:  # Exit
                    break
            # Añadir atajos de teclado
            elif key == ord('r'):  # Read Bible shortcut
                self.read_bible()
            elif key == ord('s'):  # Search Text shortcut
                self.search_text()
            elif key == ord('f'):  # View Favorites shortcut
                self.view_favorites()
            elif key == ord('h'):  # View History shortcut
                self.view_history()
            elif key == ord('v'):  # Change Version shortcut
                self.change_version()
            elif key == ord('q'):  # Exit shortcut
                break
    
    def read_bible(self):
        """Bible reading interface"""
        # Verificar si hay una versión cargada
        if not self.bible_conn:
            # Si no hay versión cargada, mostrar mensaje y permitir seleccionar una
            self.show_message("No Bible version loaded. Please select a version first.")
            self.change_version()
            
            # Si después de intentar cambiar la versión aún no hay conexión, salir
            if not self.bible_conn:
                return
        
        # Variables para el scroll
        scroll_position = 0
        all_lines = []
        
        while True:
            try:
                self.stdscr.clear()
                h, w = self.stdscr.getmaxyx()
                
                # Draw header
                header = f" {self.current_book} {self.current_chapter} - {self.version} "
                header = header.center(w-1)  # Adjust to prevent writing to last column
                self.stdscr.attron(curses.color_pair(1))
                self.stdscr.addstr(0, 0, header[:w-1])  # Prevent writing to last column
                self.stdscr.attroff(curses.color_pair(1))
                
                # Get and display verses
                try:
                    # Solo procesar el texto si all_lines está vacío (primera carga o cambio de capítulo)
                    if not all_lines:
                        # Obtener versículos individuales en lugar del capítulo completo
                        verses = []
                        max_verses = 200  # Número máximo de versículos a intentar
                        
                        try:
                            # Primero intentar obtener el capítulo completo
                            chapter_text = get_verse(self.bible_conn, self.current_book, 
                                                   self.current_chapter, (1, max_verses), 
                                                   format_style='plain')
                            
                            if chapter_text:
                                # Eliminar etiquetas <pb/> si existen
                                chapter_text = chapter_text.replace("<pb/>", "").strip()
                                
                                # Procesar etiquetas de formato
                                import re
                                
                                # Intentar dividir el texto en versículos basados en patrones comunes
                                potential_verses = re.split(r'\.\s+', chapter_text)
                                
                                # Si tenemos al menos algunos versículos potenciales, usarlos
                                if len(potential_verses) > 1:
                                    for i, v_text in enumerate(potential_verses):
                                        if v_text.strip():
                                            verses.append((i+1, v_text.strip() + "."))
                                else:
                                    # Si no podemos dividir, mostrar como un solo versículo
                                    verses.append((1, chapter_text))
                        except Exception as e:
                            self.stdscr.addstr(2, 2, f"Error getting chapter: {e}")
                            verses = []
                        
                        # Si no se encontraron versículos, intentar obtener versículos individuales
                        if not verses:
                            for verse_num in range(1, max_verses):
                                try:
                                    # Intentar obtener cada versículo individualmente
                                    verse_text = get_verse(self.bible_conn, self.current_book, 
                                                          self.current_chapter, verse_num, 
                                                          format_style='plain')
                                    
                                    if verse_text and verse_text.strip():
                                        # Procesar el texto del versículo
                                        plain_verse_text = self.process_verse_text(verse_text)
                                        verses.append((verse_num, plain_verse_text))
                                    else:
                                        # Si no hay texto, probablemente llegamos al final del capítulo
                                        break
                                except Exception:
                                    # Si hay error al obtener el versículo, probablemente llegamos al final
                                    break
                        
                        # Procesar todos los versículos y guardar las líneas formateadas
                        all_lines = []
                        
                        if verses:
                            for verse_num, verse_text in verses:
                                # Resaltar el número del versículo
                                verse_header = f"{verse_num}. "
                                
                                # Usar la nueva función para formatear el versículo
                                # Calcular el ancho disponible para el texto
                                available_width = w - 3 - len(verse_header) - 3
                                
                                # Obtener las líneas formateadas
                                verse_lines = []
                                formatted_lines = self.format_verse_for_display(verse_text, available_width)
                                
                                # Primera línea con número de versículo
                                if formatted_lines:
                                    verse_lines.append((True, formatted_lines[0]))
                                    # Resto de líneas
                                    for line in formatted_lines[1:]:
                                        verse_lines.append((False, line))
                                
                                # Agregar las líneas del versículo a all_lines
                                for is_first, line_text in verse_lines:
                                    all_lines.append((verse_num, is_first, line_text))
                                
                                # Agregar una línea en blanco entre versículos para mejor legibilidad
                                all_lines.append((None, None, ""))
                        else:
                            all_lines.append((None, None, "No verses found for this chapter."))
                    
                    # Mostrar las líneas según la posición de scroll
                    display_lines = min(h - 4, len(all_lines) - scroll_position)  # -4 para header y footer
                    
                    for i in range(display_lines):
                        line_idx = scroll_position + i
                        if line_idx < len(all_lines):
                            # Extraer los valores correctamente - SIMPLIFICADO
                            verse_num, is_first, line_text = all_lines[line_idx]
                            
                            if verse_num is not None and is_first:
                                # Línea con número de versículo
                                verse_header = f"{verse_num}. "
                                self.stdscr.attron(curses.A_BOLD)
                                self.stdscr.addstr(i + 2, 3, verse_header)
                                self.stdscr.attroff(curses.A_BOLD)
                                
                                # Usar la función de formato para mostrar el texto
                                max_text_width = w - 3 - len(verse_header) - 3
                                self.display_formatted_text(i + 2, 3 + len(verse_header), 
                                                           line_text, max_text_width)
                            elif verse_num is not None:
                                # Línea continuada de un versículo - alineada con la primera línea
                                indent = 3 + len(f"{verse_num}. ")  # Misma posición que la primera línea
                                
                                # Usar la función de formato para mostrar el texto
                                max_text_width = w - indent - 3
                                self.display_formatted_text(i + 2, indent, line_text, max_text_width)
                            else:
                                # Línea en blanco o mensaje
                                self.stdscr.addstr(i + 2, 3, line_text[:w - 6])
                    
                    # Indicadores de scroll si hay más contenido
                    if scroll_position > 0:
                        self.stdscr.addstr(1, w // 2, "↑ More ↑")
                    if scroll_position + display_lines < len(all_lines):
                        self.stdscr.addstr(h - 2, w // 2, "↓ More ↓")
                
                except Exception as e:
                    self.stdscr.addstr(2, 2, f"Error displaying verses: {str(e)}")
                
                # Draw footer with commands
                footer = " [↑/↓] Scroll | [←/→] Prev/Next Chapter | [g] Go to | [f] Add to Favorites | [q] Back to Menu "
                footer = footer.center(w-1)  # Adjust to prevent writing to last column
                if h > 1:  # Make sure we have enough space
                    self.stdscr.addstr(h-1, 0, footer[:w-1])  # Prevent writing to last column
                
                # Handle key presses
                key = self.stdscr.getch()
                
                if key == curses.KEY_UP:  # Scroll up
                    scroll_position = max(0, scroll_position - 1)
                elif key == curses.KEY_DOWN:  # Scroll down
                    if scroll_position + display_lines < len(all_lines):
                        scroll_position += 1
                elif key == curses.KEY_PPAGE:  # Page up
                    scroll_position = max(0, scroll_position - (h - 4))
                elif key == curses.KEY_NPAGE:  # Page down
                    scroll_position = min(len(all_lines) - display_lines, scroll_position + (h - 4))
                    if scroll_position < 0:  # En caso de que haya menos líneas que la pantalla
                        scroll_position = 0
                elif key == curses.KEY_LEFT:  # Previous chapter
                    self.current_chapter = max(1, self.current_chapter - 1)
                    scroll_position = 0  # Reset scroll position
                    all_lines = []  # Clear cached lines
                elif key == curses.KEY_RIGHT:  # Next chapter
                    self.current_chapter += 1
                    scroll_position = 0  # Reset scroll position
                    all_lines = []  # Clear cached lines
                elif key == ord('g'):  # Go to specific reference
                    self.go_to_reference()
                    scroll_position = 0  # Reset scroll position
                    all_lines = []  # Clear cached lines
                elif key == ord('f'):  # Add to favorites
                    self.add_to_favorites()
                elif key == ord('q'):  # Back to menu
                    break
            except Exception as e:
                # Capturar cualquier error no manejado para evitar que la aplicación se cierre
                self.show_message(f"Unexpected error: {str(e)}")
                break
    
    def search_text(self):
        """Search for text in the Bible"""
        # Placeholder implementation
        self.show_message("Search feature coming soon!")
    
    def view_favorites(self):
        """View favorite verses"""
        self.stdscr.clear()
        h, w = self.stdscr.getmaxyx()
        
        # Draw header
        header = " Favorite Verses "
        header = header.center(w-1)
        self.stdscr.attron(curses.color_pair(1))
        self.stdscr.addstr(0, 0, header[:w-1])
        self.stdscr.attroff(curses.color_pair(1))
        
        # Get favorites
        favorites = []
        try:
            import json
            import os
            favorites_file = os.path.expanduser("~/.rbible/favorites.json")
            if os.path.exists(favorites_file):
                with open(favorites_file, 'r') as f:
                    favorites = json.load(f)
        except Exception as e:
            self.stdscr.addstr(2, 2, f"Error loading favorites: {e}")
        
        # Display favorites
        if favorites:
            for i, fav in enumerate(favorites):
                if i+2 >= h-2:
                    break
                ref = fav.get('reference', 'Unknown')
                name = fav.get('name', '')
                display = f"{i+1}. {ref} - {name}" if name else f"{i+1}. {ref}"
                self.stdscr.addstr(i+2, 2, display[:w-4])
        else:
            self.stdscr.addstr(2, 2, "No favorites found.")
        
        # Footer
        footer = " Press any key to return to menu "
        footer = footer.center(w-1)
        if h > 1:
            self.stdscr.addstr(h-1, 0, footer[:w-1])
        
        # Wait for key press
        self.stdscr.getch()
    
    def view_history(self):
        """View verse history"""
        self.stdscr.clear()
        h, w = self.stdscr.getmaxyx()
        
        # Draw header
        header = " Verse History "
        header = header.center(w-1)
        self.stdscr.attron(curses.color_pair(1))
        self.stdscr.addstr(0, 0, header[:w-1])
        self.stdscr.attroff(curses.color_pair(1))
        
        # Get history
        history = []
        try:
            import json
            import os
            history_file = os.path.expanduser("~/.rbible/history.json")
            if os.path.exists(history_file):
                with open(history_file, 'r') as f:
                    history = json.load(f)
        except Exception as e:
            self.stdscr.addstr(2, 2, f"Error loading history: {e}")
        
        # Display history
        if history:
            for i, item in enumerate(history[:10]):  # Show last 10 items
                if i+2 >= h-2:
                    break
                ref = item.get('reference', 'Unknown')
                version = item.get('version', '')
                display = f"{i+1}. {ref} ({version})"
                self.stdscr.addstr(i+2, 2, display[:w-4])
        else:
            self.stdscr.addstr(2, 2, "No history found.")
        
        # Footer
        footer = " Press any key to return to menu "
        footer = footer.center(w-1)
        if h > 1:
            self.stdscr.addstr(h-1, 0, footer[:w-1])
        
        # Wait for key press
        self.stdscr.getch()
    
    def change_version(self):
        """Change Bible version"""
        self.stdscr.clear()
        h, w = self.stdscr.getmaxyx()
        
        # Get available versions and sort them alphabetically
        versions = get_available_versions()
        versions.sort()  # Ordenar alfabéticamente
        
        if not versions:
            self.show_message("No Bible versions found.")
            return
        
        current_row = 0
        current_col = 0
        if self.version in versions:
            current_idx = versions.index(self.version)
            # Calcular fila y columna basado en el índice
            cols_per_screen = max(1, (w - 10) // 20)  # Ancho aproximado de 20 caracteres por columna
            current_row = current_idx % (h - 6)  # Filas disponibles (descontando header y footer)
            current_col = current_idx // (h - 6)
        
        # Variables para el scroll horizontal
        col_offset = 0
        
        # Display versions
        while True:
            self.stdscr.clear()
            
            # Draw header
            header = " Select Bible Version "
            header = header.center(w-1)
            self.stdscr.attron(curses.color_pair(1))
            self.stdscr.addstr(0, 0, header[:w-1])
            self.stdscr.attroff(curses.color_pair(1))
            
            # Calcular el número de columnas y filas
            cols_per_screen = max(1, (w - 10) // 20)  # Ancho aproximado de 20 caracteres por columna
            rows_per_screen = h - 6  # Descontar header, footer y márgenes
            
            # Dibujar versiones en columnas
            for col in range(cols_per_screen):
                col_idx = col + col_offset
                col_x = 4 + (col * 20)  # Posición X de la columna
                
                for row in range(rows_per_screen):
                    version_idx = col_idx * rows_per_screen + row
                    
                    if version_idx < len(versions):
                        version = versions[version_idx]
                        
                        # Resaltar la versión seleccionada
                        if row == current_row and col_idx == current_col:
                            self.stdscr.attron(curses.color_pair(2))
                            self.stdscr.addstr(row + 2, col_x, version[:18])  # Limitar a 18 caracteres
                            self.stdscr.attroff(curses.color_pair(2))
                        else:
                            self.stdscr.addstr(row + 2, col_x, version[:18])
            
            # Indicadores de scroll horizontal si hay más columnas
            total_cols = (len(versions) + rows_per_screen - 1) // rows_per_screen
            if col_offset > 0:
                self.stdscr.addstr(h // 2, 1, "←")
            if col_offset + cols_per_screen < total_cols:
                self.stdscr.addstr(h // 2, w - 2, "→")
            
            # Footer
            footer = " Use ↑↓←→ to navigate, Enter to select, q to cancel "
            footer = footer.center(w-1)
            if h > 1:
                self.stdscr.addstr(h-1, 0, footer[:w-1])
            
            # Handle key presses
            key = self.stdscr.getch()
            
            if key == curses.KEY_UP and current_row > 0:
                current_row -= 1
            elif key == curses.KEY_DOWN:
                next_idx = (current_col * rows_per_screen) + current_row + 1
                if next_idx < len(versions) and current_row < rows_per_screen - 1:
                    current_row += 1
            elif key == curses.KEY_LEFT:
                if current_col > 0:
                    current_col -= 1
                    if current_col < col_offset:
                        col_offset = max(0, col_offset - 1)
            elif key == curses.KEY_RIGHT:
                next_col = current_col + 1
                next_idx = (next_col * rows_per_screen) + current_row
                if next_idx < len(versions):
                    current_col += 1
                    if current_col >= col_offset + cols_per_screen:
                        col_offset += 1
            elif key == curses.KEY_ENTER or key in [10, 13]:
                # Calcular el índice de la versión seleccionada
                selected_idx = (current_col * rows_per_screen) + current_row
                if selected_idx < len(versions):
                    # Change version
                    self.version = versions[selected_idx]
                    if self.bible_conn:
                        self.bible_conn.close()
                    self.bible_conn = load_bible_version(self.version)
                    break
            elif key == ord('q'):
                break
    
    def go_to_reference(self):
        """Go to a specific Bible reference"""
        h, w = self.stdscr.getmaxyx()
        
        # Crear una ventana más pequeña para la entrada de texto
        input_width = min(40, w-10)  # Ancho máximo de 40 o el ancho disponible
        input_win = curses.newwin(3, input_width, h//2-2, (w-input_width)//2)
        
        # Configurar colores para la ventana - fondo negro
        input_win.bkgd(' ', curses.A_NORMAL)  # Fondo negro normal
        
        # Dibujar borde azul manualmente
        curses.init_pair(5, curses.COLOR_BLUE, curses.COLOR_BLACK)  # Borde azul sobre fondo negro
        input_win.attron(curses.color_pair(5))
        input_win.box()
        input_win.attroff(curses.color_pair(5))
        
        # Título de la ventana en azul
        title = " Enter Bible Reference "
        input_win.attron(curses.color_pair(5))
        input_win.addstr(0, (input_width - len(title))//2, title)
        input_win.attroff(curses.color_pair(5))
        
        # Crear una subventana para la entrada de texto (sin el borde)
        text_win = input_win.derwin(1, input_width-4, 1, 2)
        
        # Configurar para entrada de texto
        curses.echo()
        curses.curs_set(1)  # Mostrar cursor
        
        # Inicializar color verde brillante para el texto de entrada
        curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
        text_win.attron(curses.color_pair(4))
        
        # Obtener entrada del usuario
        input_win.refresh()
        text_win.refresh()
        input_text = text_win.getstr(0, 0, input_width-6).decode('utf-8')
        
        # Restaurar configuración
        curses.noecho()
        curses.curs_set(0)  # Ocultar cursor
        
        # Procesar la referencia
        if input_text.strip():
            try:
                # Intentar analizar la referencia
                book, chapter, verse = parse_reference(input_text)
                
                # Verificar si el libro existe
                if book:
                    # Actualizar la referencia actual
                    self.current_book = book
                    self.current_chapter = chapter
                    self.current_verse = verse
                    
                    # Guardar en el historial
                    try:
                        save_to_history(book, chapter, verse, self.version)
                    except Exception:
                        pass  # Ignorar errores al guardar en el historial
                    
                    return True
                else:
                    self.show_message(f"Book not found: {input_text}")
            except Exception as e:
                self.show_message(f"Invalid reference: {input_text}\nError: {str(e)}")
        
        return False
    
    def add_to_favorites(self):
        """Add current chapter/verse to favorites"""
        # Placeholder implementation
        self.show_message("Add to favorites feature coming soon!")
    
    def show_message(self, message):
        """Show a message to the user"""
        h, w = self.stdscr.getmaxyx()
        
        # Calculate message box dimensions
        box_height = 5
        box_width = len(message) + 6
        box_y = h // 2 - box_height // 2
        box_x = w // 2 - box_width // 2
        
        # Draw message box
        for i in range(box_height):
            for j in range(box_width):
                if i == 0 or i == box_height - 1 or j == 0 or j == box_width - 1:
                    self.stdscr.addch(box_y + i, box_x + j, curses.ACS_CKBOARD)
        
        # Draw message
        self.stdscr.addstr(box_y + 2, box_x + 3, message[:box_width-6])
        
        # Draw footer
        footer = " Press any key to continue "
        footer_x = w // 2 - len(footer) // 2
        self.stdscr.addstr(box_y + box_height, footer_x, footer[:w-footer_x-1])
        
        # Wait for key press
        self.stdscr.getch()
    
    def process_verse_text(self, verse_text):
        """Procesa el texto del versículo y elimina o formatea etiquetas"""
        # Eliminar etiquetas <pb/>
        verse_text = verse_text.replace("<pb/>", "").strip()
        
        # Importar re para expresiones regulares
        import re
        
        # 1. Notas al pie - Convertirlas en superíndices o símbolos especiales
        # Ejemplo: <f>[6]</f> -> [6]
        clean_text = re.sub(r'<f>\s*\[(\d+)\]\s*</f>', r'[\1]', verse_text)
        
        # 2. Etiquetas de formato de texto poético <t> - Mantener el texto pero añadir sangría
        # Primero eliminar etiquetas <t></t> vacías
        clean_text = re.sub(r'<t>\s*</t>', ' ', clean_text)
        
        # Luego procesar las etiquetas <t> con contenido
        # Simplemente eliminamos las etiquetas pero preservamos el contenido
        clean_text = re.sub(r'<t>(.*?)</t>', r'\1', clean_text)
        
        # 3. Procesar etiquetas especiales para formato
        # Primero, asegurarnos de que las etiquetas de formato estén bien formadas
        # Esto ayuda con etiquetas que pueden estar incompletas o mal formadas
        special_tags = ['J', 'b', 'i', 'u']
        
        # Crear un patrón para encontrar etiquetas que no son especiales
        non_special_pattern = r'<(?!/?(?:' + '|'.join(special_tags) + r'))[^>]*>'
        clean_text = re.sub(non_special_pattern, '', clean_text)
        
        # 4. Eliminar espacios múltiples y limpiar
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        return clean_text

    def display_formatted_text(self, y, x, text, max_width):
        """Muestra texto con formato aplicando atributos de curses según las etiquetas"""
        import re
        
        # Diccionario de etiquetas y sus atributos correspondientes
        tag_attrs = {
            'J': curses.color_pair(3),  # Palabras de Jesús en rojo
            'b': curses.A_BOLD,         # Texto en negrita
            'i': curses.A_ITALIC,       # Texto en cursiva (si está disponible)
            'u': curses.A_UNDERLINE     # Texto subrayado
        }
        
        # Posición actual en la pantalla
        current_x = x
        remaining_width = max_width
        
        # Enfoque simplificado: primero eliminar todas las etiquetas para mostrar solo el texto
        # Esto evita problemas con etiquetas mal formadas o anidadas
        plain_text = re.sub(r'<[^>]*>', '', text)
        
        # Luego, identificar secciones que deberían tener formato
        sections = []
        
        # Buscar etiquetas de apertura y cierre
        for tag, attr in tag_attrs.items():
            pattern = f'<{tag}>(.*?)</{tag}>'
            
            # Encontrar todas las ocurrencias de esta etiqueta
            for match in re.finditer(pattern, text, re.DOTALL):
                content = match.group(1)
                
                # Calcular posiciones en el texto plano
                # Esto es aproximado y puede no ser perfecto para textos complejos
                start_text = text[:match.start()]
                start_plain = re.sub(r'<[^>]*>', '', start_text)
                start_pos = len(start_plain)
                
                content_plain = re.sub(r'<[^>]*>', '', content)
                end_pos = start_pos + len(content_plain)
                
                sections.append((start_pos, end_pos, attr))
        
        # Ordenar secciones por posición de inicio
        sections.sort(key=lambda x: x[0])
        
        # Mostrar el texto plano con formato en las secciones correspondientes
        pos = 0
        for i, char in enumerate(plain_text):
            if i >= remaining_width:
                break
                
            # Determinar si este carácter debe tener formato especial
            attr = None
            for start, end, section_attr in sections:
                if start <= i < end:
                    attr = section_attr
                    break
            
            # Mostrar el carácter con o sin atributos
            if attr is not None:
                self.stdscr.attron(attr)
                self.stdscr.addch(y, current_x, char)
                self.stdscr.attroff(attr)
            else:
                self.stdscr.addch(y, current_x, char)
            
            current_x += 1

    def format_verse_for_display(self, verse_text, width):
        """Formatea un versículo para mostrar, respetando etiquetas especiales"""
        # Procesar el texto básico primero
        processed_text = self.process_verse_text(verse_text)
        
        # Detectar si el versículo tiene formato poético (tenía etiquetas <t>)
        is_poetic = '<t>' in verse_text
        
        # Dividir en palabras para formatear
        words = processed_text.split()
        lines = []
        current_line = ""
        
        # No añadimos sangría adicional para mantener todo alineado
        
        for word in words:
            # Si añadir esta palabra excede el ancho, comenzar nueva línea
            if len(current_line) + len(word) + 1 > width:
                if current_line:  # Solo añadir si la línea no está vacía
                    lines.append(current_line)
                # Comenzar nueva línea sin sangría
                current_line = word
            else:
                # Añadir palabra a la línea actual
                if not current_line:
                    current_line = word
                else:
                    current_line += " " + word
        
        # Añadir la última línea si hay contenido
        if current_line:
            lines.append(current_line)
            
        return lines

    def process_formatting_tags(self, text):
        """Procesa las etiquetas de formato en el texto bíblico"""
        # Eliminar etiquetas <pb/> si existen
        text = text.replace("<pb/>", "")
        
        # Crear un diccionario para mapear etiquetas a atributos curses
        tag_attrs = {
            'J': curses.color_pair(3),  # Palabras de Jesús en rojo
            'b': curses.A_BOLD,         # Texto en negrita
            'i': curses.A_ITALIC,       # Texto en cursiva (si está disponible)
            'u': curses.A_UNDERLINE     # Texto subrayado
        }
        
        # Buscar todas las etiquetas en el texto
        import re
        
        # Primero, eliminar todas las etiquetas y guardar el texto plano
        plain_text = re.sub(r'<[^>]+>', '', text)
        
        # Luego, encontrar todas las secciones con etiquetas y sus posiciones
        formatted_sections = []
        
        # Buscar etiquetas de apertura y cierre
        pattern = r'<([^>]+)>(.*?)</\1>'
        for match in re.finditer(pattern, text, re.DOTALL):
            tag = match.group(1)
            content = match.group(2)
            
            # Encontrar la posición en el texto plano
            # Esto es complicado porque necesitamos mapear posiciones entre texto con etiquetas y sin ellas
            start_pos = len(re.sub(r'<[^>]+>', '', text[:match.start()]))
            end_pos = start_pos + len(re.sub(r'<[^>]+>', '', content))
            
            if tag in tag_attrs:
                formatted_sections.append((start_pos, end_pos, tag_attrs[tag]))
        
        return plain_text, formatted_sections


def run_interactive_mode(version=None):
    """Run the interactive mode"""
    return wrapper(lambda stdscr: InteractiveRBible(stdscr, version).setup() and InteractiveRBible(stdscr, version).main_menu())