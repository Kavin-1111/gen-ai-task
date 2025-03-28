import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import pandas as pd
import time

# Configure Gemini API
genai.configure(api_key="AIzaSyBTzGZLBd13S2AfocX_lYC9Lry9BTbdAss")
model = genai.GenerativeModel("gemini-2.0-pro-exp")

# List of URLs to scrape
urls = [
    "https://lenovo.com",
    "https://www.gsk.com",
    "https://www.tcs.com",
    "https://www.ford.com",
    "https://www.siemens-energy.com",
    "https://www.theheinekencompany.com",
    "https://www.americanexpress.com"
]     
relevant_links = ["home", "about", "contact",'services','products','contact us','investors','vehicles',]

def get_relevant_links(base_url):
    response = requests.get(base_url, timeout=10)
    if response.status_code != 200:
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"].lower()
        if any(keyword in href for keyword in relevant_links):
            full_url = requests.compat.urljoin(base_url, href)
            links.append(full_url)
            print(f"Found relevant link: {full_url}")
    return list(set(links))

def scrape_text(url):
    """Scrape and clean text from a webpage."""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return ""
        
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "header", "footer", "nav"]):
            tag.extract()
        text = " ".join(soup.stripped_strings)
        return text[:]
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return ""

def extract_details(text):
    """Use Gemini API to extract structured company details."""
    prompt = f"""
    Extract the following details from the provided company webpage content:
    - Mission statement or core values
    - Products or services offered
    - Founding year and founders
    - Headquarters location
    - Key executives or leadership team
    - Notable awards or recognitions
    Content:
    {text}
    Provide concise and structured responses.
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error extracting details: {e}")
        return ""

def main():
    results = []
    for url in urls:
        print(f"Processing: {url}")
        relevant_pages = get_relevant_links(url)
        combined_text = " ".join(scrape_text(link) for link in relevant_pages)
        structured_data = extract_details(combined_text)
        results.append({"URL": url, "Extracted Details": structured_data})
        time.sleep(5)  # Prevent API rate limiting
    
    df = pd.DataFrame(results)
    df.to_csv("extracted_company_details.csv", index=False)
    print("Data saved to extracted_company_details.csv")

if __name__ =="__main__":
    main()
