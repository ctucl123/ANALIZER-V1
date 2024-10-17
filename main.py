from PySide6.QtWidgets import QApplication, QFileDialog
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile,QIODevice,QDate
import sys
import requests
import json
url = 'https://recursos.kbus.kradac.com/bus/transaccion/buscar?_dc=1727813359038'


headers = {
    'Content-Type': 'application/json',  
    'Authorization': 'Bearer token_de_autorizacion'
}






class MyApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        ui_file_name = "mainwindow.ui"
        ui_file = QFile(ui_file_name)
        self.download_loops = 3
        if not ui_file.open(QIODevice.ReadOnly):
            sys.exit(-1)
        loader = QUiLoader()
        self.window = loader.load(ui_file)
        ui_file.close()
        self.transactions = []
        self.stop_download = False
        self.window.date_download.setDate(QDate.currentDate())
        self.window.download_btn.clicked.connect(self.download_data)
        self.window.stop_btn.clicked.connect(lambda: self.detenerDescarga())
    def detenerDescarga(self):
        pass
        #self.stop_download = True

    def download_data(self):
        self.transactions = []
        self.window.progress_download.setValue(0)
        selected_date = self.window.date_download.date()
        date_str = selected_date.toString("yyyy-MM-dd")
        
        for i in range(self.download_loops):
            payload = {
                'idTipoTarjeta':'',
                'cardNo': '',
                'start_date': date_str,
                'operNo': '',
                'end_date': date_str,
                'termNo': '',
                'is_historic': '',
                'transType': '',
                'blackType':'' ,
                'db_recaudo': 'kbusrecaudodb',
                'name_table': 'transline',
                'idAdministrador': 6565,
                'idApp': 1,
                'page': i,
                'start': 0,
                'limit': 700
            }
            response = requests.post(url, json=payload, headers=headers)
            if self.stop_download:
                self.stop_download = False
                self.window.progress_download.setValue(0)
                break
            if response.status_code == 200:
                response_data = response.json() 
                data = response_data.get('data', [])
                if data:
                    print(f"Descargando base de datos -->{i}")
                    for item in data:
                        aux_dict = {"transaction": item['tr'],"tarifa": item['tf'],"equipo":item['nE'],"mt":item['mt'] ,
                                    "fH":item['fH'],"lat":item["lat"],"lng":item["lng"],"lg":item["lg"],"tarjeta":item["nmT"]}
                        self.transactions.append(aux_dict)
                    valor_escalado = (i / self.download_loops) * 100
                    self.window.progress_download.setValue(valor_escalado)
                else:
                    print("No se encontraron datos.")
                    self.window.progress_download.setValue(100)
                    break
            else:
                print(f'Error {response.status_code}:', response.text)
                self.window.progress_download.setValue(0)
                break
        print(date_str)
        if len(self.transactions) > 0:
            self.window.progress_download.setValue(100)
            fecha  = date_str
            dialog = QFileDialog().getSaveFileName(
            caption='Guardar archivo como',
            dir='{}'.format(fecha),
            selectedFilter="JSON Files (*.json)"
                )
            file_path = dialog[0] + ".json"
            print(file_path)
            nombre_archivo = f'{file_path}.json'
            with open(nombre_archivo, 'w', encoding='utf-8') as archivo:
                json.dump(self.transactions, archivo, ensure_ascii=False, indent=4)


    def procesar(self):
        self.transactions
    def run(self):
        self.window.show()
        sys.exit(self.app.exec())

if __name__ == "__main__":
    app_instance = MyApp()
    app_instance.run()