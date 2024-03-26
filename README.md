# Basic Tradier Daily Report

### Setup env
Update `.env` to 
TRADIER_ACCOUNT_ID=YOUR_ACCOUNT_ID
TRADIER_API_TOKEN=YOUR_API_TOKEN

### Setup cron
```
0 6 * * *  cd <PATH> && ./update_and_push.sh >> ./log.txt 2>&1 
```