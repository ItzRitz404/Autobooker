# Autobooker

Autobooker is a Python automation bot for booking activities on the Better booking website.

The bot logs into your Better account, checks your booking configuration, opens the correct booking page, adds the slot to the basket, goes to checkout, applies credit if available, accepts the terms, and confirms the booking.

The main file used to run the bot is:

```bash
python schedulerold.py
```

## Features

- Automatically logs into a Better account
- Uses booking details from `config.json`
- Schedules bookings based on day and activation time
- Opens booking pages using Playwright
- Adds activities to the basket
- Goes to checkout
- Applies credit when available
- Accepts the terms and confirms the booking

## Project Structure

```text
Autobooker/
├── add_basket.py
├── book.py
├── booking_attempt.py
├── main.py
├── requirements.txt
├── scheduler.py
├── schedulerold.py
├── test_run.py
├── .env              # not committed
├── config.json       # not committed
└── .venv/            # not committed
```

## Requirements

Make sure Python is installed on your computer.

Python 3.10 or newer is recommended.

This project uses:

- `apscheduler`
- `playwright`
- `python-dotenv`
- `pytz`
- `selenium`

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/ItzRitz404/Autobooker.git
cd Autobooker
```

### 2. Create a Python virtual environment

#### Windows

```bash
python -m venv .venv
```

Activate it:

```bash
source .venv\Scripts\activate
```

#### macOS / Linux

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

When the virtual environment is active, you should see `(.venv)` at the start of your terminal line.

### 3. Upgrade pip

```bash
python -m pip install --upgrade pip
```

### 4. Install the Python packages

```bash
pip install -r requirements.txt
```

If that command gives an error, make sure `requirements.txt` has each package on a separate line like this:

```txt
apscheduler==3.11.2
playwright==1.58.0
python-dotenv==1.2.2
pytz==2026.1.post1
selenium==4.42.0
```

Then run the install command again:

```bash
pip install -r requirements.txt
```

### 5. Install Playwright browsers

After installing the Python packages, install the Playwright browser files:

```bash
playwright install
```

## Environment Variables

Create a file called `.env` in the project root.

Example:

```env
EMAIL=your_better_email@example.com
PASSWORD=your_better_password
```

These details are used to log into your Better account.

Do not commit your `.env` file.

## Configuration

Create a file called `config.json` in the project root.

Example:

```json
[
  {
    "id": "booking-1",
    "name": "Badminton Court",
    "enabled": true,
    "activation_day": "monday",
    "activation_time": "21:55:00",
    "location": "your-location-slug",
    "activity": "your-activity-slug",
    "day": "tuesday",
    "time": "20:00-21:00",
    "court_number": "1"
  }
]
```

## Config Fields

| Field | Description |
|---|---|
| `id` | A unique ID for the booking |
| `name` | A readable name for the booking |
| `enabled` | Set to `true` to enable this booking |
| `activation_day` | The day the bot should trigger, for example `monday` |
| `activation_time` | The time the bot should activate, in `HH:MM:SS` format |
| `location` | The Better location slug used in the booking URL |
| `activity` | The Better activity slug used in the booking URL |
| `day` | The day you want to book |
| `time` | The booking time slot |
| `court_number` | The court number or slot number |

## Running the Bot

Make sure your virtual environment is activated first.

Then run:

```bash
python schedulerold.py
```

The bot will keep running and checking `config.json`.

When a booking matches the current day and activation time, the bot will start the booking process.

## How It Works

1. `schedulerold.py` loads booking jobs from `config.json`.
2. It checks the current day and time.
3. If a booking is enabled and matches the current day, it waits for the activation time.
4. When the booking is ready, it calls the `AutoBooker` class from `main.py`.
5. The bot opens a browser using Playwright.
6. It logs into the Better website using your `.env` details.
7. It clears the basket.
8. It opens the correct booking page.
9. It adds the selected slot to the basket.
10. It goes to checkout.
11. It applies credit if available.
12. It accepts the terms.
13. It confirms the booking.

## Headless Mode

By default, the browser is visible because `headless` is set to `False`.

In `schedulerold.py`, you should see something like this:

```python
asyncio.run(schedule_bookings(auto_booker, login_lead=5, headless=False, update_interval=2))
```

To run the browser in the background, change it to:

```python
asyncio.run(schedule_bookings(auto_booker, login_lead=5, headless=True, update_interval=2))
```

## Important Notes

- Keep `.env` private.
- Keep `config.json` private.
- Do not commit `.venv`.
- Make sure your Better account email and password are correct.
- Keep the terminal open while the bot is running.
- Booking success depends on slot availability.
- The bot may stop working if the Better website changes its layout or button names.

## Troubleshooting

### `ModuleNotFoundError`

Make sure your virtual environment is activated:

```bash
.venv\Scripts\activate
```

On macOS / Linux:

```bash
source .venv/bin/activate
```

Then reinstall the packages:

```bash
pip install -r requirements.txt
```

### Playwright browser error

Run:

```bash
playwright install
```

### Login fails

Check that your `.env` file exists and contains the correct details:

```env
EMAIL=your_better_email@example.com
PASSWORD=your_better_password
```

### `config.json` not found

Create `config.json` in the project root folder, next to `schedulerold.py`.

### Bot does not trigger

Check that:

- `enabled` is set to `true`
- `activation_day` matches the current day
- `activation_time` uses `HH:MM:SS` format
- your computer time is correct
- the bot is still running in the terminal

## Disclaimer

This project is for personal automation. Use it responsibly and make sure it follows the rules and terms of the website you are using.
