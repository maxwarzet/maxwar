from telegram import Bot
from telegram.constants import ParseMode
from PIL import Image, ImageDraw, ImageFont
import asyncio
import requests

# Replace with your Telegram bot token and channel username
TELEGRAM_BOT_TOKEN = "7481793222:AAHzLRvIHvq0ZvuJ1xRBIO72lE-12WelBGY"
CHANNEL_USERNAME = "@mwtg_admin"

# Replace with your ExchangeRate-API key
EXCHANGE_RATE_API_KEY = "19ee6ab5c292866accce3156"

# Function to fetch currency exchange rates
def fetch_currency_rates():
    url = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_RATE_API_KEY}/latest/USD"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        rates = data.get("conversion_rates", {})
        return rates
    else:
        print("Failed to fetch currency rates.")
        return {}

# Function to generate an image with currency rates (without emojis)
def generate_currency_image(rates):
    # Create a blank image with white background
    img = Image.new('RGB', (400, 200), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Load a regular font for text
    try:
        text_font = ImageFont.truetype("arial.ttf", 16)  # Use a regular font for text
    except:
        text_font = ImageFont.load_default()  # Fallback to default font

    # Add header text
    header = "Valyuta kurslari (1 USD, 1 RUB, 1 EUR → UZS)"
    draw.text((10, 10), header, font=text_font, fill=(0, 0, 0))

    # Add currency rates to the image
    y_offset = 50
    currencies = ["USD", "RUB", "EUR"]  # Add more currencies if needed
    for currency in currencies:
        if currency in rates:
            uzs_rate = rates["UZS"] / rates[currency]  # Convert to UZS
            text = f"1 {currency} = {uzs_rate:.2f} UZS"
            
            # Draw the text
            draw.text((10, y_offset), text, font=text_font, fill=(0, 0, 0))
            y_offset += 30

    # Save the image
    img.save("currency_rates.png")

# Function to format currency rates as text (with emojis)
def format_currency_text(rates):
    currencies = ["USD", "RUB", "EUR"]  # Add more currencies if needed
    text = "💱 *Valyuta kurslari*\n\n"
    for currency in currencies:
        if currency in rates:
            uzs_rate = rates["UZS"] / rates[currency]  # Convert to UZS
            flag_emoji = "🇺🇸" if currency == "USD" else "🇷🇺" if currency == "RUB" else "🇪🇺"
            text += f"{flag_emoji} 1 {currency} = {uzs_rate:.2f} UZS\n"
    return text

# Function to send the image and text to the Telegram channel
async def send_currency_update_to_channel():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)

    # Fetch currency rates
    rates = fetch_currency_rates()
    if not rates:
        print("No rates fetched. Skipping this iteration.")
        return

    # Generate the image with currency rates
    generate_currency_image(rates)

    # Format the text message
    text_message = format_currency_text(rates)

    # Send the image with the text as a caption
    with open("currency_rates.png", "rb") as img:
        await bot.send_photo(
            chat_id=CHANNEL_USERNAME,
            photo=img,
            caption=text_message,
            parse_mode=ParseMode.MARKDOWN,
        )

# Run the bot in a loop every 60 seconds
async def main():
    while True:
        await send_currency_update_to_channel()
        await asyncio.sleep(3600)  # Wait for 10 seconds before sending the next update

if __name__ == "__main__":
    asyncio.run(main())