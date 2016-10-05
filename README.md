# Webhook Bot
Simple Telegram bot to accept Webhook requests. Where there is an external Webhook
request, the bot make a call (eg. send a message) to Telegram according to the config
file. This is useful when we need to make a notification service Webhook, but the
service provider can't be configured to send an appropriate Telegram API call.

## Config file

The config file is a json file, so no comments are allowed.

    {
    // Telegram bot API token.
    "apitoken": "123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghi",
    // register webhooks, object name is the mountpoint name.
    "hooks": {
        // There can be a list of hooks.
        // eg. this entry makes a /uptimerobot mountpoint
        "uptimerobot": {
            // "method" is the Telegram API method to call
            "method": "sendMessage",
            // The remaining parameters are mapped to Telegram API parameters
            "chat_id": -123456789,
            // Where the parameter is a string, the Python string formatting
            // is applied. Available variables are "q" (query string dict)
            // and "f" (form-encoded POST parameters)
            // See https://docs.python.org/3/library/string.html#formatstrings
            "text": "{q.monitorFriendlyName} {q.alertTypeFriendlyName}: {q.alertDetails}"
        }
    }
    }
