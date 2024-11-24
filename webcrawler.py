import re
import csv
import urllib.request
from urllib.parse import urljoin
from bs4 import BeautifulSoup

# Regular expressions for extracting emails and phone numbers
email_regex = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
phone_regex = re.compile(r"\b(?:\+?\d{1,3})?[-.\s]?\(?\d{2,4}\)?[-.\s]?\d{2,4}[-.\s]?\d{4}\b")

# Function to scrape URLs from the given root webpage
def scrape_urls(root_url, max_urls=100):
    if not root_url.startswith(("https://", "http://")):
        root_url = "https://" + root_url

    try:
        # Fetch and parse the root webpage
        with urllib.request.urlopen(root_url) as response:
            html_content = response.read()
            soup = BeautifulSoup(html_content, 'html.parser')

            # Extract and limit the number of URLs to max_urls
            links = []
            for anchor in soup.find_all('a', href=True):
                full_url = urljoin(root_url, anchor['href'])
                if full_url not in links:
                    links.append(full_url)
                if len(links) >= max_urls:
                    break

        # Save the URLs to a file
        with open("urls.csv", 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows([[link] for link in links])

        print(f"Scraped {len(links)} URLs from {root_url}.")
    except Exception as e:
        print(f"Failed to scrape URLs from {root_url}: {e}")

# Function to extract emails and phone numbers from URLs
def extract_emails_and_phones():
    results = []

    try:
        # Read the URLs from the file
        with open("urls.csv", 'r', encoding='utf-8') as file:
            urls = [line.strip() for line in file]

        # Process each URL
        for url in urls:
            try:
                # Fetch the webpage content
                with urllib.request.urlopen(url) as response:
                    page_content = response.read().decode('utf-8', errors='ignore')

                    # Extract emails and phone numbers
                    emails = set(email_regex.findall(page_content))
                    phones = set(phone_regex.findall(page_content))

                    if emails or phones:
                        results.append({
                            "url": url,
                            "emails": ", ".join(emails),
                            "phones": ", ".join(phones)
                        })
            except Exception as e:
                print(f"Failed to process URL {url}: {e}")

        # Save the extracted contacts to a new file
        with open("contacts.csv", 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=["url", "emails", "phones"])
            writer.writeheader()
            writer.writerows(results)

        print(f"Extracted data from {len(results)} URLs.")
    except Exception as e:
        print(f"Error extracting data: {e}")

# Main script entry point
if __name__ == "__main__":
    root_url = input("Enter the root URL: ").strip()
    scrape_urls(root_url, max_urls=100)  
    extract_emails_and_phones()
