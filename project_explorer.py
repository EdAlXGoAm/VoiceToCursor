import os
import re
from typing import List, Dict, Tuple

class ProjectExplorer:
    """
    Clase para explorar un proyecto y extraer información relevante como
    nombres de archivos y funciones para mejorar la transcripción de audio.
    """
    
    def __init__(self, project_path: str):
        """
        Inicializa el explorador de proyectos.
        
        Args:
            project_path: Ruta absoluta al directorio del proyecto.
        """
        self.project_path = project_path
        # Extensiones de archivos de código que contienen funciones
        self.code_extensions = ['.py', '.js', '.ts', '.java', '.c', '.cpp', '.cs', '.php', '.rb']
        # Patrones para extraer nombres de funciones según el lenguaje
        self.function_patterns = {
            '.py': r'def\s+([a-zA-Z0-9_]+)\s*\(',  # Python
            '.js': r'(?:function\s+([a-zA-Z0-9_]+)\s*\()|(?:const\s+([a-zA-Z0-9_]+)\s*=\s*(?:async\s*)?\(?.*\)?\s*=>)',  # JavaScript
            '.ts': r'(?:function\s+([a-zA-Z0-9_]+)\s*\()|(?:const\s+([a-zA-Z0-9_]+)\s*=\s*(?:async\s*)?\(?.*\)?\s*=>)',  # TypeScript
            '.java': r'(?:public|private|protected)?\s+(?:static\s+)?(?:[a-zA-Z0-9_<>]+)\s+([a-zA-Z0-9_]+)\s*\(',  # Java
            '.c': r'[a-zA-Z0-9_]+\s+([a-zA-Z0-9_]+)\s*\(',  # C
            '.cpp': r'[a-zA-Z0-9_:]+\s+([a-zA-Z0-9_]+)\s*\(',  # C++
            '.cs': r'(?:public|private|protected|internal)?\s+(?:static\s+)?(?:[a-zA-Z0-9_<>]+)\s+([a-zA-Z0-9_]+)\s*\(',  # C#
            '.php': r'function\s+([a-zA-Z0-9_]+)\s*\(',  # PHP
            '.rb': r'def\s+([a-zA-Z0-9_?!]+)',  # Ruby
        }
        # Carpetas a omitir durante la exploración
        self.ignored_folders = ['__pycache__', '.git', '.vscode', 'node_modules', 'venv', 'env', '.env']
    
    def _get_file_tree(self, start_path: str, prefix: str = "", is_root: bool = True) -> List[str]:
        """
        Genera una representación en árbol de los archivos y carpetas.
        
        Args:
            start_path: Ruta inicial para el árbol.
            prefix: Prefijo para la indentación.
            is_root: Si es la carpeta raíz.
            
        Returns:
            Lista de cadenas que representan el árbol de archivos.
        """
        if is_root:
            tree_lines = [os.path.basename(start_path) + "/"]
            prefix = "  "
        else:
            tree_lines = []
        
        # Obtener elementos del directorio y ordenarlos
        items = os.listdir(start_path)
        folders = []
        files = []
        
        # Filtrar carpetas y archivos, omitiendo las carpetas ignoradas
        for item in items:
            item_path = os.path.join(start_path, item)
            if os.path.isdir(item_path):
                # Solo incluir la carpeta si no está en la lista de ignorados
                if item not in self.ignored_folders:
                    folders.append(item)
            else:
                files.append(item)
        
        folders.sort()
        files.sort()
        
        # Primero las carpetas
        for i, folder in enumerate(folders):
            is_last = (i == len(folders) - 1 and len(files) == 0)
            tree_lines.append(f"{prefix}{'└─ ' if is_last else '├─ '}{folder}/")
            
            # Añadir contenido de las subcarpetas
            subpath = os.path.join(start_path, folder)
            subtree = self._get_file_tree(
                subpath, 
                prefix + ("    " if is_last else "│   "), 
                is_root=False
            )
            tree_lines.extend(subtree)
        
        # Luego los archivos
        for i, file in enumerate(files):
            is_last = (i == len(files) - 1)
            tree_lines.append(f"{prefix}{'└─ ' if is_last else '├─ '}{file}")
        
        return tree_lines
    
    def _extract_functions_from_file(self, file_path: str) -> List[str]:
        """
        Extrae nombres de funciones de un archivo.
        
        Args:
            file_path: Ruta al archivo.
            
        Returns:
            Lista de nombres de funciones encontradas.
        """
        _, ext = os.path.splitext(file_path)
        
        # Si no es un archivo de código soportado, retornar lista vacía
        if ext not in self.function_patterns:
            return []
        
        functions = []
        pattern = self.function_patterns.get(ext)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
            # Buscar todos los nombres de funciones según el patrón del lenguaje
            matches = re.finditer(pattern, content)
            for match in matches:
                # Algunos patrones tienen grupos múltiples, tomar el primero no vacío
                function_name = next((g for g in match.groups() if g), match.group(1))
                if function_name and function_name not in functions:
                    functions.append(function_name)
        except Exception as e:
            print(f"Error al leer el archivo {file_path}: {str(e)}")
        
        return functions
    
    def scan_project(self) -> Tuple[List[str], List[str]]:
        """
        Escanea el proyecto para obtener la estructura de archivos y nombres de funciones.
        
        Returns:
            Tupla con (lista de líneas de árbol, lista de nombres de funciones).
        """
        # Verificar que la ruta existe
        if not os.path.exists(self.project_path):
            return [], []
        
        # Generar árbol de archivos
        file_tree = self._get_file_tree(self.project_path)
        
        # Extraer nombres de funciones
        all_functions = []
        
        # Recorrer todos los archivos recursivamente
        for root, dirs, files in os.walk(self.project_path):
            # Modificar dirs en su lugar para evitar recorrer carpetas ignoradas
            # Esto afecta a os.walk para que no entre en esas carpetas
            dirs[:] = [d for d in dirs if d not in self.ignored_folders]
            
            for file in files:
                file_path = os.path.join(root, file)
                _, ext = os.path.splitext(file)
                
                # Si es un archivo de código, extraer funciones
                if ext in self.code_extensions:
                    functions = self._extract_functions_from_file(file_path)
                    all_functions.extend(functions)
        
        # Eliminar duplicados y ordenar
        all_functions = sorted(list(set(all_functions)))
        
        return file_tree, all_functions
    
    def generate_transcription_prompt(self) -> str:
        """
        Genera un prompt para mejorar la transcripción basado en los nombres
        de archivos y funciones encontradas en el proyecto.
        
        Returns:
            Prompt para mejorar la transcripción.
        """
        file_tree, functions = self.scan_project()
        
        prompt_parts = []
        prompt_parts.append("El usuario puede mencionar los siguientes nombres de archivos en el audio:")
        
        # Añadir estructura de archivos
        if file_tree:
            prompt_parts.append("\n".join(file_tree))
        else:
            prompt_parts.append("No se encontraron archivos en el proyecto.")
        
        prompt_parts.append("\n")
        prompt_parts.append("El usuario puede mencionar también nombres de funciones en el audio:")
        
        # Añadir nombres de funciones
        if functions:
            prompt_parts.append(", ".join(functions))
        else:
            prompt_parts.append("No se encontraron funciones en el proyecto.")
        
        # Construir prompt final
        return "\n".join(prompt_parts)

# Función para obtener el prompt directamente
def get_project_transcription_prompt(project_path: str) -> str:
    """
    Obtiene un prompt para mejorar la transcripción basado en 
    los archivos y funciones de un proyecto.
    
    Args:
        project_path: Ruta al directorio del proyecto.
        
    Returns:
        Prompt para mejorar la transcripción.
    """
    explorer = ProjectExplorer(project_path)
    return explorer.generate_transcription_prompt()

# Ejemplo de uso
if __name__ == "__main__":
    # Para pruebas
    project_path = r"D:\CursorDeployments\Voice to cursor"
    prompt = get_project_transcription_prompt(project_path)
    print(prompt) 