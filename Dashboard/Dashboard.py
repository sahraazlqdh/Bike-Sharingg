import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import altair as alt

# Load data
day_df = pd.read_csv("day.csv")

# Konversi kolom tanggal ke datetime
day_df['dteday'] = pd.to_datetime(day_df['dteday'])

# Tambahkan kolom tahun dan nama hari
day_df['year'] = day_df['dteday'].dt.year
day_df['day_name'] = day_df['dteday'].dt.day_name()

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

    # Pilih jenis pengguna
    user_type = st.selectbox("Pilih Jenis Pengguna", ["Semua", "Casual", "Registered"])

# Filter berdasarkan rentang waktu
filtered_df = day_df[(day_df['dteday'] >= pd.to_datetime(start_date)) & (day_df['dteday'] <= pd.to_datetime(end_date))]

# =========================
# Total Penyewaan per Rentang Tanggal
# =========================
st.subheader(f"Total Penyewaan Sepeda ({start_date} hingga {end_date})")

if user_type == "Casual":
    total_rentals = filtered_df['casual'].sum()
elif user_type == "Registered":
    total_rentals = filtered_df['registered'].sum()
else:
    total_rentals = filtered_df['cnt'].sum()

st.metric(label="Total Penyewaan", value=f"{total_rentals:,}")

# ============================
# Tren Penyewaan Harian (Line Chart)
# ============================
st.subheader("Tren Penyewaan Sepeda Harian")

y_col = {
    "Casual": "casual",
    "Registered": "registered",
    "Semua": "cnt"
}[user_type]

line_chart = alt.Chart(filtered_df).mark_line().encode(
    x='dteday:T',
    y=alt.Y(f'{y_col}:Q', title='Jumlah Penyewaan'),
    tooltip=['dteday', y_col]
).properties(width=700, height=400)

st.altair_chart(line_chart, use_container_width=True)

# ============================
# Penyewaan Berdasarkan Hari (Casual vs Registered)
# ============================
st.subheader("Rata-rata Penyewaan Sepeda per Hari dalam Seminggu")

avg_by_day = filtered_df.groupby('day_name')[['casual', 'registered']].mean().reindex(
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
st.caption("Sumber data: Dataset Penyewaan Sepeda (day.csv)")
