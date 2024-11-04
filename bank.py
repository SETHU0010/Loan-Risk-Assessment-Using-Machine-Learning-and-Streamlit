import streamlit as st
import pandas as pd
import pickle
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
import io

# Load the pre-trained model
with open('loan_model.pkl', 'rb') as file:
    model = pickle.load(file)

# App Title with emoji
st.title("🏦 Loan Prediction Application")

# Function to create PDF report
def create_pdf_report(input_df, status, approval_prob, rejection_prob):
    # Create a byte stream buffer
    buffer = io.BytesIO()
    # Create a PDF document
    pdf = SimpleDocTemplate(buffer, pagesize=letter)

    # Create a list to hold the content of the PDF
    content = []

    # Add a title
    styles = getSampleStyleSheet()
    title = Paragraph("Loan Prediction Report", styles['Title'])
    content.append(title)

    # Add user input features in table format
    input_features = input_df.iloc[0].to_frame().reset_index()
    input_features.columns = ['Feature', 'Value']
    
    # Prepare the prediction results
    prediction_results = [
        ['Prediction Status', status],
        ['Probability of Approval', f"{approval_prob:.2f}"],
        ['Probability of Rejection', f"{rejection_prob:.2f}"]
    ]
    
    # Combine both tables
    report_data = [['Input Features', '']] + input_features.values.tolist() + [['', '']] + prediction_results

    # Create a table
    table = Table(report_data)

    # Add style to the table
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (0, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    content.append(table)

    # Finalize the PDF and save it to the buffer
    pdf.build(content)
    buffer.seek(0)
    return buffer

# Radio button for selecting sections with icons
selected_section = st.radio("Select Section:", ("💳 Input Features", "👤 About Developer"))

if selected_section == "💳 Input Features":
    # Main section for user input
    st.header("Input Features")

    # Function to take user input with necessary encoding for categorical variables
    def user_input_features():
        age = st.slider("👶 Age", 18, 100, 30)
        income = st.number_input("💰 Income", min_value=0, value=50000)
        loan_amount = st.number_input("💵 Loan Amount", min_value=0, value=100000)
        credit_score = st.slider("📊 Credit Score", 300, 850, 700)
        employment_years = st.slider("💼 Employment Years", 0, 40, 5)

        # Encode Marital Status
        marital_status = st.selectbox("💍 Marital Status", ["Single", "Married", "Divorced"])
        marital_status_encoded = {'Single': 0, 'Married': 1, 'Divorced': 2}[marital_status]

        dependents = st.slider("👨‍👩‍👦 Dependents", 0, 5, 0)

        # Encode Education Level
        education_level = st.selectbox("🎓 Education Level", ["High School", "Bachelor's", "Master's", "Doctorate"])
        education_level_encoded = {'High School': 0, "Bachelor's": 1, "Master's": 2, "Doctorate": 3}[education_level]

        # Encode Property Area
        property_area = st.selectbox("🏡 Property Area", ["Urban", "Semiurban", "Rural"])
        property_area_encoded = {'Urban': 0, 'Semiurban': 1, 'Rural': 2}[property_area]

        loan_term = st.number_input("📅 Loan Term (months)", min_value=0, value=360)
        coapplicant_income = st.number_input("👥 Coapplicant Income", min_value=0, value=0)

        # Create a DataFrame with all features, including encoded categorical variables
        data = {
            'Age': age,
            'Income': income,
            'LoanAmount': loan_amount,
            'CreditScore': credit_score,
            'EmploymentYears': employment_years,
            'MaritalStatus': marital_status_encoded,
            'Dependents': dependents,
            'EducationLevel': education_level_encoded,
            'PropertyArea': property_area_encoded,
            'LoanTerm': loan_term,
            'CoapplicantIncome': coapplicant_income,
        }
        features = pd.DataFrame(data, index=[0])
        return features

    # Store user input in a variable
    input_df = user_input_features()

    # Display user input
    st.write("### User Input Features")
    st.write(input_df)

    # Prediction
    if st.button("🔮 Predict"):
        try:
            # Ensure no unrealistic inputs
            if input_df['LoanAmount'].values[0] > input_df['Income'].values[0] * 5:
                st.warning("⚠️ The loan amount seems too high compared to your income.")
            else:
                prediction = model.predict(input_df)
                prediction_proba = model.predict_proba(input_df)

                # Show result
                st.write("### Prediction Result")
                if prediction[0] == 1:
                    st.write("✅ Approved")
                    status = "Approved"
                else:
                    st.write("❌ Not Approved")
                    status = "Not Approved"

                st.write("### Prediction Probability")
                approval_prob = prediction_proba[0][1]
                rejection_prob = prediction_proba[0][0]
                st.write(f"Probability of Approval: {approval_prob:.2f}")
                st.write(f"Probability of Rejection: {rejection_prob:.2f}")

                # Prepare data for PDF report
                pdf_report = create_pdf_report(input_df, status, approval_prob, rejection_prob)
                st.download_button("📥 Download Report", pdf_report, "loan_prediction_report.pdf")

        except ValueError as e:
            st.write("### Error")
            st.write(str(e))

elif selected_section == "👤 About Developer":
    st.write("---")
    st.write("### About Developer")
    st.write("**Name**: Sethumadhavan V")
    st.write("**Phone No**: 9159299878")
    st.write("**Email**: [Sethumadhavanvelu2002@gmail.com](mailto:Sethumadhavanvelu2002@gmail.com)")
