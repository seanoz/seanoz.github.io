# Fantasy Football Dashboard Setup Guide

This guide will help you set up the Yahoo Fantasy Football Dashboard with automatic weekly updates.

## Overview

The dashboard consists of:
- **fantasy-football.html** - The dashboard webpage
- **fetch_fantasy_data.py** - Python script to fetch data from Yahoo API
- **fantasy-data.json** - Generated data file (created automatically)
- **GitHub Actions workflow** - Automatically updates data every Wednesday

## Prerequisites

1. A Yahoo Fantasy Football league (League ID: 598983)
2. A GitHub account with this repository
3. A Yahoo Developer account

## Step 1: Create Yahoo Developer App

1. Go to https://developer.yahoo.com/apps/create/
2. Log in with your Yahoo account
3. Fill in the application details:
   - **Application Name**: Fantasy Football Dashboard (or any name)
   - **Application Type**: Web Application
   - **Redirect URI(s)**: `oob` (out-of-band)
   - **API Permissions**: Fantasy Sports (Read)
4. Click **Create App**
5. Save your **Client ID** and **Client Secret** - you'll need these later

## Step 2: Get Refresh Token

To get a refresh token, you need to complete the OAuth flow once. Here's how:

### Method 1: Using Browser (Recommended)

1. Open the following URL in your browser (replace `YOUR_CLIENT_ID` with your actual Client ID):

```
https://api.login.yahoo.com/oauth2/request_auth?client_id=YOUR_CLIENT_ID&redirect_uri=oob&response_type=code&language=en-us
```

2. Log in and authorize the app
3. You'll be redirected to a page with an authorization code
4. Copy the authorization code

5. Use this Python script to exchange the code for a refresh token:

```python
import requests
import json

client_id = "YOUR_CLIENT_ID"
client_secret = "YOUR_CLIENT_SECRET"
auth_code = "YOUR_AUTH_CODE"

data = {
    'client_id': client_id,
    'client_secret': client_secret,
    'redirect_uri': 'oob',
    'code': auth_code,
    'grant_type': 'authorization_code'
}

response = requests.post('https://api.login.yahoo.com/oauth2/get_token', data=data)
tokens = response.json()

print("Access Token:", tokens['access_token'])
print("Refresh Token:", tokens['refresh_token'])
```

6. Save the **Refresh Token** - this is what you'll use in GitHub Secrets

### Method 2: Using cURL

```bash
# Step 1: Get authorization URL (open in browser)
echo "https://api.login.yahoo.com/oauth2/request_auth?client_id=YOUR_CLIENT_ID&redirect_uri=oob&response_type=code&language=en-us"

# Step 2: After getting the auth code, exchange it for tokens
curl -X POST https://api.login.yahoo.com/oauth2/get_token \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "redirect_uri=oob" \
  -d "code=YOUR_AUTH_CODE" \
  -d "grant_type=authorization_code"
```

## Step 3: Set Up GitHub Secrets

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** and add the following secrets:

   | Name | Value |
   |------|-------|
   | `YAHOO_CLIENT_ID` | Your Yahoo App Client ID |
   | `YAHOO_CLIENT_SECRET` | Your Yahoo App Client Secret |
   | `YAHOO_REFRESH_TOKEN` | Your refresh token from Step 2 |

## Step 4: Test the Setup

### Test Locally (Optional)

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables (replace with your values)
export YAHOO_CLIENT_ID="your_client_id"
export YAHOO_CLIENT_SECRET="your_client_secret"
export YAHOO_REFRESH_TOKEN="your_refresh_token"
export YAHOO_LEAGUE_ID="598983"

# Run the script
python fetch_fantasy_data.py
```

This should create a `fantasy-data.json` file.

### Test on GitHub

1. Go to **Actions** tab in your GitHub repository
2. Click on **Update Fantasy Football Data** workflow
3. Click **Run workflow** → **Run workflow**
4. Wait for the workflow to complete
5. Check if `fantasy-data.json` was created/updated in your repository

## Step 5: View Your Dashboard

Once the data is generated, you can view your dashboard at:

```
https://YOUR_USERNAME.github.io/fantasy-football.html
```

Or set it as your main page by renaming:
```bash
mv index.html index-old.html
mv fantasy-football.html index.html
```

## Automatic Updates

The dashboard will automatically update every Wednesday at 8 AM UTC. You can adjust this in `.github/workflows/update-fantasy-data.yml`:

```yaml
schedule:
  - cron: '0 8 * * 3'  # Minute Hour Day Month Weekday
```

For example:
- `'0 12 * * 3'` - Noon UTC on Wednesdays
- `'0 20 * * 2'` - 8 PM UTC on Tuesdays

## Customization

### Change League ID

Edit `.github/workflows/update-fantasy-data.yml`:

```yaml
env:
  YAHOO_LEAGUE_ID: 'YOUR_LEAGUE_ID'
```

### Customize Dashboard Styling

Edit `fantasy-football.html` and modify the CSS variables in the `:root` section:

```css
:root {
    --primary-blue: #0078D4;
    --dark-blue: #004578;
    --light-blue: #50A0DC;
    /* ... */
}
```

### Add More Stats

Edit `fetch_fantasy_data.py` and add your custom calculations in the processor methods.

## Troubleshooting

### "Unable to load data" Error

- Make sure the GitHub Action has run successfully
- Check that `fantasy-data.json` exists in your repository
- Verify GitHub Pages is enabled in repository settings

### GitHub Action Fails

- Check that all three secrets are set correctly
- Verify your refresh token hasn't expired (refresh tokens can expire after 1 year of inactivity)
- Check the Action logs for specific error messages

### No Data for Some Seasons

- Yahoo API might not have data for very old seasons
- Some league data might be private and not accessible via API
- Verify your league ID is correct

### Refresh Token Expired

If your refresh token expires, repeat Step 2 to get a new one and update the GitHub Secret.

## Data Privacy

- Your Yahoo credentials are stored securely as GitHub Secrets
- Only you can access these secrets
- The dashboard displays publicly on GitHub Pages, so ensure you're comfortable with the data being public
- If you want to keep it private, you can set the repository to private (note: GitHub Pages might not work with private repos on free plans)

## Support

For issues with:
- **Yahoo API**: Check https://developer.yahoo.com/fantasysports/
- **GitHub Actions**: Check the Actions tab logs in your repository
- **Dashboard Display**: Check browser console for JavaScript errors

## Next Steps

Once everything is working:
1. Customize the dashboard colors and styling
2. Add more statistics based on your league's interests
3. Consider adding charts/graphs for visual representation
4. Share the dashboard link with your league members!

Enjoy your Fantasy Football Dashboard!
