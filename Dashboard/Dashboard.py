import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import altair as alt

# Load data
day_df = pd.read_csv("day2.csv")
hour_df = pd.read_csv("hour2.csv")

# Konversi kolom tanggal ke datetime pada day_df
day_df['dteday'] = pd.to_datetime(day_df['dteday'])
day_df['year'] = day_df['dteday'].dt.year
day_df['day_name'] = day_df['dteday'].dt.day_name()

# Konversi kolom tanggal ke datetime pada hour_df
hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])
hour_df['hour'] = hour_df['hr']  # Menyimpan data jam dalam kolom baru jika perlu

# Judul Dashboard
st.title("Dashboard Penyewaan Sepeda 🚲")

# Sidebar - Logo dan Filter
with st.sidebar:
    st.markdown("# Tren Penyewaan Sepeda")
    st.image("logo.png", width=200)

    # Pilih rentang tanggal
    min_date = day_df['dteday'].min()
    max_date = day_df['dteday'].max()
    start_date, end_date = st.date_input("Pilih Rentang Tanggal", [min_date, max_date], min_value=min_date, max_value=max_date)

    # Filter berdasarkan jam
    min_hour = hour_df['hour'].min()
    max_hour = hour_df['hour'].max()
    start_hour, end_hour = st.slider("Pilih Rentang Jam", min_hour, max_hour, (min_hour, max_hour))

    
    # Pilih jenis pengguna
    user_type = st.selectbox("Pilih Jenis Pengguna", ["Semua", "Casual", "Registered"])

# Filter berdasarkan rentang waktu
filtered_day_df = day_df[(day_df['dteday'] >= pd.to_datetime(start_date)) & (day_df['dteday'] <= pd.to_datetime(end_date))]
filtered_hour_df = hour_df[(hour_df['dteday'] >= pd.to_datetime(start_date)) & (hour_df['dteday'] <= pd.to_datetime(end_date))]

# Filter berdasarkan jam
filtered_hour_df = filtered_hour_df[(filtered_hour_df['hour'] >= start_hour) & (filtered_hour_df['hour'] <= end_hour)]

# =========================
# Total Penyewaan per Rentang Tanggal
# =========================
st.subheader(f"Total Penyewaan Sepeda ({start_date} hingga {end_date})")

if user_type == "Casual":
    total_rentals = filtered_day_df['casual'].sum()
elif user_type == "Registered":
    total_rentals = filtered_day_df['registered'].sum()
else:
    total_rentals = filtered_day_df['cnt'].sum()

st.metric(label="Total Penyewaan", value=f"{total_rentals:,}")

# ============================
# Tren Penyewaan per Jam
# ============================
st.subheader("Tren Penyewaan Sepeda per Jam")

hourly_y_col = {
    "Casual": "casual",
    "Registered": "registered",
    "Semua": "cnt"
}[user_type]

# Filter berdasarkan user_type untuk hour_df
filtered_hour_df_user = filtered_hour_df.groupby(['hour'])[hourly_y_col].sum().reset_index()

line_chart_hourly = alt.Chart(filtered_hour_df_user).mark_line().encode(
    x='hour:O',
    y=alt.Y(f'{hourly_y_col}:Q', title='Jumlah Penyewaan'),
    tooltip=['hour', hourly_y_col]
).properties(width=700, height=400)

st.altair_chart(line_chart_hourly, use_container_width=True)

# ============================
# Penyewaan Berdasarkan Hari (Casual vs Registered)
# ============================
st.subheader("Rata-rata Penyewaan Sepeda per Hari dalam Seminggu")

avg_by_day = filtered_day_df.groupby('day_name')[['casual', 'registered']].mean().reindex(
    ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
)

fig, ax = plt.subplots()
ax.bar(avg_by_day.index, avg_by_day['casual'], label='Casual', color='lightcoral')
ax.bar(avg_by_day.index, avg_by_day['registered'], bottom=avg_by_day['casual'], label='Registered', color='skyblue')
ax.set_ylabel('Rata-rata Penyewaan')
ax.set_xlabel('Hari')
ax.set_title('Perbandingan Casual vs Registered')
plt.xticks(rotation=45)
ax.legend()

st.pyplot(fig)

# Footer
st.caption("Sumber data: Dataset Penyewaan Sepeda (day.csv dan hour.csv)")
