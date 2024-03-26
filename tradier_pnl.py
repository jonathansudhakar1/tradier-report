import requests
import datetime
import re
import json
import os
import argparse

from dotenv import load_dotenv 
load_dotenv()

json_file = "pnl_data.json"

def get_daily_pnl_by_symbol(account_id, token, date_str):
    """
    Gets daily gain/loss aggregated by symbol from the Tradier API. Handles option symbols.

    Args:
        account_id (str): The Tradier account ID.
        token (str): The Tradier API access token.
        date_str (str): The date in YYYY-MM-DD format.

    Returns:
        list: A list of dictionaries, each representing a symbol's aggregated PNL:
              [{"date": YYYMMDD, "symbol": "XXX", "pnl": yyy.zz}, ...]
    """

    base_url = f"https://api.tradier.com/v1/accounts/{account_id}/gainloss"
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json'
    }
    params = {
        'start': date_str,
        'end': date_str
    }

    response = requests.get(base_url, headers=headers, params=params)
    response.raise_for_status() 

    data = response.json()
    results = {}  # Use a dictionary for aggregation
    print(json.dumps(data))

    if data['gainloss'] == "null":   # Check for "null" gainloss
        return []

    for position in data['gainloss']['closed_position']:
        close_date = datetime.datetime.strptime(position['close_date'], '%Y-%m-%dT%H:%M:%S.%fZ').date()

        if close_date == datetime.datetime.strptime(date_str, '%Y-%m-%d').date():
            base_symbol = re.sub(r'\d{6}[CP]\d*', '', position['symbol'])  # Try to extract base symbol
            if base_symbol != position['symbol']:  # Check if it was an option
                symbol = base_symbol
            else:
                symbol = position['symbol']  # Keep original symbol if not an option

                
            # Aggregate in the results dictionary
            if symbol in results:
                results[symbol]['pnl'] += position['gain_loss']
            else:
                results[symbol] = {
                    "date": close_date.strftime('%Y%m%d'),
                    "symbol": symbol,
                    "pnl": position['gain_loss']
                }

    return list(results.values()) 

def overwrite_json(account_id, token, start_date, end_date):
    """Overwrites the JSON file with data from start_date to end_date."""
    data = []
    current_date = start_date
    while current_date <= end_date:
        daily_pnl = get_daily_pnl_by_symbol(account_id, token, current_date.strftime('%Y-%m-%d'))
        data.extend(daily_pnl)
        current_date += datetime.timedelta(days=1)

    with open(json_file, 'w') as outfile:
        json.dump(data, outfile, indent=4)

def update_json(account_id, token, start_date, end_date):
    """Updates the JSON file with data from start_date to end_date."""
    try:
        with open(json_file, 'r') as infile:
            existing_data = json.load(infile)
        last_date_str = existing_data[-1]['date']  # Get the last date
        last_date = datetime.datetime.strptime(last_date_str, '%Y%m%d').date()
        start_date = last_date + datetime.timedelta(days=1)  # Start from the next day
    except (FileNotFoundError, json.JSONDecodeError):  # Handle if file doesn't exist or is empty
        existing_data = []

    current_date = start_date
    while current_date <= end_date:
        daily_pnl = get_daily_pnl_by_symbol(account_id, token, current_date.strftime('%Y-%m-%d'))
        existing_data.extend(daily_pnl)
        current_date += datetime.timedelta(days=1)

    with open(json_file, 'w') as outfile:
        json.dump(existing_data, outfile, indent=4)


def main():
    # Setup argument parser
    parser = argparse.ArgumentParser(description='Tradier PNL Downloader')
    parser.add_argument('--account_id', type=str, default=os.environ.get('TRADIER_ACCOUNT_ID'), help='Your Tradier account ID')
    parser.add_argument('--token', type=str, default=os.environ.get('TRADIER_API_TOKEN'), help='Your Tradier API token')
    parser.add_argument('command', type=str, choices=['overwrite', 'update'], help='Command to execute (overwrite or update)')
    parser.add_argument('--start_date', type=str, default=datetime.date(year=2024, month=1, day=1).strftime('%Y-%m-%d'),
                        help='Start date in YYYY-MM-DD format (default: 2024-01-01)')
    parser.add_argument('--end_date', type=str, 
                        default=(datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d'),
                        help='End date in YYYY-MM-DD format (default: yesterday)')


    args = parser.parse_args()

    # Call the appropriate function based on the command
    if args.command == 'overwrite':
        overwrite_json(args.account_id, args.token, datetime.datetime.strptime(args.start_date, '%Y-%m-%d').date(), datetime.datetime.strptime(args.end_date, '%Y-%m-%d').date())
    elif args.command == 'update':
        update_json(args.account_id, args.token, datetime.datetime.strptime(args.start_date, '%Y-%m-%d').date(), datetime.datetime.strptime(args.end_date, '%Y-%m-%d').date())
    else:
        print(f"Invalid command: {args.command}")

if __name__ == '__main__':
    main()
