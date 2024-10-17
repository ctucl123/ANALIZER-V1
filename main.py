from PySide6.QtWidgets import QApplication, QFileDialog
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile,QIODevice,QDate
from Loader import FileLoader
import pandas as pd
import sys
import requests
import json
url = 'https://recursos.kbus.kradac.com/bus/transaccion/buscar?_dc=1727813359038'


headers = {
    'Content-Type': 'application/json',  
    'Authorization': 'Bearer token_de_autorizacion'
}




#desarrollado por MECDEVS - 2024 www.mecdevs.com

class MyApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        ui_file_name = "mainwindow.ui"
        ui_file = QFile(ui_file_name)
        self.download_loops = 500
        if not ui_file.open(QIODevice.ReadOnly):
            sys.exit(-1)
        loader = QUiLoader()
        self.window = loader.load(ui_file)
        ui_file.close()
        self.transactions = []
        self.df_inicial = pd.DataFrame()
        self.unidades = pd.read_json('unidades.json')
        self.stop_download = False
        self.window.date_download.setDate(QDate.currentDate())
        self.window.download_btn.clicked.connect(self.download_data)
        self.window.stop_btn.clicked.connect(lambda: self.detenerDescarga())
        self.window.upload_btn.clicked.connect(lambda: self.cargar())
        self.window.procesar_btn.clicked.connect(lambda: self.procesar())
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
                    print("No se encontraron mas datos.")
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
            self.df_inicial = pd.DataFrame(self.transactions)
            self.window.data_done.setStyleSheet("color: #2ecc71;")
            self.window.data_done.setText("Datos Listos Para Procesar :)")
    def cargar(self):
        self.window.progress_upload.setValue(0)
        self.window.progress_upload.setValue(10)
        loader = FileLoader()
        json_file = loader.open_file_dialog()
        self.window.progress_upload.setValue(30)
        self.window.file_path.setText(json_file)
        if json_file:
            self.window.progress_upload.setValue(40)
            self.df_inicial = pd.read_json(json_file)
            self.window.data_done.setStyleSheet("color: #2ecc71;")
            self.window.data_done.setText("Datos Listos Para Procesar :)")
            self.window.progress_upload.setValue(100)
        
    def procesar(self):
            self.window.process_bar.setValue(12)
            df = self.df_inicial.drop_duplicates(subset=['fH', 'equipo'], keep='first')
            #aqui vamos a realizar un segundo filtro
            df['fH'] = pd.to_datetime(df['fH'])
            df['date'] = df['fH'].dt.date
            fecha_selected = df['date'].value_counts().index[0]
            if df['date'].unique().size != 1:
                df = df[df['date'] == fecha_selected]
            self.window.process_bar.setValue(25)
            df_debitos = df[df['transaction'].isin(['Debito'])]
            self.window.process_bar.setValue(40)
            df_recargas = df[df['transaction'].isin(['Recarga'])]
            self.window.process_bar.setValue(55)
            df_otras = df[~df['transaction'].isin(['Recarga','Debito'])]
            grupo_2 = self.unidades[self.unidades['group'] == 2]
            debitos_grupo2 = df_debitos[df_debitos['equipo'].isin(grupo_2['device'])]
            total_g2 = round(debitos_grupo2['mt'].sum(), 2)
            self.window.process_bar.setValue(70)
            total_debitado = round(df_debitos['mt'].sum(), 2)
            total_g1 = round(total_debitado - total_g2,2)
            self.window.process_bar.setValue(80)
            total_recargas = round(df_recargas['mt'].sum(),2)
            self.window.process_bar.setValue(85)
            cantidad_debitos = df_debitos.shape[0]
            self.window.process_bar.setValue(90)
            cantidad_recargas = df_recargas.shape[0]
            cantidad_otras = df_otras.shape[0]
            total = cantidad_debitos + cantidad_recargas + cantidad_otras
            self.window.process_bar.setValue(100)
            result_string = (
                            f'TRANSACCIONES ANALIZADAS ---> {total}\n'
                            f'Fecha analizada: {fecha_selected}\n'
                            f'cantidad de otras transacciones: {cantidad_otras}\n'
                            f'cantidad de recargas: {cantidad_debitos}\n'
                            f'cantidad de debitos: {cantidad_recargas}\n'
                            f'ingresos de debitos: {total_debitado}\n'
                            f'ingresos de recargas: {total_recargas}\n'
                            f'INGRESOS POR GRUPO\n'
                            f'G1: {total_g1}\n'
                            f'G2: {total_g2}\n'
                            )
            self.window.result.setPlainText(result_string)
            print(result_string)
    def run(self):
        self.window.show()
        sys.exit(self.app.exec())

if __name__ == "__main__":
    app_instance = MyApp()
    app_instance.run()