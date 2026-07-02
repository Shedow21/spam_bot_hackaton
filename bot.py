import telebot
import pandas as pd
import smtplib
from email.mime.text import MIMEText

# Налаштування бота
TOKEN = "token"
bot = telebot.TeleBot(TOKEN)

# Налаштування пошти
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = "email"
EMAIL_PASSWORD = "password"

def send_email(to_email, subject, body):
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = EMAIL_SENDER
    msg["To"] = to_email
    
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, to_email, msg.as_string())


def generate_email(name, age, product, country, sex):
    greetings = {
        "uk": f"Шановний {name}, " if sex == "чоловік" else f"Шановна {name}, ",
        "en": f"Dear {name}, ",
        "ro": f"Dragă {name}, "
    }

    age_warnings = {
        "uk": "Лише за згоди батьків." if int(age) < 14 else "Повний список товарів та послуг.",
        "en": "Only with parental consent." if int(age) < 14 else "Full list of products and services.",
        "ro": "Numai cu acordul părinților." if int(age) < 14 else "Lista completă de produse și servicii."
    }

    if country == "Ukraine":
        language = "uk"
    elif country in ["USA", "England"]:
        language = "en"
    elif country == "Romania":
        language = "ro"
    else:
        language = "en"

    content = {
        "food": {"uk": "пропонуємо акції на продукти.", "en": "we offer food discounts.",
                 "ro": "oferim reduceri la alimente."},
        "sport": {"uk": "продаж товарів для спорту.", "en": "we offer sports equipment.",
                  "ro": "vindem echipamente sportive."},
        "technology": {"uk": "різна побутова техніка.", "en": "various household appliances.",
                       "ro": "diferite aparate electrocasnice."},
        "game": {"uk": "акції на ігри для ПК.", "en": "discounts on PC games.", "ro": "reduceri la jocuri pentru PC."}
    }

    greeting = greetings.get(language, greetings["en"])
    age_warning = age_warnings.get(language, age_warnings["en"])
    product_info = content.get(product, {}).get(language, "")

    return f"{greeting}{product_info} {age_warning}"

@bot.message_handler(commands=['send_email'])
def process_emails(message):
    df = pd.read_excel("data.xlsx")
    for _, row in df.iterrows():
        email_body = generate_email(row['Name'], row['age'], row['product'], row['country'], row['sex'])
        if email_body:
            send_email(row['e-mail'], "Персональна пропозиція", email_body)
    bot.reply_to(message, "Розсилка завершена!")

bot.remove_webhook()
bot.polling()
