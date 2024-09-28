import pandas as pd
import numpy as np
from datetime import datetime
import schedule
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Template
import requests

# 1. Load the Dataset (with the provided path)
def load_dataset(file_path):
    df = pd.read_csv(file_path)
    df['Month'] = pd.to_datetime(df['arrival_date_month'], format='%B')  # Assuming the dataset has 'arrival_date_month' as the month column
    return df

# 2. Detect Off-Season Months and calculate percentage drop
def detect_off_season(df):
    df['Month_name'] = df['Month'].dt.strftime('%B')
    
    # Calculate the monthly average
    monthly_avg = df.groupby('Month_name')['is_canceled'].mean()  # Assuming 'is_canceled' is a relevant metric
    overall_avg = monthly_avg.mean()
    
    # Calculate percentage drop compared to overall average
    off_season_months = {}
    
    for month, avg in monthly_avg.items():
        percentage_drop = ((overall_avg - avg) / overall_avg) * 100
        
        # Define off-season as those months where the drop is more than 10%
        if percentage_drop > 10:
            off_season_months[month] = percentage_drop
    
    return off_season_months

# 3. Generate Email Content Based on Off-Season Percentage
def generate_email_content(month, percentage_drop, promotion_type):
    template = Template("""
        <h1>Special {{ promotion_type }} in {{ month }}</h1>
        <p>This month, we are offering a {{ promotion_type }} due to the performance drop of {{ percentage_drop }}%.</p>
        <p>Don't miss out!</p>
    """)
    return template.render(month=month, percentage_drop=percentage_drop, promotion_type=promotion_type)

# 4. Send Email Function
def send_email(to_address, subject, html_content):
    from_address = 'your-email@gmail.com'
    password = 'your-email-password'

    # Create message object
    msg = MIMEMultipart()
    msg['From'] = from_address
    msg['To'] = to_address
    msg['Subject'] = subject

    # Attach HTML content
    msg.attach(MIMEText(html_content, 'html'))

    # Connect to SMTP server and send email
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(from_address, password)
    text = msg.as_string()
    server.sendmail(from_address, to_address, text)
    server.quit()

# 5. Generate Blog Content
def generate_blog_content(month, percentage_drop, promotion_type):
    template = Template("""
        <h1>Special {{ promotion_type }} in {{ month }}</h1>
        <p>This month, we are offering a {{ promotion_type }} due to the performance drop of {{ percentage_drop }}%.</p>
        <p>Take advantage of this limited-time offer!</p>
    """)
    return template.render(month=month, percentage_drop=percentage_drop, promotion_type=promotion_type)

# 6. Post Blog to WordPress
def post_blog_to_wordpress(title, content):
    url = 'https://your-wordpress-site.com/wp-json/wp/v2/posts'
    user = 'your-username'
    password = 'your-application-password'  # Application Password plugin should be enabled in WordPress

    headers = {
        'Content-Type': 'application/json',
    }
    data = {
        'title': title,
        'content': content,
        'status': 'publish'  # You can use 'draft' if you don't want to publish immediately
    }

    response = requests.post(url, json=data, auth=(user, password), headers=headers)
    
    if response.status_code == 201:
        print(f"Blog post created: {response.json()['link']}")
    else:
        print(f"Failed to create post: {response.status_code}, {response.text}")

# 7. Automate Off-Season Actions
def automate_off_season_actions(off_season_months):
    for month, percentage_drop in off_season_months.items():
        if percentage_drop < 20:
            promotion_type = "light discount"
        elif 20 <= percentage_drop < 40:
            promotion_type = "large discount"
        else:
            promotion_type = "aggressive promotion"
        
        # Generate content
        email_content = generate_email_content(month, percentage_drop, promotion_type)
        blog_content = generate_blog_content(month, percentage_drop, promotion_type)

        # Automate Email and Blog
        send_email('recipient@example.com', f'Special Offer in {month}', email_content)
        post_blog_to_wordpress(f'Special Offer in {month}', blog_content)

# 8. Yearly Detection Function with Date Check
def yearly_detection():
    today = datetime.now()

    # Run the yearly function only on a specific date (e.g., January 1st)
    if today.month == 1 and today.day == 1:  # Set the date you want to trigger this yearly
        df = load_dataset(r"C:\Users\hp\Downloads\updated_hotel_booking_dataset.csv")  # Updated dataset path
        off_season_months = detect_off_season(df)
        automate_off_season_actions(off_season_months)
    else:
        print(f"Skipping: It's not the first day of the year. Current date is {today.date()}.")

# Schedule the automation to run every day and check the date
schedule.every().day.at("00:00").do(yearly_detection)  # Checks every day at midnight

# Keep the script running to listen for the scheduled event
while True:
    schedule.run_pending()
    time.sleep(60)