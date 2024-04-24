from flask import Flask, render_template, request, redirect, url_for
from bs4 import BeautifulSoup
import requests
import smtplib
import pandas as pd
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = Flask(__name__)

# Function to extract Product Title
def get_title(soup):
    try:
        title = soup.find("span", attrs={"id": 'productTitle'})
        title_value = title.string
        title_string = title_value.strip()
    except AttributeError:
        title_string = ""
    return title_string

# Function to extract Product Price
def get_price(soup):
    try:
        price = soup.find("span", attrs={'class': 'a-price-whole'}).text
    except AttributeError:
              price = ""
    return price

# Function to extract Product Rating
def get_rating(soup):
    try:
        rating = soup.find("i", attrs={'class': 'a-icon a-icon-star a-star-4-5'}).string.strip()
    except AttributeError:
        try:
            rating = soup.find("span", attrs={'class': 'a-icon-alt'}).string.strip()
        except:
            rating = ""
    return rating

# Function to extract Number of User Reviews
def get_review_count(soup):
    try:
        review_count = soup.find("span", attrs={'id': 'acrCustomerReviewText'}).string.strip()
    except AttributeError:
        review_count = ""
    return review_count

# Function to extract Availability Status
def get_availability(soup):
    try:
        available = soup.find("div", attrs={'id': 'availability'})
        available = available.find("span").string.strip()
    except AttributeError:
        available = ""
    return available

# Function to send email
def send_email(receiver_email, product_title, product_price, product_rating, review_count, availability):
    sender_email = "psychoranger2404@gmail.com"  # Replace with your email
    sender_password = "ioxr odvo lake trgy"  # Replace with your password

    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = "Amazon Product Details"

    body = f"Product Title: {product_title}\nProduct Price: {product_price}\nProduct Rating: {product_rating}\nNumber of Reviews: {review_count}\nAvailability: {availability}"
    message.attach(MIMEText(body, 'plain'))

    session = smtplib.SMTP('smtp.gmail.com', 587)
    session.starttls()
    session.login(sender_email, sender_password)
    text = message.as_string()
    session.sendmail(sender_email, receiver_email, text)
    session.quit()

    return "Email sent successfully!"


# Function to save details to CSV
def save_details_to_csv(product_data):
    data = {
        'Product Title': [product_data['Product Title']],
        'Product Price': [product_data['Product Price']],
        'Product Rating': [product_data['Product Rating']],
        'Review Count': [product_data['Review Count']],
        'Availability': [product_data['Availability']],
        'URL': [product_data['URL']]
    }
    df = pd.DataFrame(data)
    df.to_csv('product_details.csv', mode='a', index=False, header=not os.path.exists('product_details.csv'))
    print("Product details saved to 'product_details.csv'")


@app.route('/', methods=['GET', 'POST'])
def index():
    product_data = {}
    email_status = ""
    
    if request.method == 'POST':
        url = request.form['url']
        email = request.form['email']
        
        HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
                   'Accept-Language': 'en-US, en;q=0.5'}
        
        webpage = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(webpage.content, "lxml")

        product_data['Product Title'] = get_title(soup)
        product_data['Product Price'] = get_price(soup)
        product_data['Product Rating'] = get_rating(soup)
        product_data['Review Count'] = get_review_count(soup)
        product_data['Availability'] = get_availability(soup)
        product_data['URL'] = url

        save_details_to_csv(product_data)

        email_status = send_email(email, product_data['Product Title'], product_data['Product Price'], product_data['Product Rating'], product_data['Review Count'], product_data['Availability'])
        
        return render_template('index.html', product_data=product_data, email_status=email_status)

    return render_template('index.html')

@app.route('/view-csv', methods=['GET'])
def view_csv():
    try:
        df = pd.read_csv('product_details.csv')
        csv_data = df.to_html(index=False)
        return render_template('view_csv.html', csv_data=csv_data)
    except FileNotFoundError:
        return render_template('view_csv.html', csv_data="No data available")





if __name__ == '__main__':
    app.run(debug=True)
