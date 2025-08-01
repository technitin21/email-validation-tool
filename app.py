import streamlit as st
import pandas as pd
import io
import time
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from email_validator import EmailValidator
from csv_processor import CSVProcessor

def main():
    st.set_page_config(
        page_title="Email Validation Tool",
        page_icon="📧",
        layout="wide"
    )
    
    st.title("DataView Labs Email Validation")
    
    # Initialize session state
    if 'validation_results' not in st.session_state:
        st.session_state.validation_results = None
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'current_tab' not in st.session_state:
        st.session_state.current_tab = "Upload"
    
    # Sidebar Navigation
    with st.sidebar:
        # Display company logo
        st.image("assets/dataview_logo.png", width=250)
        st.markdown("---")
        
        # About the tool section
        st.markdown(
            """
            <div style='background-color: #f0f0f0; padding: 15px; border-radius: 8px; margin: 10px 0;'>
                <h3 style='margin-top: 0; color: #333;'>About the Tool</h3>
                <h4 style='color: #555; margin-bottom: 10px;'>DataView Labs Email Validation Tool</h4>
                <p style='margin-bottom: 10px; color: #666;'>Professional email validation using SMTP and MX record verification. Upload a CSV file to get started.</p>
                <p style='margin-bottom: 0; font-weight: bold; color: #333;'>Version 1.0.0</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        st.markdown("---")
        
        # Navigation Menu
        st.markdown("### 📁 Navigation")
        
        # Define tab styling
        tab_style = """
        <style>
        .nav-tab {
            background-color: transparent;
            border: none;
            padding: 12px 20px;
            margin: 5px 0;
            border-radius: 8px;
            cursor: pointer;
            width: 100%;
            text-align: left;
            font-size: 16px;
            transition: background-color 0.3s;
        }
        .nav-tab:hover {
            background-color: #f0f0f0;
        }
        .nav-tab-active {
            background-color: #e3f2fd;
            border-left: 4px solid #1976d2;
        }
        </style>
        """
        st.markdown(tab_style, unsafe_allow_html=True)
        
        # Navigation Tabs
        if st.button("📤 Upload", key="upload_tab", use_container_width=True):
            st.session_state.current_tab = "Upload"
            st.rerun()
        
        if st.button("📊 Results", key="results_tab", use_container_width=True, 
                    disabled=st.session_state.validation_results is None):
            st.session_state.current_tab = "Results"
            st.rerun()
        
        if st.button("📈 Metrics", key="metrics_tab", use_container_width=True,
                    disabled=st.session_state.validation_results is None):
            st.session_state.current_tab = "Metrics"
            st.rerun()
        
        if st.button("🎯 Mood Ring", key="mood_tab", use_container_width=True,
                    disabled=st.session_state.validation_results is None):
            st.session_state.current_tab = "Mood Ring"
            st.rerun()
        
        if st.button("🔧 Recommendations", key="recommendations_tab", use_container_width=True,
                    disabled=st.session_state.validation_results is None):
            st.session_state.current_tab = "Recommendations"
            st.rerun()
        
        st.markdown("---")
    
    # Main Content Area based on selected tab
    if st.session_state.current_tab == "Upload":
        # File upload section
        st.header("📁 Upload CSV File")
        uploaded_file = st.file_uploader(
            "Choose a CSV file containing email addresses",
            type=['csv'],
            help="The CSV file should contain a column with email addresses"
        )
        
        if uploaded_file is not None:
            try:
                # Preview the uploaded file
                df = pd.read_csv(uploaded_file)
                st.subheader("📋 File Preview")
                st.dataframe(df.head(10), use_container_width=True)
                
                # Column selection
                email_columns = [col for col in df.columns if any(keyword in col.lower() for keyword in ['email', 'mail', 'e-mail'])]
                
                if email_columns:
                    default_column = email_columns[0]
                else:
                    default_column = df.columns[0] if len(df.columns) > 0 else None
                
                email_column = st.selectbox(
                    "Select the column containing email addresses:",
                    options=df.columns.tolist(),
                    index=df.columns.tolist().index(default_column) if default_column else 0
                )
                
                # Validation section
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    validate_button = st.button(
                        "🚀 Start Validation",
                        type="primary",
                        disabled=st.session_state.processing
                    )
                
                with col2:
                    if st.session_state.validation_results is not None:
                        clear_button = st.button("🗑️ Clear Results")
                        if clear_button:
                            st.session_state.validation_results = None
                            st.rerun()
                
                # Process validation
                if validate_button and not st.session_state.processing:
                    st.session_state.processing = True
                    
                    # Initialize processors
                    csv_processor = CSVProcessor()
                    email_validator = EmailValidator(timeout=10, max_workers=5)
                    
                    # Extract emails
                    emails = csv_processor.extract_emails(df, email_column)
                    
                    if not emails:
                        st.error("❌ No valid email addresses found in the selected column.")
                        st.session_state.processing = False
                        st.rerun()
                    
                    st.info(f"🔍 Found {len(emails)} unique email addresses to validate")
                    
                    # Create progress indicators
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    results_container = st.empty()
                    
                    # Validate emails
                    results = []
                    for i, (email, domain, status, error) in enumerate(email_validator.validate_emails_batch(emails)):
                        results.append({
                            'Email': email,
                            'Domain': domain,
                            'Status': status,
                            'Error': error if error else ''
                        })
                        
                        # Update progress
                        progress = (i + 1) / len(emails)
                        progress_bar.progress(progress)
                        status_text.text(f"Processed {i + 1}/{len(emails)} emails ({progress:.1%})")
                        
                        # Show partial results every 10 validations
                        if (i + 1) % 10 == 0 or i == len(emails) - 1:
                            with results_container.container():
                                st.subheader("🔄 Validation Progress")
                                partial_df = pd.DataFrame(results)
                                st.dataframe(partial_df, use_container_width=True)
                    
                    # Store results in session state
                    st.session_state.validation_results = pd.DataFrame(results)
                    st.session_state.processing = False
                    
                    # Clear progress indicators
                    progress_bar.empty()
                    status_text.empty()
                    results_container.empty()
                    
                    st.success("✅ Validation completed!")
                    st.rerun()
            
            except Exception as e:
                st.error(f"❌ Error processing file: {str(e)}")
                st.session_state.processing = False
    
    elif st.session_state.current_tab == "Results":
        # Results view matching reference design
        if st.session_state.validation_results is not None:
            results_df = st.session_state.validation_results
            total_emails = len(results_df)
            valid_emails = len(results_df[results_df['Status'] == 'Valid'])
            invalid_emails = len(results_df[results_df['Status'] == 'Invalid'])
            error_emails = len(results_df[results_df['Status'] == 'Error'])
            valid_percentage = (valid_emails / total_emails * 100) if total_emails > 0 else 0
            
            # Header with icon
            st.markdown("# 📊 Email Validation Results")
            
            # Health status bar with updated color thresholds
            if valid_percentage >= 95:
                status_color = "#10B981"  # Green
                status_text = "Excellent"
            elif valid_percentage >= 70:
                status_color = "#F59E0B"  # Amber
                status_text = "Good"
            else:
                status_color = "#EF4444"  # Red
                status_text = "Poor"
            
            st.markdown(
                f"""
                <div style='background: linear-gradient(135deg, {status_color}20 0%, {status_color}10 100%); 
                            border-left: 4px solid {status_color}; 
                            padding: 15px 20px; 
                            border-radius: 8px; 
                            margin: 20px 0;
                            display: flex;
                            align-items: center;
                            justify-content: center;'>
                    <div style='display: flex; align-items: center; gap: 15px;'>
                        <div style='width: 40px; height: 40px; border-radius: 50%; background-color: {status_color}; 
                                    display: flex; align-items: center; justify-content: center;'>
                            <div style='width: 16px; height: 16px; border-radius: 50%; background-color: white;'></div>
                        </div>
                        <div>
                            <h3 style='margin: 0; color: {status_color};'>Email Health: {status_text}</h3>
                            <p style='margin: 0; color: #666; font-weight: bold;'>{valid_percentage:.1f}% Valid ({total_emails} total emails)</p>
                        </div>
                    </div>
                </div>
                """, 
                unsafe_allow_html=True
            )
            
            # Validation Results section
            st.subheader("Validation Results")
            
            # Prepare display data with proper column names matching the reference
            display_df = results_df.copy()
            display_df = display_df.rename(columns={
                'Email': 'email_ids',
                'Domain': 'domain', 
                'Status': 'status',
                'Error': 'reason'
            })
            
            # Add normalized_email column (same as email_ids for now)
            display_df['normalized_email'] = display_df['email_ids']
            
            # Reorder columns to match reference exactly
            display_df = display_df[['email_ids', 'normalized_email', 'domain', 'status', 'reason']]
            
            # Color coding for status matching reference design
            def style_status(val):
                if val == 'Valid':
                    return 'background-color: #d4edda; color: #155724; font-weight: bold;'
                elif val == 'Invalid':
                    return 'background-color: #f8d7da; color: #721c24; font-weight: bold;'
                else:
                    return 'background-color: #fff3cd; color: #856404; font-weight: bold;'
            
            # Apply styling and display with index column visible
            styled_df = display_df.style.map(style_status, subset=['status'])
            st.dataframe(styled_df, use_container_width=True, height=400)
            
            # Download button at bottom left corner
            csv_buffer = io.StringIO()
            results_df.to_csv(csv_buffer, index=False)
            csv_data = csv_buffer.getvalue()
            
            col1, col2, col3 = st.columns([1, 2, 2])
            with col1:
                st.download_button(
                    label="Download Results as CSV",
                    data=csv_data,
                    file_name=f"email_validation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    type="secondary"
                )
        else:
            st.info("No validation results available.")
    
    elif st.session_state.current_tab == "Metrics":
        # Metrics view matching reference design
        if st.session_state.validation_results is not None:
            results_df = st.session_state.validation_results
            total_emails = len(results_df)
            valid_emails = len(results_df[results_df['Status'] == 'Valid'])
            invalid_emails = len(results_df[results_df['Status'] == 'Invalid'])
            error_emails = len(results_df[results_df['Status'] == 'Error'])
            valid_percentage = (valid_emails / total_emails * 100) if total_emails > 0 else 0
            
            # Header with icon
            st.markdown("# 📊 Email Validation Metrics")
            
            # Validation Metrics section
            st.subheader("Validation Metrics")
            
            # Email Health Mood Ring with updated color thresholds
            if valid_percentage >= 95:
                status_color = "#10B981"  # Green
                status_text = "Excellent"
            elif valid_percentage >= 70:
                status_color = "#F59E0B"  # Amber
                status_text = "Good"
            else:
                status_color = "#EF4444"  # Red
                status_text = "Poor"
            
            st.markdown(
                f"""
                <div style='background-color: #f8f9fa; border: 2px solid {status_color}; border-radius: 12px; padding: 30px; margin: 20px 0; text-align: center;'>
                    <div style='width: 80px; height: 80px; border-radius: 50%; border: 6px solid {status_color}; margin: 0 auto 20px auto; display: flex; align-items: center; justify-content: center; background-color: white;'>
                        <div style='width: 30px; height: 30px; border-radius: 50%; background-color: {status_color};'></div>
                    </div>
                    <h2 style='color: {status_color}; margin: 15px 0 5px 0;'>Mood Ring Status: {status_text}</h2>
                    <h3 style='color: #666; margin: 5px 0; font-weight: bold;'>{valid_percentage:.1f}% Valid ({total_emails} total emails)</h3>
                    <p style='color: #888; margin: 0; font-size: 14px;'>{'Outstanding email health! Your data is in excellent condition.' if valid_percentage >= 90 else 'Good email health. Most emails are valid.' if valid_percentage >= 70 else 'Email health needs attention. Consider cleaning your data.'}</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
            
            # Two column layout - Email Counts and Email Metrics
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Email Counts")
                # Create pie chart
                fig = go.Figure(data=[go.Pie(
                    labels=['Valid', 'Invalid', 'Error'] if error_emails > 0 else ['Valid', 'Invalid'],
                    values=[valid_emails, invalid_emails, error_emails] if error_emails > 0 else [valid_emails, invalid_emails],
                    hole=0.4,
                    marker_colors=['#10B981', '#EF4444', '#F59E0B'] if error_emails > 0 else ['#10B981', '#EF4444'],
                    textinfo='percent',
                    textfont_size=14,
                    showlegend=False
                )])
                
                fig.update_layout(
                    height=400,
                    margin=dict(t=0, b=0, l=0, r=0),
                    annotations=[dict(text='100%', x=0.5, y=0.5, font_size=20, showarrow=False)]
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("Email Metrics")
                
                # Metrics display
                st.markdown("#### Total Emails")
                st.markdown(f"**{total_emails}**")
                st.markdown("---")
                
                st.markdown("#### Valid Emails") 
                st.markdown(f"**{valid_emails}**")
                st.markdown(f"↗ {valid_percentage:.1f}%")
                st.markdown("---")
                
                st.markdown("#### Invalid Emails")
                st.markdown(f"**{invalid_emails}**")
                st.markdown(f"↗ {(invalid_emails/total_emails*100):.1f}%")
                
                if error_emails > 0:
                    st.markdown("---")
                    st.markdown("#### Error Emails")
                    st.markdown(f"**{error_emails}**")
                    st.markdown(f"↗ {(error_emails/total_emails*100):.1f}%")
            
            # Common Error Reasons section
            st.subheader("Common Error Reasons")
            
            # Check if there are any errors to display
            error_df = results_df[results_df['Status'] != 'Valid']
            if len(error_df) > 0:
                # Count error reasons
                error_reasons = error_df['Error'].value_counts()
                if len(error_reasons) > 0:
                    for reason, count in error_reasons.head(5).items():
                        if reason and reason.strip():
                            st.info(f"{reason}: {count} occurrences")
                else:
                    st.info("No specific error reasons available.")
            else:
                st.success("No invalid emails found.")
                         
        else:
            st.info("No validation results available.")
    
    elif st.session_state.current_tab == "Mood Ring":
        # Email Health Dashboard (previously dashboard view)
        if st.session_state.validation_results is not None:
            results_df = st.session_state.validation_results
            total_emails = len(results_df)
            valid_emails = len(results_df[results_df['Status'] == 'Valid'])
            invalid_emails = len(results_df[results_df['Status'] == 'Invalid'])
            error_emails = len(results_df[results_df['Status'] == 'Error'])
            
            # Calculate health status with updated color thresholds
            valid_percentage = (valid_emails / total_emails * 100) if total_emails > 0 else 0
            
            if valid_percentage >= 95:
                status_color = "#10B981"  # Green
                status_text = "Excellent"
                ring_color = "#10B981"
            elif valid_percentage >= 70:
                status_color = "#F59E0B"  # Amber
                status_text = "Good"
                ring_color = "#F59E0B"
            else:
                status_color = "#EF4444"  # Red
                status_text = "Poor"
                ring_color = "#EF4444"
            
            st.header("🎯 Email Health Mood Ring")
            
            # Health Status Card
            st.markdown(
                f"""
                <div style='background-color: #f8f9fa; border: 2px solid {status_color}; border-radius: 12px; padding: 30px; margin: 20px 0; text-align: center;'>
                    <div style='width: 80px; height: 80px; border-radius: 50%; border: 6px solid {ring_color}; margin: 0 auto 20px auto; display: flex; align-items: center; justify-content: center; background-color: white;'>
                        <div style='width: 30px; height: 30px; border-radius: 50%; background-color: {ring_color};'></div>
                    </div>
                    <h2 style='color: {status_color}; margin: 15px 0 10px 0;'>Email Health Status: {status_text}</h2>
                    <h3 style='color: #666; margin: 10px 0; font-weight: bold;'>{valid_percentage:.1f}% Valid ({total_emails} total emails)</h3>
                    <p style='color: #888; margin: 0; font-size: 14px;'>{'Outstanding email health! Your data is in excellent condition.' if valid_percentage >= 90 else 'Good email health. Most emails are valid.' if valid_percentage >= 70 else 'Email health needs attention. Consider cleaning your data.'}</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
            
            # Create two main columns for layout
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📈 Email Counts")
                # Large metrics display
                st.metric("Total Emails", total_emails, help="Total number of emails processed")
                st.metric("Valid Emails", valid_emails, f"{valid_percentage:.1f}%", help="Emails that passed validation")
                st.metric("Invalid Emails", invalid_emails, f"{(invalid_emails/total_emails*100):.1f}%", help="Emails that failed validation")
                st.metric("Error Emails", error_emails, f"{(error_emails/total_emails*100):.1f}%", help="Emails that encountered processing errors")
            
            with col2:
                st.subheader("📊 Email Metrics")
                # Visual distribution
                if valid_emails > 0:
                    st.success(f"✅ Valid Emails: {valid_emails} ({valid_percentage:.1f}%)")
                    st.progress(valid_percentage / 100)
                
                if invalid_emails > 0:
                    st.error(f"❌ Invalid Emails: {invalid_emails} ({invalid_emails/total_emails*100:.1f}%)")
                    st.progress((invalid_emails/total_emails))
                
                if error_emails > 0:
                    st.warning(f"⚠️ Error Emails: {error_emails} ({error_emails/total_emails*100:.1f}%)")
                    st.progress((error_emails/total_emails))
        else:
            st.info("No validation results available.")
    
    elif st.session_state.current_tab == "Recommendations":
        # Recommendations view
        if st.session_state.validation_results is not None:
            results_df = st.session_state.validation_results
            total_emails = len(results_df)
            valid_emails = len(results_df[results_df['Status'] == 'Valid'])
            invalid_emails = len(results_df[results_df['Status'] == 'Invalid'])
            error_emails = len(results_df[results_df['Status'] == 'Error'])
            valid_percentage = (valid_emails / total_emails * 100) if total_emails > 0 else 0
            
            st.header("🔧 Recommendations")
            
            # Generate recommendations based on updated thresholds
            if valid_percentage >= 95:
                st.success("🎉 Excellent Email Health!")
                st.write("Your email list is in outstanding condition. Here are some tips to maintain this quality:")
                st.write("• Continue regular email validation to maintain high quality")
                st.write("• Monitor engagement rates to identify potential issues early")
                st.write("• Consider implementing double opt-in for new subscribers")
                
            elif valid_percentage >= 70:
                st.warning("⚠️ Good Email Health - Room for Improvement")
                st.write("Your email list has good quality but could be improved:")
                st.write("• Remove invalid emails to improve deliverability")
                st.write("• Implement email verification at the point of collection")
                st.write("• Consider re-engagement campaigns for inactive subscribers")
                
            else:
                st.error("🚨 Poor Email Health - Immediate Action Required")
                st.write("Your email list needs significant cleaning:")
                st.write("• Remove all invalid emails immediately")
                st.write("• Investigate the source of invalid emails")
                st.write("• Implement stricter validation at email collection points")
                st.write("• Consider professional email list cleaning services")
            
            # Domain-specific recommendations
            st.subheader("Domain Analysis")
            domain_counts = results_df['Domain'].value_counts()
            
            st.write("**Top domains in your list:**")
            for domain, count in domain_counts.head(5).items():
                domain_valid = len(results_df[(results_df['Domain'] == domain) & (results_df['Status'] == 'Valid')])
                domain_rate = (domain_valid / count * 100) if count > 0 else 0
                
                if domain_rate >= 90:
                    st.success(f"✅ {domain}: {count} emails ({domain_rate:.1f}% valid)")
                elif domain_rate >= 70:
                    st.warning(f"⚠️ {domain}: {count} emails ({domain_rate:.1f}% valid)")
                else:
                    st.error(f"❌ {domain}: {count} emails ({domain_rate:.1f}% valid)")
                    
        else:
            st.info("No validation results available.")
    

    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666; font-size: 14px; margin-top: 2rem;'>"
        "© 2025 DataView Labs Pvt Ltd. | DataView Labs Email Validation"
        "</div>", 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
