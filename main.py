from PySide6.QtWidgets import QApplication, QPushButton
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile

def main():
    # Inicializa la aplicación
    app = QApplication([])

    # Cargar el archivo .ui
    loader = QUiLoader()
    ui_file = QFile("MainWindow.ui")
    ui_file.open(QFile.ReadOnly)
    window = loader.load(ui_file)
    ui_file.close()

    # Acceder a los componentes, por ejemplo un botón
    # boton = window.findChild(QPushButton, "nombreDelBoton")
    # boton.clicked.connect(lambda: print("Botón presionado"))

    # Mostrar la ventana
    window.show()

    # Iniciar el loop de la aplicación
    app.exec()

if __name__ == "__main__":
    main()
