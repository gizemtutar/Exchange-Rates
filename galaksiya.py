import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QSizePolicy
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
import pandas as pd
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt

class ExchangeRateApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Exchange Rate Comparison')
        self.resize(800, 600)  # Pencerenin boyutunu 800x600 piksel olarak ayarla

        # Arka plan rengini ayarla
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(192, 192, 192))  # Gri rengi ayarla
        self.setPalette(p)

        # Düğmeleri oluştur
        self.btn_fetch = QPushButton('Güncel Döviz Kurlarını Getir', self)
        self.btn_fetch.clicked.connect(self.fetch_exchange_rates)
        self.btn_show_table = QPushButton('Döviz Kurlarını Tabloda Göster', self)
        self.btn_show_table.clicked.connect(self.show_exchange_rates_table)
        self.btn_show_graph = QPushButton('Döviz Kurlarını Grafiğe Göster', self)
        self.btn_show_graph.clicked.connect(self.show_exchange_rates_graph)
        self.btn_save = QPushButton('Excele Kaydet', self)
        self.btn_save.clicked.connect(self.save_to_excel)

        # Düğmelerin stilini ayarla
        self.btn_fetch.setStyleSheet("background-color: #f44336; color: black;")
        self.btn_show_table.setStyleSheet("background-color: #f44336; color: black;")
        self.btn_show_graph.setStyleSheet("background-color: #f44336; color: black;")
        self.btn_save.setStyleSheet("background-color: #f44336; color: black;")
        
        # Diğer bileşenleri ekle (label, table, vb.)
        self.label_status = QLabel('', self)
        self.table = QTableWidget()
        self.table.setColumnCount(5)

        # Gizem Tutar tarafından kodlandı etiketi
        self.label_gizem = QLabel('<a href="https://github.com/gizemtutar">Gizem Tutar tarafından kodlandı</a>', self)
        self.label_gizem.setStyleSheet("color: red; font-style: italic; font-size: 12px;")
        self.label_gizem.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.label_gizem.setOpenExternalLinks(True)  # Harici bağlantıları açma özelliğini etkinleştir

        # Layout'u oluştur
        layout = QVBoxLayout()
        layout.addWidget(self.btn_fetch)
        layout.addWidget(self.btn_show_table)
        layout.addWidget(self.btn_show_graph)
        layout.addWidget(self.btn_save)
        layout.addWidget(self.table)
        layout.addWidget(self.label_status)
        layout.addWidget(self.label_gizem)  # Gizem Tutar tarafından kodlandı etiketini layout'a ekle
        
        # Table'ın boyutunu ayarla ve layout'a ekle
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.setStretchFactor(self.table, 1)  # Table'ın tüm boş alanı kaplamasını sağla
        
        self.setLayout(layout)

    def fetch_exchange_rates(self):
        # TCMB'den veri çekme
        tcmb_url = "https://www.tcmb.gov.tr/kurlar/today.xml"
        response = requests.get(tcmb_url)
        tcmb_soup = BeautifulSoup(response.content, "xml")  # XML olarak veri çek

        tcmb_currency_names = tcmb_soup.find_all("CurrencyName")
        tcmb_forex_buying_rates = tcmb_soup.find_all("ForexBuying")
        tcmb_forex_selling_rates = tcmb_soup.find_all("ForexSelling")
        tcmb_effective_buying_rates = tcmb_soup.find_all("BanknoteBuying")
        tcmb_effective_selling_rates = tcmb_soup.find_all("BanknoteSelling")

        tcmb_data = []
        for currency, buying_rate, selling_rate, effective_buying_rate, effective_selling_rate in zip(tcmb_currency_names, tcmb_forex_buying_rates, tcmb_forex_selling_rates, tcmb_effective_buying_rates, tcmb_effective_selling_rates):
            tcmb_data.append({
                "Döviz Türü": currency.text,
                "TCMB Döviz Alış": buying_rate.text,
                "TCMB Döviz Satış": selling_rate.text,
                "TCMB Efektif Alış": effective_buying_rate.text,
                "TCMB Efektif Satış": effective_selling_rate.text
            })

        # Ziraat Bankası'ndan veri çekme
        ziraat_url = "https://www.ziraatbank.com.tr/tr/fiyatlar-ve-oranlar"
        response = requests.get(ziraat_url)
        ziraat_soup = BeautifulSoup(response.content, "html.parser")

        ziraat_data = []
        ziraat_table = ziraat_soup.find("div", attrs={"data-id": "rdIntBranchDoviz"})
        if ziraat_table:
            rows = ziraat_table.find_all("tr")
            for row in rows[1:]:
                cells = row.find_all("td")
                doviz_turu = cells[0].text.strip()
                doviz_alis = cells[2].text.strip() if cells[2].text.strip() else '0'
                doviz_satis = cells[3].text.strip() if cells[3].text.strip() else '0'
                efektif_alis = cells[4].text.strip() if cells[4].text.strip() else '0'
                efektif_satis = cells[5].text.strip() if cells[5].text.strip() else '0'
                ziraat_data.append({
                    "Döviz Türü": doviz_turu,
                    "Ziraat Bankası Döviz Alış": doviz_alis,
                    "Ziraat Bankası Döviz Satış": doviz_satis,
                    "Ziraat Bankası Efektif Alış": efektif_alis,
                    "Ziraat Bankası Efektif Satış": efektif_satis
                })
        else:
            # Ziraat Bankası verisi yoksa, boş bir satır ekleyelim
            ziraat_data.append({
                "Döviz Türü": "",
                "Ziraat Bankası Döviz Alış": "0",
                "Ziraat Bankası Döviz Satış": "0",
                "Ziraat Bankası Efektif Alış": "0",
                "Ziraat Bankası Efektif Satış": "0"
            })

        # TCMB ve Ziraat Bankası verilerini birleştirme
        tcmb_df = pd.DataFrame(tcmb_data)
        ziraat_df = pd.DataFrame(ziraat_data)

        # TCMB ve Ziraat Bankası verilerini tek bir veri çerçevesinde birleştirme
        merged_df = pd.merge(tcmb_df, ziraat_df, on="Döviz Türü", how="outer")

        # NaN değerlerini düzeltme
        merged_df.fillna({'TCMB Döviz Alış': 0, 'TCMB Döviz Satış': 0,
                          'TCMB Efektif Alış': 0, 'TCMB Efektif Satış': 0,
                          'Ziraat Bankası Döviz Alış': 0, 'Ziraat Bankası Döviz Satış': 0,
                          'Ziraat Bankası Efektif Alış': 0, 'Ziraat Bankası Efektif Satış': 0}, inplace=True)

        # Excel dosyasına yazdırma
        excel_file = "doviz_verileri.xlsx"
        merged_df.to_excel(excel_file, index=False)

        self.label_status.setText('Exchange rates fetched and saved to "doviz_verileri.xlsx"')

    def save_to_excel(self):
        self.fetch_exchange_rates()  # Verileri önce çekelim
        self.label_status.setText('"doviz_verileri.xlsx" adlı dosyaya başarılı bir şekilde kaydedilmiştir')

    def show_exchange_rates_table(self):
        try:
            merged_df = pd.read_excel("doviz_verileri.xlsx")  # Önceki verileri oku
            if merged_df.empty:
                self.label_status.setText('There are no exchange rates to show.')
                return

            # Verileri tabloya ekleme
            self.table.setRowCount(len(merged_df))
            self.table.setColumnCount(len(merged_df.columns))
            self.table.setHorizontalHeaderLabels(merged_df.columns)  # Sütun başlıklarını ayarla
            for i, row in merged_df.iterrows():
                for j, value in enumerate(row):
                    item = QTableWidgetItem(str(value))
                    self.table.setItem(i, j, item)

            self.label_status.setText('Döviz kurları tabloda gösterilmektedir.')

        except FileNotFoundError:
            self.label_status.setText('Döviz kurları bulunamadı. Lütfen önce Güncel Döviz Kurlarını Getir butonuna basın.')

    def show_exchange_rates_graph(self):
        try:
            merged_df = pd.read_excel("doviz_verileri.xlsx")  # Önceki verileri oku
            if merged_df.empty:
                self.label_status.setText('There are no exchange rates to show.')
                return

            # Verileri grafik olarak gösterme
            plt.figure(figsize=(10, 6))
            merged_df.plot(x="Döviz Türü", y=["TCMB Döviz Alış", "TCMB Döviz Satış", "Ziraat Bankası Döviz Alış", "Ziraat Bankası Döviz Satış"], kind="bar")
            plt.title('Döviz Kurları')
            plt.xlabel('Döviz Türü')
            plt.ylabel('Kur Değeri')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.show()

            self.label_status.setText('Döviz kurları grafikte gösterilmektedir.')

        except FileNotFoundError:
            self.label_status.setText('Döviz kurları bulunamadı. Lütfen önce Güncel Döviz Kurlarını Getir butonuna basın.')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ExchangeRateApp()
    ex.show()
    sys.exit(app.exec_())
