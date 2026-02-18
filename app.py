import streamlit as st
import pandas as pd
import numpy as np
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import io

# --- CONFIGURATION (ENTER YOUR DETAILS HERE) ---
SENDER_EMAIL = "vsrivastva_be23@thapar.edu"  # <--- Put your email here
SENDER_PASSWORD = "ezid mumq vxam xbjd"  # <--- Put your 16-char App Password here

def send_email(receiver_email, result_df):
    try:
        # Create the email structure
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = receiver_email
        msg['Subject'] = "TOPSIS Result File"

        body = "Hello,\n\nPlease find attached the result of your TOPSIS analysis.\n\nBest regards,\nTOPSIS Web Service"
        msg.attach(MIMEText(body, 'plain'))

        # Convert DataFrame to CSV in memory (no need to save to disk)
        csv_buffer = io.StringIO()
        result_df.to_csv(csv_buffer, index=False)
        csv_data = csv_buffer.getvalue()

        # Create Attachment
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(csv_data)
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="result.csv"')
        msg.attach(part)

        # Connect to Gmail SMTP Server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Secure the connection
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        text = msg.as_string()
        server.sendmail(SENDER_EMAIL, receiver_email, text)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Failed to send email: {e}")
        return False

def topsis_logic(df, weights, impacts):
    # [cite_start]This is the logic required by Assignment Part I
    dataset = df.iloc[:, 1:].values.astype(float) # Numeric columns only
    
    # 1. Vector Normalization
    rss = np.sqrt(np.sum(dataset**2, axis=0))
    normalized_data = dataset / rss

    # 2. Weighted Normalization
    weighted_data = normalized_data * weights

    # [cite_start]3. Ideal Best & Worst
    ideal_best = []
    ideal_worst = []
    for i in range(len(weights)):
        if impacts[i] == '+':
            ideal_best.append(np.max(weighted_data[:, i]))
            ideal_worst.append(np.min(weighted_data[:, i]))
        else:
            ideal_best.append(np.min(weighted_data[:, i]))
            ideal_worst.append(np.max(weighted_data[:, i]))

    # 4. Euclidean Distance & Score
    S_plus = np.sqrt(np.sum((weighted_data - ideal_best)**2, axis=1))
    S_minus = np.sqrt(np.sum((weighted_data - ideal_worst)**2, axis=1))
    score = S_minus / (S_plus + S_minus)

    df['Topsis Score'] = score
    df['Rank'] = df['Topsis Score'].rank(ascending=False).astype(int)
    return df

# --- WEB INTERFACE ---
st.title("TOPSIS Web Service")

# Inputs required by assignment
uploaded_file = st.file_uploader("Upload CSV File", type="csv")
weights_input = st.text_input("Weights (comma separated)", "1,1,1,1,1")
impacts_input = st.text_input("Impacts (comma separated)", "+,+,+,+,+")
email_input = st.text_input("Email Id")

if st.button("Submit"):
    if uploaded_file is not None and email_input:
        try:
            df = pd.read_csv(uploaded_file)
            
            # Validations 
            if df.shape[1] < 3:
                st.error("Error: Input file must contain three or more columns.")
            else:
                try:
                    weights = [float(w) for w in weights_input.split(',')]
                    impacts = impacts_input.split(',')
                except ValueError:
                    st.error("Error: Weights must be numeric.")
                    st.stop()

                # Check if number of weights/impacts matches columns
                if len(weights) != len(impacts) or len(weights) != (df.shape[1] - 1):
                    st.error(f"Error: Number of weights/impacts must match the number of criteria columns ({df.shape[1] - 1}).")
                elif not all(i in ['+', '-'] for i in impacts):
                    st.error("Error: Impacts must be '+' or '-'.")
                else:
                    # Run TOPSIS
                    result_df = topsis_logic(df, weights, impacts)
                    
                    # Send Email 
                    success = send_email(email_input, result_df)
                    
                    if success:
                        st.success(f"Success! Result sent to {email_input}")
                        st.dataframe(result_df)
                    
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please upload a file and enter an email address.")