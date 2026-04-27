import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 1. Page Configuration
st.set_page_config(page_title="Smartphone Addiction Analytics", layout="wide")

# 2. Specific CSS
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap');

    .main h1, .main h2, .main h3, .main h4, .main h5, .main h6, .main p, .main span {
        font-family: 'DM Sans', sans-serif !important;
    }

    [data-testid="stMetricValue"] {
        font-family: 'DM Sans', sans-serif !important;
        font-size: 1.8rem;
        font-weight: 700;
    }
    
    [data-testid="stMetricLabel"] {
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 500;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 3. Header Section
st.title("Smartphone Usage & Addiction Dashboard")
st.markdown("Detailed analysis of behavioral patterns and addiction metrics.")
st.markdown("---")

# 4. Data Loading
@st.cache_data
def load_data():
    df = pd.read_csv("cleanedData.csv")
    cols_to_fix = ['addiction_level', 'academic_work_impact', 'stress_level']
    for col in cols_to_fix:
        df[col] = df[col].fillna('none').astype(str)
    return df

try:
    df = load_data()

    # 5. Sidebar - Triple Filters
    st.sidebar.title("Filters")
    
    addiction_options = sorted(df["addiction_level"].unique())
    selected_addiction = st.sidebar.multiselect("Addiction Levels", options=addiction_options, default=addiction_options)

    impact_options = sorted(df["academic_work_impact"].unique())
    selected_impact = st.sidebar.multiselect("Academic/Work Impact", options=impact_options, default=impact_options)

    stress_options = sorted(df["stress_level"].unique())
    selected_stress = st.sidebar.multiselect("Stress Level", options=stress_options, default=stress_options)

    mask = (
        df["addiction_level"].isin(selected_addiction) & 
        df["academic_work_impact"].isin(selected_impact) & 
        df["stress_level"].isin(selected_stress)
    )
    filtered_df = df[mask]

    # 6. Key Metrics
    if not filtered_df.empty:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Selected Users", f"{len(filtered_df):,}")
        col2.metric("Avg Screen Time", f"{filtered_df['daily_screen_time_hours'].mean():.1f}h")
        col3.metric("Avg Notifications", int(filtered_df['notifications_per_day'].mean()))
        col4.metric("Addicted Users", len(filtered_df[filtered_df['addicted_label'] == 1]))

        st.markdown("---")

        # 7. Visualizations - Row 1
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['font.sans-serif'] = ['DM Sans']
        
        row1_col1, row1_col2 = st.columns(2)

        with row1_col1:
            st.subheader("📊 Screen Time Distribution")
            fig1, ax1 = plt.subplots(figsize=(10, 6))
            sns.histplot(filtered_df['daily_screen_time_hours'], kde=True, color="#3B82F6", ax=ax1)
            st.pyplot(fig1)

        with row1_col2:
            st.subheader("📈 Mobile Hours vs Addiction Status")
            fig2, ax2 = plt.subplots(figsize=(10, 6))
            sns.boxplot(x='addicted_label', y='daily_screen_time_hours', data=filtered_df, palette="coolwarm", ax=ax2)
            st.pyplot(fig2)

        st.markdown("---")

        # 8. Visualizations - Row 2 (New Charts)
        row2_col1, row2_col2 = st.columns(2)

        with row2_col1:
            st.subheader("🔗 Usage Correlations (Heatmap)")
            # اختيار الأعمدة الرقمية فقط للارتباط
            numeric_cols = filtered_df.select_dtypes(include=['float64', 'int64']).columns
            corr = filtered_df[numeric_cols].corr()
            fig3, ax3 = plt.subplots(figsize=(10, 8))
            sns.heatmap(corr, annot=True, cmap='RdBu_r', center=0, ax=ax3, fmt=".2f")
            st.pyplot(fig3)

        with row2_col2:
            st.subheader("😴 App Opens vs. Sleep Hours")
            fig4, ax4 = plt.subplots(figsize=(10, 8))
            sns.scatterplot(x='app_opens_per_day', y='sleep_hours', 
                            hue='addiction_level', data=filtered_df, alpha=0.7, ax=ax4)
            ax4.set_xlabel("App Opens Per Day")
            ax4.set_ylabel("Sleep Hours")
            st.pyplot(fig4)

    else:
        st.warning("No data matches the selected filters.")

except Exception as e:
    st.error(f"Error loading dashboard: {e}")