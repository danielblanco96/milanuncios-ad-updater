# Milanuncios-ad-updater
Milanuncios-ad-updater is a script to automatically update your ads on [milanuncios.com](https://milanuncios.com)

## Installation
You need to have installed Python3 and the following dependencies:
- [Selenium](https://pypi.org/project/selenium/). Library to automate browsers.
- [Chrome Driver](https://chromedriver.chromium.org/). **Note**: You need the same version as your browser's.
- [Schedule](https://pypi.org/project/schedule/). Library to schedule tasks, used to update your ads every day!
- [Yagmail](https://pypi.org/project/yagmail/). Used to send emails reporting the results or errors.

## Configuration
You need to set your configuration in the config.json file:
- `updateTime`: The time of the daily updates, based on your computer time.
- `milanuncios`: Your milanuncios.com email and password.
- `notifications`: The email that is going to be used to send notifications and the list of emails that are going to receive the email notifications. **Important**: The `from` email must be a Gmail account!

```json
{
    "updateTime": "20:33",
    "milanuncios" : {
        "email" :"example@email.com",
        "password":  "example_password"
    },
    "notifications": {
        "from": {
            "email" :"example_mail@gmail.com",
            "password":  "example_password"
        },
        "to": [
            "example_mail_1@hotmail.com",
            "example_mail_2@gmail.com"
        ]
    }
}
```

## Usage
To launch the script just execute the following command:
```bash
python3 milanuncios.py &
```