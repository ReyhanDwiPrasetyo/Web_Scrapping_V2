# Library Used
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
HEADERS = {
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

# Email Configuration
SENDER_EMAIL = "prasetyoreyhan0509@gmail.com"
RECIPIENTS = ["prasetyoreyhan0509@gmail.com",'Gratia.Trixe@cimbniaga.co.id','Nancy.Sianipar2@cimbniaga.co.id'] #Insert Recipients Email Here
APP_PASSWORD = "mzgt qbqc pbxs hktu" #Insert Sender Gmail APP PASSWORD

def SCRAP_ROJK(url):
    """
    Scrapes Rancangan Otoritas Jasa Keuangan data from the given OJK URL.
    
    Parameters:
        url (str): The URL of the Rancangan OJK page to scrape.
    
    Returns:
        pd.DataFrame: A DataFrame containing scraped data with the following columns:
            - REGULATOR: The name of the regulator (OJK).
            - JUDUL: The title of the rancangan draft.
            - TANGGAL_TERBIT: The publication date of the regulation draft.
            - LINK_RANCANGAN: The link to the detailed regulation draft page.
            - TIMESTAMP: The timestamp when the data was scraped.
            - DESKRIPSI: A description of the regulation draft.
        If an error occurs or no data is found, returns an empty DataFrame or None.
    
    Raises:
        Exception: If any unexpected error occurs during scraping.
    """
    try:
        #Get the current timestamp for logging purposes
        timestamp = datetime.now()
        regulator = 'OJK'
        
        #Send a GET request to the provided URL 
        response = requests.get(url,headers=HEADERS)
        if response.status_code != 200:
            print(f"Error: Failed to retrieve the OJK page. Status code: {response.status_code}")
            return pd.DataFrame()
        
        # Parse the main page using Beautiful Soup
        soup = BeautifulSoup(response.content,'html.parser')
        table = soup.find('table',{'class':"table table-bordered table-styled"})
        rows = table.find_all('tr') #Get all Rows from the Table
        
        #Initiate Empty List to store scrapped value
        data = []
        
        #Iterate over each row except the header
        for row in rows[1:]:
            #Extract all 'td' elements to access relevant information
            td_tag = row.find_all('td')
            # Extract Relevant Data from the row
            judul_rancangan = td_tag[0].text.strip()
            deskripsi = td_tag[1].text.strip().replace('\u200b','') #Remove unwanted Unicode Characters
            link = 'https://www.ojk.go.id' +row.find('a')['href'] #Construct full link to the documents
            
            #Send another get requests to Extract detail information
            response2 = requests.get(link,headers=HEADERS)
            if response2.status_code != 200:
                print('Failed to retrieve Rancangan Page')
            
            #Extract Content from child pages of the rancangan regulasi
            soup2 = BeautifulSoup(response2.content,'html.parser')
            tanggal_rancangan = soup2.find('span',{'class':'display-date-text'}).text.strip()
            if not tanggal_rancangan:
                print('Warning : Unable to Find info for waktu berlaku. Skipping')
                continue # Skip the process if the publication date is missing (Terkadang regulator mengunci laman sehingga tidak dapat diakses)
            
            #Append Extracted Data to empty list. 
            data.append({'REGULATOR':regulator,'JUDUL':judul_rancangan,'TANGGAL_TERBIT':tanggal_rancangan,'LINK_RANCANGAN':link,'TIMESTAMP':timestamp,'DESKRIPSI':deskripsi})
        
        #Create dataframe that contains information from the appended    
        df = pd.DataFrame(data)
        return df 
    
    except Exception as e:
        print(f"Error in SCRAP_ROJK: {e}")
        return None

def SCRAP_OJK(url):
    """
    Scrapes regulation data from the specified OJK page.
    
    Parameters:
        url (str): The URL of the OJK page to scrape.
    
    Returns:
        pd.DataFrame: A DataFrame containing the following columns:
            - REGULATOR: The name of the regulator (OJK).
            - JUDUL: The complete title of the regulation.
            - TANGGAL_REGULASI_EFEKTIF: The effective date of the regulation.
            - LINK_REGULASI: The link to the detailed regulation document.
            - TIMESTAMP: The timestamp when the data was scraped.
        If an error occurs or no data is available, returns an empty DataFrame or None.
    
    Raises:
        Exception: If any unexpected error occurs during the scraping process.
    """
    try:
        #Get the current timestamp for logging purposes
        timestamp = datetime.now()
        regulator = 'OJK' #Regulator Name
        
        # Send a GET Request to the provided URL 
        response = requests.get(url,headers=HEADERS)
        if response.status_code != 200:
                print(f"Error: Failed to retrieve the OJK page. Status code: {response.status_code}")
                return pd.DataFrame()
            
        #Parse the main page using Beautiful Soup
        soup = BeautifulSoup(response.content, "html.parser")
        table = soup.find("table", {"class": "table table-bordered table-styled"})
        rows = table.find_all("tr") # Get all rows in the table
        
        #Initiate empty List
        data = []
        
        # Iterate through each row except for the header
        for row in rows[1:]:
            #Extract the title of the regulation
            judul = row.find('td').text.strip()
            
            #Change the regulation title aliases for clarity
            if 'seojk' in judul.lower():
                judul = "Surat Edaran Otoritas Jasa Keuangan Nomor "+judul
            else:
                judul = "Peraturan Otoritas Jasa Keuangan Nomor "+judul
            
            #Extract additionals detail about the regulation
            strong_tag = row.find('strong') #Find strong element
            tentang = strong_tag.find('a').text.strip() #Regulation Description
            link = 'https://www.ojk.go.id'+strong_tag.find('a')['href'] #Full link to the regulation pages
            
            #Concatenate regulation title and 'tentang' information to gain full documents name.
            judul = " ".join((judul + ' tentang '+tentang).strip().split())
            
            #Parsed to the regulation page to extract another relevant information 
            response2 = requests.get(link,headers=HEADERS)
            if response2.status_code != 200:
                print('Failed to Retrieve Data')
            
            #Parsed using another BeautifulSoup Library
            soup2 = BeautifulSoup(response2.content,'html.parser')
            waktu_berlaku = soup2.find('span',{'class':'display-date-text tanggal-2'}).text.strip()
            if not waktu_berlaku:
                print('Warning: Unable to find info for waktu berlaku..Skipping')
                continue #Skip the page if effective date cannot be extracted (Behaviour OJK untuk mengunci laman regulasi ketika regulasi baru dikeluarkan)
            
            #Append the extracted data to the list
            data.append({
                'REGULATOR': regulator,'JUDUL':judul,'TANGGAL_REGULASI_EFEKTIF':waktu_berlaku,'LINK_REGULASI':link,'TIMESTAMP':timestamp
            })
        df = pd.DataFrame(data)
        return df
    
    except Exception as e:
        print(f"Error in SCRAP_OJK: {e}")
        return None

def SCRAP_BI(url):
    """
    Scrapes regulatory data from the specified Bank Indonesia (BI) page.
    
    Parameters:
        url (str): The URL of the BI page to scrape.
    
    Returns:
        pd.DataFrame: A DataFrame containing the following columns:
            - REGULATOR: The name of the regulator (BI).
            - JUDUL: The title of the regulation.
            - TANGGAL_REGULASI_EFEKTIF: The publication date of the regulation.
            - LINK_REGULASI: The link to the detailed regulation document.
            - TIMESTAMP: The timestamp when the data was scraped.
        If an error occurs or no data is available, returns an empty DataFrame or None.
    
    Raises:
        Exception: If any unexpected error occurs during the scraping process.
    """

    try:
        #Get the current timestamp for logging purposes
        timestamp = datetime.now()
        regulator = 'BI' #Regulator name
        
        #Send a GET Request to the provided URL
        response = requests.get(url,headers=HEADERS)
        if response.status_code != 200:
                print(f"Error: Failed to retrieve the BI page. Status code: {response.status_code}")
                return pd.DataFrame()
            
        # Parse the main page using BeautifulSoup
        soup = BeautifulSoup(response.content, "html.parser")
        tag_list = soup.find_all('div',class_='media media--pers') #Extract all tag that contains relevant information

        #Initiate empty list to be appended by scrapped information
        data = []
        
        #Iterate over each tag in the content block that has been scrapped
        for tag in tag_list:
            #Extract and preprocessed the regulation title
            judul = " ".join(tag.find('a',class_='mt-0 media__title ellipsis--two-line').get_text(strip=True).replace('\u200b','').replace('\r','').replace('\n','').split())
            #Extract the regulation page to get the detailed information 
            link_judul = tag.a['href']
            #Extract the publcation date
            waktu_berlaku = tag.find('div',class_='media__subtitle').get_text(strip=True)
            
            #Append the extracted data to the empty list that has been initiated
            data.append({
            'REGULATOR':regulator,'JUDUL':judul,'TANGGAL_REGULASI_EFEKTIF':waktu_berlaku,'LINK_REGULASI':link_judul,'TIMESTAMP':timestamp
            })
        df = pd.DataFrame(data)
        return df
    except Exception as e:
        print(f"Error in SCRAP_BI: {e}")
        return None

def SCRAP_SELPS(url):
    """
    Scrapes regulatory data from the specified Lembaga Penjamin Simpanan (LPS) page.
    
    Parameters:
        url (str): The URL of the LPS page to scrape.
    
    Returns:
        pd.DataFrame: A DataFrame containing the following columns:
            - REGULATOR: The name of the regulator (LPS).
            - JUDUL: The title of the regulation or announcement.
            - TANGGAL_REGULASI_EFEKTIF: The publication date of the regulation.
            - LINK_REGULASI: The link to the detailed regulation document.
            - TIMESTAMP: The timestamp when the data was scraped.
        If an error occurs or no data is available, returns an empty DataFrame or None.
    
    Raises:
        Exception: If any unexpected error occurs during the scraping process.
    """
    try:
        #Get the current timestamp for logging and report purposes
        timestamp = datetime.now()
        regulator = 'LPS' #regulator name
        
        #Send a GET request to the provided URl
        response = requests.get(url,headers=HEADERS)
        if response.status_code != 200:
            print(f"Error: Failed to retrieve the LPS page. Status code: {response.status_code}")
            return pd.DataFrame()
        
        #Parse the main page using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        tag_list = soup.findAll('div',class_='content') #Extract all tag in content blocks
        
        #Initiate Empty List to be appended by relevant information
        data = []
        
        #Iterate over each tag in the content block
        for tag in tag_list:
            
            #Extract the title of the regulation
            judul = " ".join(tag.find('span',class_='screen-reader-text').get_text(strip=True).split())
            #Extract the link to the detailed regulation document
            link_judul = tag.a['href']
            #Extract the publication date
            waktu_berlaku = tag.find('span',class_='meta-date').get_text(strip=True)
            
            #Append the extracted data to the list
            data.append({
                'REGULATOR':regulator,'JUDUL':judul,'TANGGAL_REGULASI_EFEKTIF':waktu_berlaku,'LINK_REGULASI':link_judul,'TIMESTAMP':timestamp
            })
        #Convert the appended data in the list to a Pandas Dataframe
        df = pd.DataFrame(data)
        return df
    except Exception as e:
        print(f"Error in SCRAP_SELPS: {e}")
        return None
    
def SCRAP_LPS(url):
    """
    Scrapes regulatory data from the specified Lembaga Penjamin Simpanan (LPS) page.

    Parameters:
        url (str): The URL of the LPS page to scrape.

    Returns:
        pd.DataFrame: A DataFrame containing the following columns:
            - REGULATOR: The name of the regulator (LPS).
            - JUDUL: The title of the regulation or announcement.
            - TANGGAL_REGULASI_EFEKTIF: The publication date of the regulation.
            - LINK_REGULASI: The link to the detailed regulation document.
            - TIMESTAMP: The timestamp when the data was scraped.
        If an error occurs or no data is available, returns an empty DataFrame or None.

    Raises:
        Exception: If any unexpected error occurs during the scraping process.
    """
    try:
        # Record the Current timestamp for tracking when the data was scrapped
        timestamp = datetime.now()
        regulator = 'LPS' # Define the regulator name
        
        #Send an HTTP GET request to the specified URL
        response = requests.get(url,headers=HEADERS)
        if response.status_code != 200:
                print(f"Error: Failed to retrieve the LPS page. Status code: {response.status_code}")
                return pd.DataFrame()
            
        #Parse the response content using Beautiful Soup
        soup = BeautifulSoup(response.content, "html.parser")
        tag_list = soup.findAll('div',class_='content') #Extract all tag card in the content block in the pages.
        
        #Initiate Empty List to be appended by extracted information
        data = []
        
        #Iterate over the extracted content blocks
        for tag in tag_list :
            #Extract the title of the regulation
            judul = " ".join(tag.find('span',class_='screen-reader-text').get_text(strip=True).split())
            #Extract the link to the regulation pages
            link_judul = tag.a['href']
            #Extract the publication date and clean up extra spaces
            waktu_berlaku = " ".join(tag.find('span',class_='meta-date').get_text(strip=True).split())
            
            #Appended the Extracted Information
            data.append({
                'REGULATOR':regulator,'JUDUL':judul,'TANGGAL_REGULASI_EFEKTIF':waktu_berlaku,'LINK_REGULASI':link_judul,'TIMESTAMP':timestamp,
            })
        
        #Convert the list of extracted data into a Pandas Dataframe
        df = pd.DataFrame(data)
        return df
    
    except Exception as e:
        print(f"Error in SCRAP_LPS: {e}")
        return None

def check_for_new_entries(df):
    """
    Checks for new entries in the given DataFrame by comparing it to an existing database.

    Parameters:
        df (pd.DataFrame): The DataFrame containing the latest scraped data. 
            Must include a column named 'JUDUL'.

    Returns:
        pd.DataFrame: A DataFrame containing rows that are not present in the existing database.
            If no new entries are found, returns an empty DataFrame.
    """
    #Load the existing database from a CSV file
    database = pd.read_csv(DATABASE_PATH)
    
    #Identify rows in the new dataframe (df) that title are not in the database (csv file)
    new_entries = df[~df['JUDUL'].isin(database['JUDUL'])]
    
    #If there's new entries, return new entries
    if not new_entries.empty:
        return new_entries
    
def check_for_new_entries_rancangan(df):
    """
    Checks for new entries in the given DataFrame by comparing it to an existing database of Rancangan data.

    Parameters:
        df (pd.DataFrame): The DataFrame containing the latest scraped data. 
            Must include a column named 'JUDUL'.

    Returns:
        pd.DataFrame: A DataFrame containing rows that are not present in the existing Rancangan database.
            If no new entries are found, returns an empty DataFrame.
    """
    #Load the existing Rancangan Database from a CSV File
    database = pd.read_csv(RANCANGAN_PATH)
    
    #Identify rows in the new dataframe (df) that are not in the Rancangan Database
    new_entries = df[~df['JUDUL'].isin(database['JUDUL'])]
    
    #Return new entry if theres any
    if not new_entries.empty:
        return new_entries

def load_to_database_rancangan(df):
    """
    Loads new entries from a DataFrame into the Rancangan database file.

    Parameters:
        df (pd.DataFrame): The DataFrame containing new entries to be added to the database.
            If `df` is None or empty, no changes are made to the database.

    Returns:
        pd.DataFrame: The updated Rancangan database, including the newly added entries.
    
    Side Effects:
        Updates the Rancangan database file at the path specified by `RANCANGAN_PATH`.
    """
    
    # Load the existing database from a CSV File
    database = pd.read_csv(RANCANGAN_PATH)
    
    if df is not None:
        #Concatenate the new entries to the existing database
        database = pd.concat([database, df],ignore_index=True)
        #Save the updated database back to the CSV File
        database.to_csv(RANCANGAN_PATH,index=False)
        return database
    else:
        print('Tidak ada entri baru')

def load_to_database(df):
    """
    Loads new entries into the main database and assigns unique IDs and notification statuses.

    Parameters:
        df (pd.DataFrame): The DataFrame containing new entries to be added to the database.
            If `df` is None or empty, no changes are made to the database.

    Returns:
        pd.DataFrame: The updated database including the new entries, or None if no entries were added.

    Side Effects:
        Updates the database file at the path specified by `DATABASE_PATH`.
        Logs actions performed and any potential issues into a log file.
    """
    #Load the existing databases
    database = pd.read_csv(DATABASE_PATH)
    if df is not None:
        df['NOTIFICATION_STATUS'] = 'NOT SENT' #NOTE THIS COLUMN IS NOT RELEVANT TO THE SCRAPPING PROCESS. PLEASE SKIP THIS
        #Assign unique IDs to the new entries
        start_id = int(database['ID_REGULASI'].max())+1
        df['ID_REGULASI'] = range(start_id,start_id+len(df))
        
        #Concatenate the new entries to the database
        database = pd.concat([database,df],ignore_index=True)
        
        #Save the updated database back to the file
        database.to_csv(DATABASE_PATH,index=False)
        return database
    else: 
        print('Tidak ada entri baru') 

def split_tentang(judul):
    """
    Splits a regulatory title into its "nomor ketentuan" (regulation number) and "tentang" (regulation subject).

    This function identifies the position of the word "tentang" in the input string. If found, it splits the string
    into two parts:
      - Before "tentang": Considered as the regulation number (`no_ketentuan`).
      - After "tentang": Considered as the regulation subject (`tentang`).

    Parameters:
        judul (str): The full title of the regulation as a string.

    Returns:
        tuple: A tuple containing:
            - no_ketentuan (str): The part of the title before the word "tentang".
            - tentang (str): The part of the title after the word "tentang". If "tentang" is not found, this will be an empty string.

    Example:
        >>> split_tentang("Peraturan Nomor 12 tentang Pengawasan Perbankan")
        ("Peraturan Nomor 12", "Pengawasan Perbankan")
        
        >>> split_tentang("Surat Edaran Nomor 7")
        ("Surat Edaran Nomor 7", "")
    """
    #Convert the title to lowercase for case-insensitive search
    judul_lower = judul.lower()
    
    #Find the position of the word 'tentang'
    posisi_tentang = judul_lower.find('tentang')
    
    #If "tentang" is found, split the title
    if posisi_tentang != -1:
        no_ketentuan = judul[:posisi_tentang].strip()
        tentang = judul[posisi_tentang+len('tentang'):].strip()
    else:
        #if not found, treat the entire title as 'no ketentuan'
        no_ketentuan = judul 
        tentang = ''
    return no_ketentuan,tentang

def is_weekday():
    """
    Checks if today is a weekday (Monday to Friday).

    This function returns `True` if the current day is a weekday (i.e., Monday to Friday), and `False` if it is a weekend (Saturday or Sunday).

    Returns:
        bool: `True` if today is a weekday, `False` if today is a weekend.

    Example:
        >>> is_weekday()
        True   # If today is a weekday (e.g., Monday, Tuesday, etc.)
        False  # If today is a weekend (Saturday or Sunday)
    """
    #Get the current day of the week
    today = datetime.now().weekday()
    return today < 5

def is_friday():
    """
    Checks if today is Friday.

    This function returns `True` if today is Friday, and `False` if it is any other day of the week.

    Returns:
        bool: `True` if today is Friday, `False` otherwise.

    Example:
        >>> is_friday()
        True   # If today is Friday
        False  # If today is any other day (e.g., Monday, Tuesday, etc.)
    """
    return datetime.now().weekday()==4

def is_last_weekday_of_month():
    """
    Checks if today is the last weekday of the current month.

    This function returns `True` if today is the last weekday (Monday to Friday) of the current month,
    and `False` if today is not the last weekday.

    Returns:
        bool: `True` if today is the last weekday of the month, `False` otherwise.

    Example:
        >>> is_last_weekday_of_month()
        True   # If today is the last weekday of the month
        False  # If today is not the last weekday
    """
    today = datetime.now() #Get today's date and time
    last_day_of_month = calendar.monthrange(today.year,today.month)[1] #Get the last day of the month
    last_date = datetime(today.year,today.month,last_day_of_month) # Create a datetime object for the last day
    
     # Adjust the last date to the last weekday if it's a weekend (Saturday or Sunday)
    while last_date.weekday() >4:
        last_date -= timedelta(days=1)
    
     # Compare today's date with the adjusted last weekday of the month
    return today.date() == last_date.date()

def send_telegram_message(token,chat_id,message):
    """
    Sends a message to a specified Telegram chat using a bot.

    This function allows you to send a text message to a Telegram chat via a bot using the Telegram Bot API.
    The message is sent in Markdown format.

    Parameters:
        token (str): The bot's API token, provided by Telegram when creating the bot.
        chat_id (str): The chat ID of the recipient, which can be a user, group, or channel.
        message (str): The text message to send to the Telegram chat.

    Returns:
        None

    Example:
        >>> send_telegram_message("123456:ABC-XYZ", "@mygroup", "Hello, this is a test message!")
        Message sent successfully to the specified Telegram chat.

    Notes:
        - The message is sent using the `parse_mode` parameter set to 'Markdown', which allows for basic text formatting.
        - Ensure that the `chat_id` is correct, and the bot has the necessary permissions to send messages to the chat.
    """
    # Telegram API endpoint to send the message
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    # The payload to be sent with the request, including chat_id and message content
    payload = {
        'chat_id' : chat_id,
        'text': message,
        'parse_mode' : 'Markdown'
    }
    response = requests.post(url,data=payload)
    
def push_new_regulation_notification(df,email):
    """
    Sends an email notification about new regulations from regulators.

    This function generates an email containing details of new regulations and sends it to a specified recipient.

    Parameters:
        df (pandas.DataFrame): A DataFrame containing details of new regulations. The DataFrame should include the columns:
            - REGULATOR: Name of the regulator
            - JUDUL: Title of the regulation
            - LINK_REGULASI: Link to the regulation
            - TIMESTAMP: Timestamp of when the regulation was found
        email (str): The recipient's email address where the notification will be sent.

    Returns:
        None

    Example:
        >>> push_new_regulation_notification(df, "example@domain.com")
        Email notification sent successfully.
    """
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
    sender = SENDER_EMAIL #Sender Email Address
    receiver = email #Recipient Email Address
    password = APP_PASSWORD #App Password for the sender's email account
    
    # Prepare the email message
    message = MIMEMultipart()
    message['From'] = sender
    message['To'] = receiver
    message['Subject'] = subject
    message.attach(MIMEText(body,'plain')) #Attach the body text to the message
    
    #Send the email using Gmail SMTP Server
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com',465) as server:
            server.login(sender,password) #Login to the email account
            server.sendmail(sender,receiver,message.as_string()) #Send the email
            print('Email Notifikasi berhasil dikirim')
    except Exception as e:
        print(f'Gagal mengirim email: {e}') 
        
def push_daily_notification(email):
    """
    Sends a daily email notification about new regulations detected on the specified date.

    This function sends a daily summary email to a given recipient with information about 
    the new regulations detected today, including the total count of new regulations, 
    and attaches an Excel file containing the relevant details if applicable.

    Parameters:
        email (str): The recipient's email address to send the daily summary to.

    Returns:
        None

    Example:
        >>> push_daily_notification("example@domain.com")
        Email notification sent successfully.
    """
    # Load the database containing regulation data
    database = pd.read_csv(DATABASE_PATH)
    # Get today's date and filter the regulations that were added today
    today = datetime.now().strftime('%Y-%m-%d')
    query = database[pd.to_datetime(database['TIMESTAMP']).dt.strftime('%Y-%m-%d')==today]
    
    # Prepare the email subject and body
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
    sender = SENDER_EMAIL #Sender email address
    receiver = email #Recipients Email Address
    password = APP_PASSWORD # App Password for the sender email
    
    #Create email message
    message = MIMEMultipart()
    message['From'] = sender
    message['To'] = receiver
    message['Subject'] = subject
    message.attach(MIMEText(body,'plain'))
    
    # Attach the Excel file if there are new regulations
    attachment = None
    if len(query) > 0:
        excel_buffer = BytesIO()
        excel = query[['REGULATOR','NO_KETENTUAN','TANGGAL_REGULASI_EFEKTIF','TENTANG']]
        excel.to_excel(excel_buffer,index=False,sheet_name='Laporan_Harian')
        excel_buffer.seek(0)
        attachment = MIMEApplication(excel_buffer.read(),_subtype='xlsx')
        attachment.add_header('Content-Disposition','attachment',filename='Laporan_Harian.xlsx')
        message.attach(attachment)
    
    # Send the email using Gmail's SMTP server
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com',465) as server:
            server.login(sender,password)
            server.sendmail(sender,receiver,message.as_string())
            #Implement Logging
            print('Email berhasil dikirim')
    except Exception as e:
        print('Gagal Mengirim Email')
    
    # Update the notification status in the database to 'SENT'
    database.loc[query.index,'NOTIFICATION_STATUS'] = 'SENT'
    database.to_csv('REGULATION_DATABASE.csv',index=False)

def push_weekly_notification(email):
    """
    Sends a weekly email notification summarizing new regulations detected in the last week.

    This function sends a weekly summary email to a given recipient with information about 
    the new regulations detected over the past week, including the total count of new regulations, 
    and attaches an Excel file containing the relevant details if applicable.

    Parameters:
        email (str): The recipient's email address to send the weekly summary to.

    Returns:
        None
    """
    #Load the database containing regulation data
    database = pd.read_csv(DATABASE_PATH)
    database['TIMESTAMP'] = pd.to_datetime(database['TIMESTAMP'])
    
    #Calculate the start and end dates of the past week
    today = pd.Timestamp.now()
    start_day = today - pd.DateOffset(days=6) 
    end_day = today
    
    
    # Filter the regulations that were added within the past week and that need notification
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
    sender = SENDER_EMAIL #Sender Email
    receiver = email # Recipients Email
    password = APP_PASSWORD # App Password for the sender email address
    
    #Create email message
    message = MIMEMultipart()
    message['From'] = sender
    message['To'] = receiver
    message['Subject'] = subject
    message.attach(MIMEText(body,'plain')) #Attach the body text to the message
    
    # Attach the Excel file if there are new regulations in the past week
    if len(weekly_data)>0:
        excel_buffer = BytesIO()
        excel_column = ['REGULATOR','NO_KETENTUAN','TANGGAL_REGULASI_EFEKTIF','TENTANG']
        weekly_data[excel_column].to_excel(excel_buffer,index=False,sheet_name='Laporan Mingguan')
        excel_buffer.seek(0)
        attachment = MIMEApplication(excel_buffer.read(),_subtype='xlsx')
        attachment.add_header('Content-Disposition','attachment',filename='Laporan_Mingguan.xlsx')
        message.attach(attachment)
    try:
        #Send the email using Gmail's SMTP Server
        with smtplib.SMTP_SSL('smtp.gmail.com',465) as server:
            server.login(sender,password)
            server.sendmail(sender,receiver,message.as_string())
            print('Email Notifikasi Berhasil dikirim')
    except Exception as e:
        print('Error') 
        
def push_monthly_regulation(email):
    """
    Sends a monthly email notification summarizing new regulations detected in the current month.

    This function sends a monthly summary email to a given recipient with information about 
    the new regulations detected in the current month, including the total count of new regulations, 
    and attaches an Excel file containing the relevant details if applicable.

    Parameters:
        email (str): The recipient's email address to send the monthly summary to.

    Returns:
        None

    Example:
        >>> push_monthly_regulation("example@domain.com")
        Email notification sent successfully.

    Notes:
        - The function queries the database for regulations added in the current month and formats the results into a summary email.
        - An Excel file will be attached if new regulations were detected in the current month.
        - The email is sent through Gmail's SMTP server, requiring a sender email (`SENDER_EMAIL`) and an app-specific password (`APP_PASSWORD`).
    """
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
    sender_email = SENDER_EMAIL #Sender Email Address
    receiver = email #Recipients Email Address
    password = APP_PASSWORD #App Password for the Sender email
    
    #Create the email message
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver
    message['Subject'] = subject
    message.attach(MIMEText(body,'plain'))
    
    # If there are new regulations, attach an Excel file with details
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
         # Send the email using Gmail's SMTP server
        with smtplib.SMTP_SSL('smtp.gmail.com',465) as server:
            server.login(sender_email,password)
            server.sendmail(sender_email,receiver,message.as_string())
            print('Email notifikasi berhasil dikirim')
    except Exception as e:
        print(f'Gagal mengirim email') #Implement Logging

def push_rancangan_notification(df,email):
    """
    Sends an email notification about new draft regulations from the Otoritas Jasa Keuangan (OJK).

    This function sends an email notification to a specified recipient with details about new draft regulations
    from OJK. The email includes a summary of the draft regulations and an attachment containing the full details
    in an Excel file.

    Parameters:
        df (pandas.DataFrame): A DataFrame containing information about the new draft regulations.
        email (str): The recipient's email address to send the notification to.

    Returns:
        None

    Example:
        >>> push_rancangan_notification(df, "example@domain.com")
        Email notification sent successfully.

    Notes:
        - The function expects the DataFrame to contain specific columns: 'REGULATOR', 'JUDUL', 'LINK_RANCANGAN', 'TIMESTAMP'.
        - The function sends an email through Gmail's SMTP server using a sender email (`SENDER_EMAIL`) and an app-specific password (`APP_PASSWORD`).
        - The email includes an attachment with the draft regulation details in Excel format.
    """
    #Prepare the Email Subject and Body
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
    # Sender and Recipient Email
    sender = SENDER_EMAIL
    receiver = email 
    password = APP_PASSWORD
    
    #Create email message
    message = MIMEMultipart()
    message['From'] = sender
    message['To'] = receiver
    message['Subject'] = subject
    message.attach(MIMEText(body,'plain'))
    
    # Prepare and attach the Excel file with draft regulation details
    excel_buffer = BytesIO()
    excel = df[['REGULATOR','JUDUL','TANGGAL_TERBIT','LINK_RANCANGAN','DESKRIPSI']]
    excel.to_excel(excel_buffer,index=False,sheet_name='Laporan Rancangan Regulasi Baru')
    excel_buffer.seek(0)
    
    # Create the attachment and add it to the email message
    attachment = MIMEApplication(excel_buffer.read(),_subtype="octet-stream")
    attachment.add_header('Content-Disposition','attachment',filename='Laporan Rancangan Regulasi Baru')
    message.attach(attachment)
    try:
         # Send the email using Gmail's SMTP server
        with smtplib.SMTP_SSL('smtp.gmail.com',465) as server:
            server.login(sender,password)
            server.sendmail(sender,receiver,message.as_string())
            #Implement Logging
            print('Notifikasi Rancangan Regulasi Baru berhasil dikirim')
    except Exception as e:
        print(f'Gagal mengirim email: {e}') 

# Constants for working hours and Telegram notification setup
current_time = datetime.now().time()
start_work_hours = time(9,00)# Start of workday (9:00 AM)
end_work_hours = time(19,10)  # End of workday (6:10 PM)


# Check if the current time is within the working hours
if start_work_hours <= current_time <= end_work_hours:
    # Define the time window for sending reports (4:00 PM - 4:20 PM)
    report_start_time = time(18,00)
    report_end_time = time(19,10)
    
     # Scrape data from various regulatory bodies
    scrap_ojk = SCRAP_OJK(URL_OJK) #OJK Scrap
    scrap_bi = SCRAP_BI(URL_BI) #Bank Indonesia Scrap
    scrap_lps = SCRAP_LPS(URL_LPS) #LPS Scrap
    scrap_selps = SCRAP_SELPS(URL_SELPS) #SELPS Scrap
    scrap_rojk = SCRAP_ROJK(URL_ROJK) #ROJK SCRAP
    
    # Combine data from all sources into a single DataFrame
    union = pd.concat([scrap_ojk,scrap_bi,scrap_lps,scrap_selps],ignore_index=True)
    
    # Check for new regulatory entries in the scraped data
    new_entries = check_for_new_entries(union)
    
    # Process new drafts (rancangan regulasi)
    new_rancangan = check_for_new_entries_rancangan(scrap_rojk)
    if new_rancangan is not None:
        load_to_database_rancangan(new_rancangan)# Load new drafts into the database
        for email in RECIPIENTS: # Send notifications for new drafts
            push_rancangan_notification(new_rancangan)
            
    # Process new regulations
    if new_entries is not None:
        # Split 'TENTANG' from 'JUDUL' to extract relevant information
        new_entries[['NO_KETENTUAN','TENTANG']] = new_entries['JUDUL'].apply(split_tentang).apply(pd.Series)
    load_to_database(new_entries)
    
    # Send notifications for new regulations
    if new_entries is not None:
        for email in RECIPIENTS:
            push_new_regulation_notification(new_entries,email)
            
    # Send daily notifications (between 5:00 PM - 5:20 PM)        
    if report_start_time <= current_time <= report_end_time:
        for email in RECIPIENTS:
            push_daily_notification(email)
            
    # Send weekly notifications (on Friday between 5:00 PM - 5:20 PM)
    if is_friday() and report_start_time<=current_time<=report_end_time:
        for email in RECIPIENTS:
            push_weekly_notification(email)
    
    # Send monthly notifications (on the last weekday of the month between 5:00 PM - 5:20 PM)
    if is_last_weekday_of_month() and report_start_time<=current_time<=report_end_time:
        for email in RECIPIENTS:
            push_monthly_regulation(email)