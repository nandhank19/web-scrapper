import os
from flask import Flask, render_template, request, jsonify, send_file
import requests
from bs4 import BeautifulSoup
import pandas as pd

app = Flask(__name__)

def scrape_website(url):
    """
    Scrapes the given URL for headlines in <h2> tags and saves the data to a CSV file.
    Returns the data as an HTML table or an error message.
    """
    try:
        headers = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/110.0.0.0 Safari/537.36'
            )
        }
        response = requests.get(url, headers=headers, timeout=10)

        # Debugging: Log response status
        print(f"Status Code: {response.status_code}")
        if response.status_code != 200:
            return f"Error: Unable to access the website (Status Code: {response.status_code})."

        soup = BeautifulSoup(response.text, 'html.parser')
        headlines = soup.find_all('h2')

        # Debugging: Check if headlines are found
        if not headlines:
            print("No <h2> tags found on the page.")
            return "No <h2> tags found on the page. Please check the URL or the HTML structure."

        # Extract and clean data
        data = {'Headline': [headline.text.strip() for headline in headlines]}
        filename = 'scraped_headlines.csv'
        df = pd.DataFrame(data)

        # Save to CSV and return data as HTML table
        df.to_csv(filename, index=False)
        print("Scraping successful. Data saved to CSV.")
        return df.to_html(classes='table table-striped')   
    except requests.exceptions.RequestException as e:
        print(f"RequestException: {e}")
        return f"Error during scraping: {e}"
    except Exception as e:
        print(f"Unexpected Exception: {e}")
        return f"An unexpected error occurred: {e}"

@app.route('/')
def index():
    """Serves the main HTML template for the web scraper."""
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    """Handles the scraping request and returns the results as JSON."""
    url = request.form['url']
    result = scrape_website(url)
    return jsonify({'data': result})

@app.route('/download')
def download():
    """Allows the user to download the scraped data as a CSV file."""
    filename = 'scraped_headlines.csv'
    if os.path.exists(filename):
        return send_file(filename, as_attachment=True)
    return "File not found. Please scrape a website first."

if __name__ == "__main__":
    app.run(debug=True)
