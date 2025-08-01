# DataView Labs Email Validation Tool

A professional Streamlit-based email validation application that processes CSV files and validates email addresses using SMTP and MX record checks.

## Features

- **Professional Interface**: Clean, branded UI with DataView Labs styling
- **Comprehensive Validation**: SMTP connections and MX record verification
- **Interactive Navigation**: 5-tab system (Upload, Results, Metrics, Mood Ring, Recommendations)
- **Visual Analytics**: Pie charts, health indicators, and mood ring status
- **CSV Processing**: Upload, process, and download validation results
- **Real-time Progress**: Live validation progress with status updates

## Live Demo

[View the live app here](https://your-app-name.streamlit.app) (After deployment)

## How to Use

1. **Upload**: Select and upload your CSV file containing email addresses
2. **Results**: View detailed validation results with health status indicators
3. **Metrics**: Analyze email health with interactive charts and statistics
4. **Mood Ring**: Visual health indicator with color-coded status
5. **Recommendations**: Get actionable advice based on validation results

## Health Status Thresholds

- **Green (Excellent)**: 95%+ valid emails
- **Amber (Good)**: 70-94% valid emails  
- **Red (Poor)**: <70% valid emails

## Installation

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Files Structure

- `app.py` - Main Streamlit application
- `email_validator.py` - Email validation logic with SMTP and MX checks
- `csv_processor.py` - CSV file processing and email extraction
- `.streamlit/config.toml` - Streamlit configuration

## Tech Stack

- **Frontend**: Streamlit
- **Data Processing**: Pandas
- **Visualizations**: Plotly
- **Email Validation**: dnspython, smtplib
- **Deployment**: Streamlit Community Cloud

## License

This project is developed by DataView Labs.