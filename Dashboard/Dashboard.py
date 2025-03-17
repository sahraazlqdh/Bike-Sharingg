import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Load dataset
@st.cache_data
def load_data():
    day_df = pd.read_csv("Dashboard/day.csv")
    hour_df = pd.read_csv("Dashboard/hour.csv")
    return day_df, hour_df

day_df, hour_df = load_data()

# Sidebar
st.sidebar.title("Dashboard Penyewaan Sepeda")
option = st.sidebar.selectbox("Pilih Visualisasi:", 
                              ["Tren Penyewaan Sepeda", "Penyewaan Berdasarkan Hari", 
                               "Perbandingan Hari Kerja vs Akhir Pekan", 
                               "Perbandingan Penyewaan Berdasarkan Waktu"])

# 1️⃣ **Tren Penyewaan Sepeda (2011-2012)**
if option == "Tren Penyewaan Sepeda":
    st.title("📈 Tren Penyewaan Sepeda (2011-2012)")
    
    # Mengubah tahun dan bulan menjadi format kontinu (misalnya, Jan 2011 = 1, Jan 2012 = 13)
    day_df['time_index'] = day_df['yr'].replace({0: 0, 1: 12}) + day_df['mnth']

    # Menghitung total penyewaan sepeda per bulan dalam urutan waktu kontinu
    monthly_rentals = day_df.groupby('time_index')['cnt'].sum().reset_index()

    # Visualisasi tren penyewaan sepeda sebagai satu garis kontinu
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.lineplot(data=monthly_rentals, x='time_index', y='cnt', marker='o', color='b', ax=ax)

    # Menyesuaikan label sumbu x
    ax.set_xticks(range(1, 25))
    ax.set_xticklabels(['Jan 2011', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des',
                        'Jan 2012', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des'],
                       rotation=45)

    # Label dan judul
    ax.set_title("Tren Penyewaan Sepeda (2011-2012)")
    ax.set_xlabel("Bulan")
    ax.set_ylabel("Total Penyewaan")

    st.pyplot(fig)

elif option == "Penyewaan Berdasarkan Hari":
    st.title("📅 Total Penyewaan Sepeda per Hari dalam Seminggu")

    # Pastikan weekday masih berupa angka sebelum dipetakan
    if day_df['weekday'].dtype != 'int64':  
        day_df['weekday'] = pd.to_numeric(day_df['weekday'], errors='coerce')

    # Mengatur label hari dalam seminggu
    weekday_labels = {0: 'Senin', 1: 'Selasa', 2: 'Rabu', 3: 'Kamis', 
                      4: 'Jumat', 5: 'Sabtu', 6: 'Minggu'}
    day_df['weekday'] = day_df['weekday'].map(weekday_labels)

    # Pastikan urutan hari benar
    day_order = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
    day_df['weekday'] = pd.Categorical(day_df['weekday'], categories=day_order, ordered=True)

    # Grouping data
    weekday_rentals = day_df.groupby('weekday')['cnt'].sum().reset_index()

    # Membuat visualisasi
    fig, ax = plt.subplots()
    sns.barplot(data=weekday_rentals, x='weekday', y='cnt', palette='Blues', ax=ax)

    plt.xlabel("Hari")
    plt.ylabel("Total Penyewaan")
    plt.xticks(rotation=45)
    plt.title("Total Penyewaan Sepeda per Hari dalam Seminggu")

    st.pyplot(fig)

# 3️⃣ **Perbandingan Hari Kerja vs Akhir Pekan**
elif option == "Perbandingan Hari Kerja vs Akhir Pekan":
    st.title("🏢 vs 🎉 Perbandingan Penyewaan: Hari Kerja vs Akhir Pekan")
    
    # Mengelompokkan data berdasarkan hari kerja dan akhir pekan
    day_df['workingday'] = day_df['workingday'].map({0: 'Akhir Pekan', 1: 'Hari Kerja'})
    workingday_rentals = day_df.groupby('workingday')['cnt'].sum().reset_index()
    
    fig, ax = plt.subplots()
    sns.barplot(data=workingday_rentals, x='workingday', y='cnt', palette='viridis', ax=ax)
    
    plt.xlabel("Kategori Hari")
    plt.ylabel("Total Penyewaan")
    plt.title("Perbandingan Penyewaan Sepeda pada Hari Kerja dan Akhir Pekan")
    st.pyplot(fig)

# 4️⃣ **Perbandingan Penyewaan Berdasarkan Waktu**
elif option == "Perbandingan Penyewaan Berdasarkan Waktu":
    st.title("🌞🌆🌙 Perbandingan Penyewaan Berdasarkan Waktu")

    # Fungsi kategori waktu
    def time_of_day(hour):
        if 6 <= hour < 12:
            return "Pagi"
        elif 12 <= hour < 16:
            return "Siang"
        elif 16 <= hour < 20:
            return "Sore"
        else:
            return "Malam"

    # Tambahkan kolom baru untuk kategori waktu
    hour_df['time_of_day'] = hour_df['hr'].apply(time_of_day)

    # Pisahkan data hari kerja dan akhir pekan
    working_day = hour_df[hour_df['workingday'] == 1]
    weekend = hour_df[hour_df['workingday'] == 0]

    # Hitung rata-rata penyewaan berdasarkan waktu dalam sehari
    working_day_avg = working_day.groupby('time_of_day')['cnt'].mean().reset_index()
    weekend_avg = weekend.groupby('time_of_day')['cnt'].mean().reset_index()

    # Gabungkan kedua dataframe untuk perbandingan
    merged_avg_df = working_day_avg.merge(weekend_avg, on="time_of_day", suffixes=("_workday", "_weekend"))

    # Visualisasi
    fig, ax = plt.subplots(figsize=(8, 5))
    bar_width = 0.4
    x = np.arange(len(merged_avg_df['time_of_day']))

    ax.bar(x - bar_width/2, merged_avg_df['cnt_workday'], bar_width, label="Hari Kerja", color='royalblue')
    ax.bar(x + bar_width/2, merged_avg_df['cnt_weekend'], bar_width, label="Akhir Pekan", color='orange')

    plt.xticks(x, merged_avg_df['time_of_day'])
    plt.xlabel("Waktu dalam Sehari")
    plt.ylabel("Rata-rata Penyewaan Sepeda")
    plt.title("Perbandingan Penyewaan Sepeda Berdasarkan Waktu (Hari Kerja vs Akhir Pekan)")
    plt.legend()
    st.pyplot(fig)

st.sidebar.write("""
### Tampilan Visualisasi:
- 📈 **Tren Penyewaan Sepeda** (2011-2012)
- 📅 **Total Penyewaan per Hari dalam Seminggu**
- 🏢 vs 🎉 **Perbandingan Hari Kerja vs Akhir Pekan**
- 🌞🌆🌙 **Perbandingan Penyewaan Berdasarkan Waktu**
""")
