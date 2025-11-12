# LinkedIn Profile Scraper

Automates the process of logging into LinkedIn, visiting a list of public profile URLs, scraping key profile details, and storing the data in a CSV file. The project uses Selenium WebDriver, rotates user-agents, inserts human-like delays, and offers resumable scraping to minimise detection risk.

## Project Structure

```
linkedin_scraper/
├── main.py
├── scraper.py
├── config.py
├── utils.py
├── requirements.txt
├── profiles.csv        # Generated automatically after running the scraper
├── restricted_profiles.csv  # Generated when LinkedIn blocks access to a profile
└── README.md
```

## Prerequisites

- Python 3.9+
- Google Chrome installed
- Matching ChromeDriver binary (on `PATH` or provided via `CHROMEDRIVER_PATH`)
- A LinkedIn test account for scraping

## Setup Instructions

1. **Clone / copy the project**
   ```bash
   git clone <repo-url>
   cd linkedin_scraper
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Provide credentials and profile URLs**
   - Set environment variables for your LinkedIn test account:
     ```bash
     set LINKEDIN_EMAIL="test@example.com"
     set LINKEDIN_PASSWORD="SuperSecret!"
     ```
     Replace the values with your test credentials.
   - Update the list returned by `get_profile_urls()` in `config.py` with the 20 LinkedIn profile URLs you wish to scrape.

5. **(Optional) Configure extras**
   - To specify a custom ChromeDriver path:
     ```bash
     set CHROMEDRIVER_PATH="C:\path\to\chromedriver.exe"
     ```
   - To toggle resume mode:
     ```bash
     set RESUME_SCRAPE=false
     ```
   - Populate `get_proxy_list()` in `config.py` with proxies if you need rotation.
   - Tune scrape pacing & retries:
     ```bash
     set SCRAPE_DELAY_MIN=4
     set SCRAPE_DELAY_MAX=8
     set SCRAPE_RETRY_ATTEMPTS=2
     set LOGIN_WAIT_SECONDS=30
     ```
     These values control the human-like delay range (seconds), retry attempts for restricted profiles, and the login wait timeout.
   - Enable user-agent rotation only if needed:
     ```bash
     set ROTATE_USER_AGENT=true
     ```
     Rotating the user-agent between requests can trigger additional LinkedIn security checks; keep it disabled unless you have a proxy pool and understand the risk.

6. **Run the scraper**
   ```bash
   python main.py
   ```

   The script opens Chrome, logs into LinkedIn, visits each profile, and appends results to `profiles.csv`.

## Usage Notes

- **Verify profile accessibility first**: With the test account logged in, manually open every target URL. If LinkedIn shows a “Join LinkedIn” or marketing page, that profile is inaccessible and will be logged to `restricted_profiles.csv`.
- **Resume behaviour**: By default the scraper skips URLs already present in `profiles.csv`. Delete the file or set `RESUME_SCRAPE=false` if you want a completely fresh run.
- **Environment variables are per shell**: In PowerShell, use `$env:VAR="value"` for the current session. Run `setx VAR "value"` only if you want to persist the variable for future shells.
- **Pacing matters**: Increase `SCRAPE_DELAY_MIN/MAX` and add proxies before scaling to large batches. Long pauses dramatically reduce the chance of logout or rate limiting.
- **User-agent rotation is optional**: It stays disabled unless `ROTATE_USER_AGENT=true`. Rotating device fingerprints too aggressively can trigger re-logins.

## Example CSV Output

```
Full Name,Headline,Location,Current Company,Profile URL
Jane Doe,Senior Data Scientist at OpenAI,San Francisco Bay Area,OpenAI,https://www.linkedin.com/in/jane-doe/
John Smith,Product Manager,Berlin Area,GrowthHub,https://www.linkedin.com/in/john-smith/
```

## Troubleshooting

- **Login issues**: Confirm the credentials are correct and not subject to multi-factor authentication. Use a dedicated test account to avoid security prompts.
- **Blocked or throttled requests**: Increase the delay range in `scraper.py`, provide a richer proxy pool, or reduce the scrape frequency.
- **Restricted profiles**: Entries that remain inaccessible are recorded in `restricted_profiles.csv`. Verify account permissions or replace the URLs.
- **ChromeDriver mismatch**: Ensure the ChromeDriver version matches your installed Chrome browser. Use `CHROMEDRIVER_PATH` to point to the correct binary if it isn't on `PATH`.
- **Empty fields**: LinkedIn frequently updates its markup. Adjust the CSS selectors in `_scrape_profile` and `_extract_current_company` to match the latest DOM structure.

## Responsible Scraping Disclaimer

Scrape responsibly and comply with LinkedIn's terms of service and applicable laws. Always use test accounts and obtain permission before scraping data. Prolonged or aggressive scraping may lead to account restrictions or legal issues; use this project ethically and only for legitimate purposes.


