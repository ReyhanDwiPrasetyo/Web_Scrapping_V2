import pandas as pd
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import requests
from bs4 import BeautifulSoup
from datetime import datetime, time,timedelta
import locale
from io import BytesIO
from email.mime.application import MIMEApplication
import calendar

URL_OJK = "https://www.ojk.go.id/id/Regulasi/Default.aspx"
URL_BI = "https://www.bi.go.id/id/publikasi/peraturan/Default.aspx"
URL_LPS = "https://lps.go.id/plps/"
URL_SELPS = "https://lps.go.id/surat-edaran/"
URL_ROJK = 'https://www.ojk.go.id/id/regulasi/otoritas-jasa-keuangan/rancangan-regulasi/default.aspx'
DATABASE_PATH = 'REGULATION_DATABASE.csv'
RANCANGAN_PATH = 'RANCANGAN_DATABASE.csv'

# Email Configuration
SENDER_EMAIL = "prasetyoreyhan0509@gmail.com"
RECIPIENTS = ["prasetyoreyhan0509@gmail.com"]
APP_PASSWORD = "xxxxxxxxxx"
def SCRAP_ROJK(url):
    try:
        timestamp = datetime.now()
        regulator = 'OJK'
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Error: Failed to retrieve the OJK page. Status code: {response.status_code}")
            return pd.DataFrame()
        soup = BeautifulSoup(response.content,'html.parser')
        table = soup.find('table',{'class':"table table-bordered table-styled"})
        rows = table.find_all('tr')
        data = []
        for row in rows[1:]:
            td_tag = row.find_all('td')
            judul_rancangan = td_tag[0].text.strip()
            deskripsi = td_tag[1].text.strip().replace('\u200b','')
            link = 'https://www.ojk.go.id' +row.find('a')['href']
            response2 = requests.get(link)
            if response2.status_code != 200:
                print('Failed to Rancangan Page')
            soup2 = BeautifulSoup(response2.content,'html.parser')
            tanggal_rancangan = soup2.find('span',{'class':'display-date-text'}).text.strip()
            if not tanggal_rancangan:
                print('Warning : Unable to Find info for waktu berlaku. Skipping')
                continue
            data.append({'REGULATOR':regulator,'JUDUL':judul_rancangan,'TANGGAL_TERBIT':tanggal_rancangan,'LINK_RANCANGAN':link,'TIMESTAMP':timestamp,'DESKRIPSI':deskripsi})
        df = pd.DataFrame(data)
        return df 
    except Exception as e:
        print(f"Error in SCRAP_ROJK: {e}")
        return None

def SCRAP_OJK(url):
    try:
        timestamp = datetime.now()
        regulator = 'OJK'
        response = requests.get(url)
        if response.status_code != 200:
                print(f"Error: Failed to retrieve the OJK page. Status code: {response.status_code}")
                return pd.DataFrame()
        soup = BeautifulSoup(response.content, "html.parser")
        table = soup.find("table", {"class": "table table-bordered table-styled"})
        rows = table.find_all("tr")
        data = []
        for row in rows[1:]:
            judul = row.find('td').text.strip()
            if 'seojk' in judul.lower():
                judul = "Surat Edaran Otoritas Jasa Keuangan Nomor "+judul
            else:
                judul = "Peraturan Otoritas Jasa Keuangan Nomor "+judul
            strong_tag = row.find('strong')
            tentang = strong_tag.find('a').text.strip()
            link = 'https://www.ojk.go.id'+strong_tag.find('a')['href']
            judul = " ".join((judul + ' tentang '+tentang).strip().split())
            response2 = requests.get(link)
            if response2.status_code != 200:
                print('Failed to Retrieve Data')
            soup2 = BeautifulSoup(response2.content,'html.parser')
            waktu_berlaku = soup2.find('span',{'class':'display-date-text tanggal-2'}).text.strip()
            if not waktu_berlaku:
                print('Warning: Unable to find info for waktu berlaku..Skipping')
                continue
            
            data.append({
                'REGULATOR': regulator,'JUDUL':judul,'TANGGAL_REGULASI_EFEKTIF':waktu_berlaku,'LINK_REGULASI':link,'TIMESTAMP':timestamp
            })
        df = pd.DataFrame(data)
        return df
    except Exception as e:
        print(f"Error in SCRAP_OJK: {e}")
        return None

def SCRAP_BI(url):
    try:
        timestamp = datetime.now()
        regulator = 'BI'
        response = requests.get(url)
        if response.status_code != 200:
                print(f"Error: Failed to retrieve the BI page. Status code: {response.status_code}")
                return pd.DataFrame()
        soup = BeautifulSoup(response.content, "html.parser")
        tag_list = soup.find_all('div',class_='media media--pers')
        data = []
        for tag in tag_list:
            judul = " ".join(tag.find('a',class_='mt-0 media__title ellipsis--two-line').get_text(strip=True).replace('\u200b','').replace('\r','').replace('\n','').split())
            link_judul = tag.a['href']
            waktu_berlaku = tag.find('div',class_='media__subtitle').get_text(strip=True)
            data.append({
            'REGULATOR':regulator,'JUDUL':judul,'TANGGAL_REGULASI_EFEKTIF':waktu_berlaku,'LINK_REGULASI':link_judul,'TIMESTAMP':timestamp
            })
        df = pd.DataFrame(data)
        return df
    except Exception as e:
        print(f"Error in SCRAP_BI: {e}")
        return None
    
def SCRAP_LPS(url):
    try:
        timestamp = datetime.now()
        regulator = 'LPS'
        response = requests.get(url)
        if response.status_code != 200:
                print(f"Error: Failed to retrieve the LPS page. Status code: {response.status_code}")
                return pd.DataFrame()
        soup = BeautifulSoup(response.content, "html.parser")
        tag_list = soup.findAll('div',class_='content')
        data = []
        for tag in tag_list :
            judul = " ".join(tag.find('span',class_='screen-reader-text').get_text(strip=True).split())
            link_judul = tag.a['href']
            waktu_berlaku = " ".join(tag.find('span',class_='meta-date').get_text(strip=True).split())
            data.append({
                'REGULATOR':regulator,'JUDUL':judul,'TANGGAL_REGULASI_EFEKTIF':waktu_berlaku,'LINK_REGULASI':link_judul,'TIMESTAMP':timestamp,
            })
        df = pd.DataFrame(data)
        return df
    except Exception as e:
        print(f"Error in SCRAP_LPS: {e}")
        return None

def SCRAP_SELPS(url):
    try:
        timestamp = datetime.now()
        regulator = 'LPS'
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        tag_list = soup.findAll('div',class_='content')
        data = []
        for tag in tag_list:
            judul = " ".join(tag.find('span',class_='screen-reader-text').get_text(strip=True).split())
            link_judul = tag.a['href']
            waktu_berlaku = tag.find('span',class_='meta-date').get_text(strip=True)
            data.append({
                'REGULATOR':regulator,'JUDUL':judul,'TANGGAL_REGULASI_EFEKTIF':waktu_berlaku,'LINK_REGULASI':link_judul,'TIMESTAMP':timestamp
            })
        df = pd.DataFrame(data)
        return df
    except Exception as e:
        print(f"Error in SCRAP_SELPS: {e}")
        return None

def check_for_new_entries(df):
    database = pd.read_csv(DATABASE_PATH)
    new_entries = df[~df['JUDUL'].isin(database['JUDUL'])]
    
    if not new_entries.empty:
        return new_entries
    
def check_for_new_entries_rancangan(df):
    database = pd.read_csv(RANCANGAN_PATH)
    new_entries = df[~df['JUDUL'].isin(database['JUDUL'])]
    if not new_entries.empty:
        return new_entries

def load_to_database_rancangan(df):
    database = pd.read_csv(RANCANGAN_PATH)
    if df is not None:
        database = pd.concat([database, df],ignore_index=True)
        database.to_csv(RANCANGAN_PATH,index=False)
        return database
    else:
        print('Tidak ada entri baru')
    
def load_to_database(df):
    database = pd.read_csv(DATABASE_PATH)
    if df is not None:
        df['NOTIFICATION_STATUS'] = 'NOT SENT'
        start_id = int(database['ID_REGULASI'].max())+1
        df['ID_REGULASI'] = range(start_id,start_id+len(df))
        
        database = pd.concat([database,df],ignore_index=True)
        database.to_csv(DATABASE_PATH,index=False)
        return database
    else: 
        print('Tidak ada entri baru') #implement Logging

def split_tentang(judul):
    judul_lower = judul.lower()
    posisi_tentang = judul_lower.find('tentang')
    if posisi_tentang != -1:
        no_ketentuan = judul[:posisi_tentang].strip()
        tentang = judul[posisi_tentang+len('tentang'):].strip()
    else:
        no_ketentuan = judul 
        tentang = ''
    return no_ketentuan,tentang

def is_weekday():
    today = datetime.now().weekday()
    return today < 5

def is_friday():
    return datetime.now().weekday()==4

def is_last_weekday_of_month():
    today = datetime.now()
    last_day_of_month = calendar.monthrange(today.year,today.month)[1]
    last_date = datetime(today.year,today.month,last_day_of_month)
    
    while last_date.weekday() >4:
        last_date -= timedelta(days=1)
    
    return today.date() == last_date.date()

def push_new_regulation_notification(df,email):
    subject = '[Pemberitahuan] Terdapat Regulasi Baru dari Regulator'
    list_kebijakan = '\n'.join([f"\nNama Regulator: {row['REGULATOR']}\nNama Regulasi: {row['JUDUL']}\nLink Regulasi: {row['LINK_REGULASI']}\nWaktu Terbit: {row['TIMESTAMP']}"for index,row in df.iterrows()])
    body = f"""Dear Kak Trixie,
    
Saya berharap Anda dalam keadaan baik. Saya ingin melaporkan bahwa terdapat kebijakan baru pada situs regulator. Detail dari kebijakan baru tersebut adalah sebagai berikut :
    {list_kebijakan}
    
Saya harap informasi yang saya berikan dapat bermanfaat. Jika terdapat pertanyaan dan juga keluhan, mohon untuk menghubungi saya dengan alamat email ini. 

Terima kasih atas Perhatiannya
Hormat Saya,
Reyhan Dwi Prasetyo
    """
    sender = SENDER_EMAIL
    receiver = email 
    password = APP_PASSWORD
    
    message = MIMEMultipart()
    message['From'] = sender
    message['To'] = receiver
    message['Subject'] = subject
    message.attach(MIMEText(body,'plain'))
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com',465) as server:
            server.login(sender,password)
            server.sendmail(sender,receiver,message.as_string())
            #Implement Logging
            print('Email Notifikasi berhasil dikirim')
    except Exception as e:
        print(f'Gagal mengirim email: {e}') #IMPLEMENT LOGGING

def push_daily_notification(email):
    database = pd.read_csv(DATABASE_PATH)
    today = datetime.now().strftime('%Y-%m-%d')
    query = database[pd.to_datetime(database['TIMESTAMP']).dt.strftime('%Y-%m-%d')==today]
    subject = '[Pemberitahuan] Total Regulasi Baru Hari Ini'
    body = f"""Dear Kak Trixie,
    
Saya berharap Kak Trixie dalam keadaan sehat. Dengan ini, saya ingin melaporkan hasil monitoring terbaru terkait penambahan kebijakan baru di situs regulator hari ini. Berdasarkan pemantauan yang telah dilakukan, berikut adalah hasilnya:
    
Total Kebijakan Baru : {len(query)}
    
Dengan demikian, terdapat {len(query)} regulasi baru yang perlu ditinjau lebih lanjut pada periode pemantauan kali ini. Jika di kemudian hari terdapat kebijakan baru yang terdeteksi, Saya akan mengirim notifikasi untuk informasi lebih lanjut.

Terima kasih atas perhatian dan kerjasamanya

Hormat Saya,
Reyhan Dwi Prasetyo
Compliance Data Analyst Intern
    """
    sender = SENDER_EMAIL
    receiver = email
    password = APP_PASSWORD
    
    message = MIMEMultipart()
    message['From'] = sender
    message['To'] = receiver
    message['Subject'] = subject
    message.attach(MIMEText(body,'plain'))
    
    attachment = None
    if len(query) > 0:
        excel_buffer = BytesIO()
        excel = query[['REGULATOR','NO_KETENTUAN','TANGGAL_REGULASI_EFEKTIF','TENTANG']]
        excel.to_excel(excel_buffer,index=False,sheet_name='Laporan_Harian')
        excel_buffer.seek(0)
        attachment = MIMEApplication(excel_buffer.read(),_subtype='xlsx')
        attachment.add_header('Content-Disposition','attachment',filename='Laporan_Harian.xlsx')
        message.attach(attachment)
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com',465) as server:
            server.login(sender,password)
            server.sendmail(sender,receiver,message.as_string())
            #Implement Logging
            print('Email berhasil dikirim')
    except Exception as e:
        print('Gagal Mengirim Email')
    
    #Update Notification Status
    database.loc[query.index,'NOTIFICATION_STATUS'] = 'SENT'
    database.to_csv('REGULATION_DATABASE.csv',index=False)
    
def push_weekly_notification(email):
    database = pd.read_csv(DATABASE_PATH)
    database['TIMESTAMP'] = pd.to_datetime(database['TIMESTAMP'])
    today = pd.Timestamp.now()
    start_day = today - pd.DateOffset(days=6) 
    end_day = today
    weekly_data =database[(database['TIMESTAMP']>=start_day) & (database['TIMESTAMP']<=end_day) & (database['NOTIFICATION_STATUS'].isin(['NOT SENT','SENT']))]
    subject = '[Pemberitahuan] Pelaporan Regulasi Baru pada Minggu Ini'
    body = f"""Dear Kak Trixie,
    
Saya berharap Kak Trixie dalam keadaan sehat. Dengan ini, saya ingin melaporkan hasil monitoring selama seminggu ini terkait penambahan kebijakan baru di situs regulator. Berdasarkan pemantauan yang telah dilakukan, berikut adalah hasilnya:
    
Total Kebijakan Baru : {len(weekly_data)}
    
Dengan demikian, terdapat {len(weekly_data)} regulasi baru yang perlu ditinjau lebih lanjut pada periode pemantauan kali ini. Jika di kemudian hari terdapat kebijakan baru yang terdeteksi, Saya akan mengirim notifikasi untuk informasi lebih lanjut.

Terima kasih atas perhatian dan kerjasamanya

Hormat Saya,
Reyhan Dwi Prasetyo
Compliance Data Analyst Intern
    """
    sender = SENDER_EMAIL
    receiver = email
    password = APP_PASSWORD
    
    message = MIMEMultipart()
    message['From'] = sender
    message['To'] = receiver
    message['Subject'] = subject
    message.attach(MIMEText(body,'plain'))
    
    if len(weekly_data)>0:
        excel_buffer = BytesIO()
        excel_column = ['REGULATOR','NO_KETENTUAN','TANGGAL_REGULASI_EFEKTIF','TENTANG']
        weekly_data[excel_column].to_excel(excel_buffer,index=False,sheet_name='Laporan Mingguan')
        excel_buffer.seek(0)
        attachment = MIMEApplication(excel_buffer.read(),_subtype='xlsx')
        attachment.add_header('Content-Disposition','attachment',filename='Laporan_Mingguan.xlsx')
        message.attach(attachment)
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com',465) as server:
            server.login(sender,password)
            server.sendmail(sender,receiver,message.as_string())
            print('Email Notifikasi Berhasil dikirim') #Implement Logging
    except Exception as e:
        print('Error') # Implement Logging

def push_monthly_regulation(email):
    database = pd.read_csv(DATABASE_PATH)
    database['TIMESTAMP'] = pd.to_datetime(database['TIMESTAMP'])
    current_month = pd.Timestamp.now().month
    current_year = pd.Timestamp.now().year
    monthly_data = database[(database['TIMESTAMP'].dt.month==current_month) & (database['TIMESTAMP'].dt.year==current_year) &
                            (database['NOTIFICATION_STATUS'].isin(['NOT SENT','SENT']))]
    subject = '[Pemberitahuan] Pelaporan Regulasi Baru pada Bulan Ini'
    body = f"""Dear Kak Trixie,
    
Saya berharap Kak Trixie dalam keadaan sehat. Dengan ini, saya ingin melaporkan hasil monitoring selama sebulan ini terkait penambahan kebijakan baru di situs regulator. Berdasarkan pemantauan yang telah dilakukan, berikut adalah hasilnya:
    
Total Kebijakan Baru : {len(monthly_data)}
    
Dengan demikian, terdapat {len(monthly_data)} regulasi baru yang perlu ditinjau lebih lanjut pada periode pemantauan kali ini. Jika di kemudian hari terdapat kebijakan baru yang terdeteksi, Saya akan mengirim notifikasi untuk informasi lebih lanjut.

Terima kasih atas perhatian dan kerjasamanya

Hormat Saya,
Reyhan Dwi Prasetyo
Compliance Data Analyst Intern
    """
    sender_email = SENDER_EMAIL
    receiver = email 
    password = APP_PASSWORD
    
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver
    message['Subject'] = subject
    message.attach(MIMEText(body,'plain'))
    
    if len(monthly_data)>0:
        monthly_data[['NO_KETENTUAN','TENTANG']] = monthly_data['JUDUL'].apply(split_tentang).apply(pd.Series)
        excel_buffer = BytesIO()
        excel_column = ['REGULATOR','NO_KETENTUAN','TANGGAL_REGULASI_EFEKTIF','TENTANG']
        monthly_data[excel_column].to_excel(excel_buffer,index=False,sheet_name='Laporan Bulanan')
        excel_buffer.seek(0)
        attachment = MIMEApplication(excel_buffer.read(),_subtype='xlsx')
        attachment.add_header('Content-Disposition','attachment',filename='Laporan_Bulanan.xlsx')
        message.attach(attachment)
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com',465) as server:
            server.login(sender_email,password)
            server.sendmail(sender_email,receiver,message.as_string())
            print('Email notifikasi berhasil dikirim')
    except Exception as e:
        print(f'Gagal mengirim email') #Implement Logging

def push_rancangan_notification(df,email):
    subject = '[Pemberitahuan] Terdapat Rancangan Regulasi Baru dari Regulator Otoritas Jasa Keuangan'
    list_rancangan = '\n'.join([f"\nNama Regulator: {row['REGULATOR']}\nNama Rancangan Regulasi: {row['JUDUL']}\nLink Rancangan: {row['LINK_RANCANGAN']}\nWaktu Terbit: {row['TIMESTAMP']}"for index,row in df.iterrows()])
    body = f"""Dear Kak Trixie,
    
Saya berharap Anda dalam keadaan baik. Saya ingin melaporkan bahwa terdapat rancangan regulasi baru pada situs regulator Otoritas Jasa Keuangan. Detail dari rancangan baru tersebut adalah sebagai berikut :
    {list_rancangan}
    
Saya harap informasi yang saya berikan dapat bermanfaat. Jika terdapat pertanyaan dan juga keluhan, mohon untuk menghubungi saya dengan alamat email ini. 

Terima kasih atas Perhatiannya
Hormat Saya,
Reyhan Dwi Prasetyo
    """
    sender = SENDER_EMAIL
    receiver = email 
    password = APP_PASSWORD
    message = MIMEMultipart()
    message['From'] = sender
    message['To'] = receiver
    message['Subject'] = subject
    message.attach(MIMEText(body,'plain'))
    excel_buffer = BytesIO()
    excel = df[['REGULATOR','JUDUL','TANGGAL_TERBIT','LINK_RANCANGAN','DESKRIPSI']]
    excel.to_excel(excel_buffer,index=False,sheet_name='Laporan Rancangan Regulasi Baru')
    excel_buffer.seek(0)
    attachment = MIMEApplication(excel_buffer.read(),_subtype="octet-stream")
    attachment.add_header('Content-Disposition','attachment',filename='Laporan Rancangan Regulasi Baru')
    message.attach(attachment)
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com',465) as server:
            server.login(sender,password)
            server.sendmail(sender,receiver,message.as_string())
            #Implement Logging
            print('Notifikasi Rancangan Regulasi Baru berhasil dikirim')
    except Exception as e:
        print(f'Gagal mengirim email: {e}') #IMPLEMENT LOGGING

def send_telegram_message(token,chat_id,message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        'chat_id' : chat_id,
        'text': message,
        'parse_mode' : 'Markdown'
    }
    response = requests.post(url,data=payload)

current_time = datetime.now().time()
start_work_hours = time(9,00)
end_work_hours = time(18,10)
bot_token = "6897064541:AAGxQpMMpXm-mGfSUS7f3bYaODhtTfe1D40"
chat_id = 1965212047
t_message = f"System Berjalan dengan Baik pada {current_time} dan Jangan Lupa Absen pada https://docs.google.com/forms/d/e/1FAIpQLSeRHnMoUTrPy4Y3EmvD6J1tnB93GSQHtadH43I5mDhuPHUIdg/viewform"


#Push Notification
if start_work_hours<= current_time<=end_work_hours :
    start_time = time(16,00)
    end_time = time(16,20)
    scrap_ojk = SCRAP_OJK(URL_OJK)
    scrap_bi = SCRAP_BI(URL_BI)
    scrap_lps = SCRAP_LPS(URL_LPS)
    scrap_selps = SCRAP_SELPS(URL_SELPS)
    scrap_rojk = SCRAP_ROJK(URL_ROJK)
    union = pd.concat([scrap_ojk,scrap_bi,scrap_lps,scrap_selps],ignore_index=True)
    new_entries = check_for_new_entries(union)
    new_rancangan = check_for_new_entries_rancangan(scrap_rojk)
    if new_rancangan is not None:
        load_to_database_rancangan(new_rancangan)
        for email in RECIPIENTS:
            push_rancangan_notification(new_rancangan)
    if new_entries is not None:
        new_entries[['NO_KETENTUAN','TENTANG']] = new_entries['JUDUL'].apply(split_tentang).apply(pd.Series)
    load_to_database(new_entries)
    if new_entries is not None:
        for email in RECIPIENTS:
            push_new_regulation_notification(new_entries,email)
    if start_time <= current_time <= end_time:
        for email in RECIPIENTS:
            push_daily_notification(email)
    if is_friday() and start_time<=current_time<=end_time:
        for email in RECIPIENTS:
            push_weekly_notification(email)
    if is_last_weekday_of_month() and start_time<=current_time<=end_time:
        for email in RECIPIENTS:
            push_monthly_regulation(email)
else:
    print("Diluar jam Kerja")

send_telegram_message(bot_token,chat_id,t_message)
