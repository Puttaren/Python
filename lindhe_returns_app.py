import streamlit as st
import pandas as pd
from datetime import datetime, date
import uuid

# Initialize session state variables
if 'database' not in st.session_state:
    st.session_state.database = []
if 'registered_serials' not in st.session_state:
    st.session_state.registered_serials = []
if 'form_submitted' not in st.session_state:
    st.session_state.form_submitted = False
if 'show_final_table' not in st.session_state:
    st.session_state.show_final_table = False

# Dummy data for dropdowns (simulating database lookups)
products_db = {
    "SN001": "Product A",
    "SN002": "Product B", 
    "SN003": "Product C",
    "SN004": "Product D",
    "SN005": "Product E"
}

issue_options = ["Mechanical failure", "Software issue", "User error", "Manufacturing defect", "Normal wear"]
customer_options = ["Customer A", "Customer B", "Customer C", "Customer D", "Customer E"]
gen_options = ["Gen 1", "Gen 2", "Gen 3", "Gen 4"]
size_options = ["Small", "Medium", "Large", "X-Large"]
status_options = ["Open", "In Progress", "Closed", "Pending"]
vigilance_options = ["Low", "Medium", "High", "Critical"]
activity_levels = ["Low", "Moderate", "High", "Very High"]
sports = ["Running", "Swimming", "Cycling", "Walking", "Other"]
water_use = ["No", "Fresh water", "Salt water", "Chlorinated water"]
compensation = ["None", "Replacement", "Refund", "Credit"]
investigation_results = ["User error", "Product defect", "Normal wear", "Inconclusive"]

def reset_form():
    """Reset all form fields to default values"""
    for key in st.session_state.keys():
        if key.startswith('form_'):
            del st.session_state[key]
    st.session_state.form_submitted = False

def validate_required_fields(serial_number, issue, customer):
    """Validate that all required fields are filled"""
    return all([serial_number, issue, customer])

# Page layout
st.title("Lindhe Returns")
st.subheader("Register your returns here, and press Done to upload to the database.")

# Only show form if not showing final table
if not st.session_state.show_final_table:
    # Create two columns - main form and sidebar
    col1, col2 = st.columns([3, 1])
    
    with col2:
        st.subheader("Recent Registrations")
        if st.session_state.registered_serials:
            for serial in st.session_state.registered_serials:
                st.write(f"• {serial}")
        else:
            st.write("No registrations yet")
        
        # Stop button
        if st.button("Stop", type="secondary"):
            # Show confirmation dialog using a form
            with st.form("stop_confirmation"):
                st.write("Are you finished registering all returns?")
                col_yes, col_no = st.columns(2)
                with col_yes:
                    yes_clicked = st.form_submit_button("Yes")
                with col_no:
                    no_clicked = st.form_submit_button("No")
                
                if yes_clicked:
                    st.session_state.show_final_table = True
                    st.rerun()
                elif no_clicked:
                    st.write("Continue registering returns...")
    
    with col1:
        # Main form
        with st.form("returns_form"):
            # Date picker (defaults to today)
            selected_date = st.date_input("Date", value=date.today())
            
            # Required fields (marked with *)
            st.subheader("Required Fields *")
            
            # Serial Number (required) - auto-populates Product
            serial_number = st.selectbox("Serial Number *", 
                                       options=[""] + list(products_db.keys()),
                                       key="form_serial")
            
            # Auto-populate product based on serial number
            if serial_number:
                product = products_db.get(serial_number, "Unknown Product")
                st.text_input("Product (Auto-populated)", value=product, disabled=True)
            else:
                st.text_input("Product (Auto-populated)", value="", disabled=True)
            
            # Issue (required)
            issue = st.selectbox("Issue *", options=[""] + issue_options, key="form_issue")
            
            # Customer (required)
            customer = st.selectbox("Customer *", options=[""] + customer_options, key="form_customer")
            
            st.subheader("Optional Fields")
            
            # Optional fields
            gen3 = st.selectbox("Gen 3", options=[""] + gen_options, key="form_gen")
            size = st.selectbox("Size", options=[""] + size_options, key="form_size")
            issue_date = st.date_input("Issue Date", key="form_issue_date")
            status = st.selectbox("Status", options=[""] + status_options, key="form_status")
            vigilance = st.selectbox("Vigilance", options=[""] + vigilance_options, key="form_vigilance")
            closure_date = st.date_input("Closure Date", key="form_closure_date")
            time_on_patient = st.number_input("Time on patient (months)", min_value=0, key="form_time_patient")
            user_weight = st.number_input("User weight (kg)", min_value=0.0, step=0.1, key="form_weight")
            activity_level = st.selectbox("Patient activity level", options=[""] + activity_levels, key="form_activity")
            sport = st.selectbox("Sport", options=[""] + sports, key="form_sport")
            water_use_field = st.selectbox("Use in water", options=[""] + water_use, key="form_water")
            frequent_claim = st.checkbox("Frequent claim", key="form_frequent")
            compensation_field = st.selectbox("Compensation", options=[""] + compensation, key="form_compensation")
            comp_reason = st.text_area("Reason for comp decision", key="form_comp_reason")
            investigation = st.selectbox("Investigation result", options=[""] + investigation_results, key="form_investigation")
            comment = st.text_area("Comment", key="form_comment")
            archived_where = st.text_input("Archived where", key="form_archived")
            
            # Form submission buttons
            finished_registering = st.form_submit_button("Finished registering data")
            
            # Validate required fields when form is submitted
            if finished_registering:
                if validate_required_fields(serial_number, issue, customer):
                    st.session_state.form_submitted = True
                    st.success("✅ All required fields completed! You can now register the return.")
                else:
                    st.error("❌ Please fill in all required fields (marked with *)")
                    st.session_state.form_submitted = False
        
        # Register Return button (only active after form validation)
        if st.session_state.form_submitted:
            if st.button("Register return", type="primary"):
                # Prepare data for database
                return_data = {
                    "ID": str(uuid.uuid4())[:8],
                    "Date": selected_date,
                    "Serial Number": serial_number,
                    "Product": products_db.get(serial_number, "Unknown"),
                    "Issue": issue,
                    "Customer": customer,
                    "Gen 3": gen3 or "N/A",
                    "Size": size or "N/A",
                    "Issue Date": issue_date if 'form_issue_date' in st.session_state else "N/A",
                    "Status": status or "N/A",
                    "Vigilance": vigilance or "N/A",
                    "Closure Date": closure_date if 'form_closure_date' in st.session_state else "N/A",
                    "Time on patient (months)": time_on_patient or "N/A",
                    "User weight": user_weight or "N/A",
                    "Patient activity level": activity_level or "N/A",
                    "Sport": sport or "N/A",
                    "Use in water": water_use_field or "N/A",
                    "Frequent claim": frequent_claim,
                    "Compensation": compensation_field or "N/A",
                    "Reason for comp decision": comp_reason or "N/A",
                    "Investigation result": investigation or "N/A",
                    "Comment": comment or "N/A",
                    "Archived where": archived_where or "N/A"
                }
                
                # Add to database
                st.session_state.database.append(return_data)
                st.session_state.registered_serials.append(serial_number)
                
                st.success(f"✅ Return registered successfully! Serial: {serial_number}")
                
                # Reset form for new entry
                reset_form()
                st.rerun()
        else:
            st.button("Register return", disabled=True, help="Complete required fields first")

else:
    # Show final table with all registrations
    st.title("All Registered Returns")
    
    if st.session_state.database:
        df = pd.DataFrame(st.session_state.database)
        st.dataframe(df, use_container_width=True)
        
        # Option to download data
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name=f"returns_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.write("No returns registered yet.")
    
    # Button to start over
    if st.button("Start New Session"):
        # Clear all session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# Display current database state in sidebar (for demo purposes)
with st.sidebar:
    st.subheader("Database Status")
    st.write(f"Total registered returns: {len(st.session_state.database)}")
    
    if st.session_state.database:
        st.subheader("Database Preview")
        df_preview = pd.DataFrame(st.session_state.database)[['Serial Number', 'Product', 'Customer', 'Issue']]
        st.dataframe(df_preview, use_container_width=True)
