# Regulatory Notification Script

Script  dengan bahasa Pemrograman Python ini dirancang untuk memonitor regulasi baru yang dikeluarkan oleh regulator melalui situs resmi seperti Otoritas Jasa Keuangan (OJK), Bank Indonesia (BI), dan Lembaga Penjamin Simpanan (LPS). Script ini melakukan proses crawling untuk mengekstrak informasi regulasi yang disajikan dalam bentuk tabel pada situs regulator. Setelah data diambil, script membandingkan informasi tersebut dengan database regulasi yang ada (REGULATION_DATABASE.csv dan RANCANGAN_DATABASE.csv) untuk mendeteksi regulasi baru.

Proses pembandingan dilakukan dengan mencocokkan Judul Regulasi. Jika script mendeteksi adanya regulasi baru (yang ditandai oleh judul yang belum terdaftar di database), maka sistem secara otomatis mengirimkan notifikasi melalui protokol SMTP Gmail ke alamat email yang telah ditentukan.

Laporan periodik disusun berdasarkan jadwal yang ditentukan, yaitu harian, mingguan, dan bulanan, dan akan dikirimkan ke email pada waktu dan hari kerja yang telah ditentukan. Proses pemantauan ini dijalankan secara otomatis setiap 30 menit sekali menggunakan CRON Jobs pada sistem operasi Linux.

# Main Features

 1. **Crawling Data Regulasi**
 Mengambil data regulasi dari situs Otoritas Jasa Keuangan, Bank Indonesia dan Lembaga Penjamin Simpanan. Detail dari jenis regulasi yang dilakukan scrapping adalah sebagai berikut :

|Regulator                |Link Situs                         |Jenis Dokumen Regulasi                 |
|----------------|-------------------------------|------------------------------|
|Otoritas Jasa Keuangan (Regulasi)|https://www.ojk.go.id/id/Regulasi/Default.aspx            |Surat Otoritas Jasa Keuangan (SEOJK), Peraturan Otoritas Jasa Keuangan (POJK), Rancangan Regulasi Otoritas Jasa Keuangan            |
|Otoritas Jasa Keuangan (Rancangan Regulasi)          |https://www.ojk.go.id/id/regulasi/otoritas-jasa-keuangan/rancangan-regulasi/default.aspx            |Rancangan Regulasi Otoritas Jasa Keuangan (ROJK)            |
|Bank Indonesia          |https://www.bi.go.id/id/publikasi/peraturan/default.aspx            |Peraturan Anggota Dewan Gubernur (PADG) dan Peraturan Bank Indonesia (PBI)            |
|Lembaga Penjamin Simpanan (Regulasi)          |https://lps.go.id/plps/Peraturan |Peraturan Lembaga Penjamin Simpanan
|Lembaga Penjamin Simpanan (Surat Edaran)          |https://lps.go.id/surat-edaran/ |Surat Edaran Lembaga Penjamin Simpanan

 2. **Deteksi Regulasi Baru**
 Membandingkan hasil ekstraksi informasi pada laman pertama dari situs regulator terkait yang kemudian akan dibandingkan dengan database berformat .csv. Regulasi dianggap baru jika Judul dari Regulasi tersebut tidak terdapat di dalam database. 
 3. **Email Notifikasi**
 Mengirimkan Email Notifikasi dengan detail kondisi sebagai berikut : 

|Email Notifikasi                |Kondisi Email Notifikasi                         |Periode Notifikasi                 |
|----------------|-------------------------------|------------------------------|
|Notifikasi Regulasi Baru| Notifikasi ini langsung dikirimkan apabila script berhasil mendeteksi adanya regulasi baru          |Dikirimkan secara langsung apabila terdeteksi regulasi baru pada hari dan jam kerja.           |
|Notifikasi Laporan Regulasi Harian         |Notifikasi ini dikirim jika sudah waktunya untuk mengirim laporan harian yaitu pada akhir Hari Kerja pada pukul 17.00          | Dikirimkan pada pukul 17.00 setiap Hari Kerja           |
|Notifikasi Laporan Regulasi Mingguan          |Notifikasi ini akan dikirimkan jika waktu untuk mengirimkan laporan Mingguan telah tiba yakni Pada Hari Kerja Terakhir di Minggu Tersebut           |Dikirimkan pada pukul 17.00 setiap Hari Kerja Terakhir pada Minggu Tersebut            |
|Notifikasi Laporan Regulasi Bulanan         |Laporan ini akan dikirimkan jika waktu untuk mengirimkan laporan Bulanan telah tiba yakni Pada Hari Kerja terakhir pada Bulan tersebut |Pukul 17.00 setiap Hari Kerja Terakhir pada Bulan Tersebut

 5. **Scheduling Aktivitas Pemantauan**
 Pemantuan dilakukan selama 30 Menit Sekali selama hari dan jam kerja menggunakan CRON Jobs. Adapun perintah yang dapat dituliskan di dalam crontabnya adalah sebagai berikut : 
 ```
 #Membuka isi dari crontab 
 crontab -l 
 # Mengedit Crontab
 crontab -e
 # Menambahkan Rumus Crontab untuk Deteksi setiap 30 Menit dan menulis status eksekusi pada file cron_log.log
 */30 * * * * cd /file/directory/app.py && /usr/bin/python3/app.py 2>&1 | /usr/bin/sed "s/^/$(/bin/date '+\%Y-\%m-\%d \%H: \%M: \%S') : /" >> cron_log.log
```
 

## Library yang Digunakan

Dalam menjalankan fungsinya, script ini memerlukan pustaka dengan Bahasa Pemrograman Python seperti : 

 - **beautifulsoup4 (BeautifulSoup)** 
 Digunakan untuk melakukan ekstraksi informasi melalui situs regulator (*web scrapping*).
 - **Pandas**
 Digunakan untuk memanipulasi data agar dapat memudahkan proses pengolahan serta eksport pada pengiriman laporan.
 - **email**
 Digunakan untuk mengirimkan notifikasi berupa email melalui protokol SMTP 
 - **requests**
 Digunakan untuk mengirimkan permintaan HTTP pada situs regulator
 - **smtplib**
 Digunakan untuk mengirimkan notifikasi berupa email melalui protokol
 - **calendar**
 Digunakan untuk membantu terkait penjadwalan sistem dalam mengirimkan notifikasi 
 - **datetime**
 Digunakan untuk membantu terkait penjadwalan sistem dalam mengirimkan notifikasi

## Flowchart Script

Keseluruhan Proses yang terjadi dalam Script ini dapat dilihat melalui ilustrasi berikut : 
![Flowchart Script](https://ibb.co.com/sRybrBC)

## Catatan Pengembangan

Terdapat beberapa catatan penting yang perlu diketahui pada saat Pengembangan ini terutama terkait kendala dan juga improvisasi yang dapat dilakukan seperti : 

 - Menyatukan Database Regulasi dengan Database Rancangan dengan merubah struktur data dari Database Regulasi untuk dapat disesuaikan dengan tipe regulasi. Seperti (PADG, PBI, SELPS,ROJK)
 - Melakukan Preprocessing Data Regulasi pada saat Ekstraksi pada Situs Berlangsung (sehingga tidak perlu memisahkan Nomor Ketentuan dan Judul Regulasi) agar tidak membingungkan.
 - Menggunakan Protokol lain selain GMAIL dikarenakan lingkungan Pt Bank XXX yang menggunakan Outlook sebagai sistem surat menyuratnya.
 - Membuat Database selain menggunakan Format .csv sehingga tidak menyebabkan bug apabila Regulasi memiliki Judul yang terdapat tanda koma (,) didalamnya. 
 - Merubah Struktur Database agar lebih relevan dengan kebutuhan bisnis mengenai pelaporan regulasi 
 - Melakukan Hosting dari program agar tidak dijalankan secara Lokal pada laptop pribadi
