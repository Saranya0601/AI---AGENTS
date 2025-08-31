import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt
import requests
import io

# ------------------ Load Excel ------------------
def load_excel(file):
    try:
        df = pd.read_excel(file)
        return df
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None

# ------------------ Clean Data ------------------
def clean_data(df, drop_na=True, drop_duplicates=True, fill_na_value=None):
    if drop_na:
        df = df.dropna()
    if drop_duplicates:
        df = df.drop_duplicates()
    if fill_na_value is not None:
        df = df.fillna(fill_na_value)
    return df

# ------------------ Filter Data ------------------
def filter_data(df, column, filter_value):
    return df[df[column] == filter_value]

# ------------------ Visualize Data ------------------
def generate_visualization(df, chart_type, x_col, y_col=None):
    if df is None or df.empty:
        st.warning("No data available for visualization.")
        return
    try:
        if chart_type == "Bar Chart":
            chart = alt.Chart(df).mark_bar().encode(x=x_col, y=y_col).interactive()
        elif chart_type == "Column Chart":
            chart = alt.Chart(df).mark_bar().encode(x=x_col, y=y_col).interactive()
        elif chart_type == "Line Chart":
            chart = alt.Chart(df).mark_line().encode(x=x_col, y=y_col).interactive()
        elif chart_type == "Scatter Plot":
            chart = alt.Chart(df).mark_circle(size=60).encode(x=x_col, y=y_col).interactive()
        elif chart_type == "Histogram":
            chart = alt.Chart(df).mark_bar().encode(x=alt.X(x_col, bin=True), y='count()').interactive()
        elif chart_type == "Pie Chart":
            chart = alt.Chart(df).mark_arc().encode(theta=x_col, color=y_col)
        elif chart_type == "Waterfall Chart":
            df['cumulative'] = df[y_col].cumsum()
            chart = alt.Chart(df).mark_bar().encode(x=x_col, y='cumulative')
        else:
            st.write("Invalid visualization type.")
            return
        st.altair_chart(chart, use_container_width=True)
    except Exception as e:
        st.error(f"Error generating visualization: {e}")

# ------------------ Download Cleaned Data ------------------
def convert_df_to_excel(df):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    return buffer

# ------------------ Query Ollama LLM ------------------
def query_ollama(prompt, model="llama2"):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            headers={"Content-Type": "application/json"},
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            }
        )
        if response.status_code == 200:
            return response.json()['response']
        else:
            return f"❌ Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"❌ Failed to connect to Ollama: {e}"

# ------------------ Streamlit UI ------------------
st.set_page_config(page_title="Data Analyst Bot", layout="wide")

st.title("🔍Analyst Bot")
st.write("Upload an Excel file, clean the data, explore it visually, and ask questions to an AI model using Ollama.")

uploaded_file = st.file_uploader("📂 Upload an Excel file", type=["xlsx", "xls"])

if uploaded_file:
    df = load_excel(uploaded_file)
    
    if df is not None:
        st.write("### 📝 Original Data Preview", df.head())
        st.write("### 🧬 Data Types", df.dtypes)

        # ----------- Cleaning Options -----------
        st.subheader("🧹 Data Cleaning Options")
        col1, col2, col3 = st.columns(3)
        with col1:
            drop_na = st.checkbox("Remove missing values", value=True)
        with col2:
            drop_duplicates = st.checkbox("Remove duplicate rows", value=True)
        with col3:
            fill_na_value = st.text_input("Fill missing values with (optional):")

        if st.button("Clean Data"):
            df = clean_data(df, drop_na, drop_duplicates, fill_na_value if fill_na_value else None)
            st.success("✅ Data cleaned successfully!")
            st.write("### 📊 Cleaned Data Preview", df.head())

            # Download cleaned data
            excel_data = convert_df_to_excel(df)
            st.download_button(
                label="📥 Download Cleaned Data",
                data=excel_data,
                file_name="cleaned_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        # ----------- Visualization -----------
        if df is not None and not df.empty:
            st.subheader("📊 Generate Visualization")
            chart_type = st.selectbox("Select Chart Type", ["Bar Chart", "Column Chart", "Line Chart", "Scatter Plot", "Histogram", "Pie Chart", "Waterfall Chart"])
            x_col = st.selectbox("Select X-axis Column", df.columns)
            y_col = None if chart_type in ["Histogram", "Pie Chart"] else st.selectbox("Select Y-axis Column", df.columns)
            
            if st.button("Generate Visualization"):
                generate_visualization(df, chart_type, x_col, y_col)

        # ----------- LLM Chat -----------
        st.subheader("🧠 Ask Questions About the Data (LLM-powered by Ollama)")
        user_question = st.text_input("Ask something about the data:")

        if user_question and df is not None:
            with st.spinner("Thinking..."):
                preview = df.head(10).to_markdown(index=False)
                prompt = f"""
You are a data expert. Here is a preview of the dataset:

{preview}

Now answer this question from the user based on the dataset above:

{user_question}
"""
                response = query_ollama(prompt)
                st.success("🧠 Response:")
                st.markdown(response)