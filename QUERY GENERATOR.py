import google.generativeai as genai
import streamlit as st

# Configure API key (Replace with your actual API key)
genai.configure(api_key="AIzaSyBjQ8TIAD-bJq2k16Bbqxg8oh0uzFdzX9Q")

def generate_sql_query(user_input):
    """
    Generates an SQL query based on text input using Gemini 2.0 Pro Experimental model.
    """
    prompt = f"""
    Convert the following text instruction into a valid SQL query.

    Instruction: {user_input}

    Ensure the SQL is formatted correctly for SQLite. Do NOT include markdown formatting like triple backticks.
    """
    
    # Use an available model from your list
    model = genai.GenerativeModel(model_name="gemini-2.0-pro-exp")

    # Generate response
    response = model.generate_content(prompt)
    
    # Clean the output by removing unwanted formatting
    sql_query = response.text.strip() if response and response.text else "Error generating SQL query"
    
    # Remove markdown formatting if present
    sql_query = sql_query.replace("sql", "").replace("", "").strip()

    return sql_query

# Streamlit UI
st.title("Text to query generator")
user_input = st.text_area("Enter text:")

if st.button("Generate SQL Query"):
    if user_input:
        sql_query = generate_sql_query(user_input)
        st.subheader("Generated SQL Query:")
        st.code(sql_query, language='sql')
    else:
        st.warning("Please enter an instruction.")