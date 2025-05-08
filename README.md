# **UniFi Network Server Linux Downloader Scraper**

This Scrapy project scrapes the Ubiquiti downloads page ([ui.com/download](https://ui.com/download)) to find the direct download URL for the latest version of the UniFi Network Server (or UniFi Network Application) for Linux (Debian/Ubuntu .deb package).

It uses Scrapy with scrapy-playwright to handle JavaScript-rendered content on the target website.

## **Prerequisites**

### **1\. System-Level Dependencies**

This project requires certain system libraries to be installed for Playwright and its browsers to function correctly. On Debian/Ubuntu-based systems, install them using:

sudo apt-get update  
sudo apt-get install \-y libicu-dev libevent-dev libavif-dev libjpeg-dev \\  
    libpng-dev libwebp-dev libfontconfig1 libdbus-glib-1-2 libxtst6 \\  
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libgbm1 \\  
    libasound2

(Note: The list above includes libraries confirmed to work for similar setups plus a few other common ones that Playwright often needs for full browser functionality. libxtst6, libnss3, libatk1.0-0, libatk-bridge2.0-0, libcups2, libdrm2, libgbm1, libasound2 are often part of playwright install-deps output or common requirements for headless browsers on Linux.)

### **2\. Python**

* Python 3.8+ is recommended.  
* pip (Python package installer).  
* pipx (if you choose to manage Scrapy and Playwright CLI via pipx).

### **3\. Playwright Browsers**

After installing the Python package playwright (which scrapy-playwright depends on), you need to install the browser binaries. This project is configured to use chromium.

To install Chromium for Playwright:

\# If the playwright CLI is in your PATH  
\# (e.g., from \`pipx install playwright\` or a global pip install of playwright)  
playwright install chromium

Or, if you installed playwright into a specific Python environment (like the one pipx uses for scrapy, or a local project venv), you might need to run it as a module from that environment's Python:

\# Example for a pipx-managed scrapy environment:  
/home/your\_user/.local/share/pipx/venvs/scrapy/bin/python \-m playwright install chromium

\# Example for a local venv:  
venv/bin/python \-m playwright install chromium

(Replace /home/your\_user/ with your actual home directory if using the pipx example)

## **Setup**

Clone the repository (if you put this project on GitHub):

git clone \<your-repository-url\>  
cd \<your-repository-name\>

(If you're just working locally, ensure all project files are in a directory, e.g., unifi\_project)

Install Scrapy:  
You need Scrapy installed on your system.  
Using pipx (recommended for managing CLI tools like Scrapy): If you don't have pipx, install it first (see pipx documentation: [https://pypa.github.io/pipx/](https://pypa.github.io/pipx/)). Then install Scrapy:

pipx install scrapy

Using pip in a dedicated project virtual environment (see step 3): If you plan to use a local virtual environment for the project, Scrapy will be installed as part of pip install \-r requirements.txt.

Python Environment & Project Dependencies:

Recommended: Using a local project virtual environment (venv)  
This keeps project dependencies isolated.  
\# Navigate to your project's root directory (e.g., unifi\_project)  
python3 \-m venv venv  
source venv/bin/activate  \# On Linux/macOS  
\# For Windows: venv\\Scripts\\activate  
\`\`\`bash  
\# Install Python packages (including Scrapy and scrapy-playwright)  
pip install \-r requirements.txt

You will need to create a requirements.txt file (see step 4).

Alternative: Using pipx for Scrapy (if you installed Scrapy with pipx in step 2\)  
If Scrapy is managed by pipx, inject scrapy-playwright into Scrapy's environment:  
pipx inject scrapy scrapy-playwright

You'll also need the playwright CLI for installing browsers (e.g., via pipx install playwright or it might be available if scrapy-playwright pulled it into the pipx env).

Create requirements.txt (Essential for local venv setup):  
In your project's root directory (e.g., unifi\_project), create a file named requirements.txt with the following content:  
scrapy\>=2.11.0  \# Or your desired Scrapy version  
scrapy-playwright\>=0.0.30  
\# Add other specific versions or packages if your project evolves

## **Running the Scraper**

Navigate to the project's root directory (e.g., unifi\_project) in your terminal.

If using a local virtual environment (venv), make sure it's activated (source venv/bin/activate).

Run the Scrapy spider:

scrapy crawl unifi\_server

The scraper will output the found download information to the console, including:

* Software Name  
* Platform  
* Version (extracted from the URL by the pipeline)  
* Download URL

## **Project Structure**

unifi\_project/  
├── scrapy.cfg          \# Scrapy deploy configuration file  
├── README.md           \# This file: setup and usage instructions  
├── requirements.txt    \# Python package dependencies (for venv setup)  
└── unifi\_scraper/      \# Project's Python module  
    ├── \_\_init\_\_.py  
    ├── items.py        \# Scraped item definitions  
    ├── middlewares.py  \# Custom middlewares (if any \- currently default)  
    ├── pipelines.py    \# Item processing pipelines  
    ├── settings.py     \# Scrapy project settings  
    └── spiders/        \# Directory for spiders  
        ├── \_\_init\_\_.py  
        └── unifi\_server\_spider.py  \# The spider code

## **Notes**

* The ROBOTSTXT\_OBEY setting in unifi\_scraper/settings.py is set to False. While it's generally good practice to obey robots.txt, dynamic sites handled by Playwright sometimes require this to be False to access all necessary resources for rendering. Always ensure your scraping activity is ethical and respects the website's terms of service.  
* Website structures change. The XPath selectors in unifi\_server\_spider.py might need adjustments if Ubiquiti updates its download page layout in the future.  
* The PLAYWRIGHT\_LAUNCH\_OPTIONS in settings.py has headless: True. For debugging, you can temporarily set this to headless: False to see the browser window Playwright controls.
