from firebase_admin import messaging
from database import subscribers_collection

def send_notification(category, title, body=None):
    if body is None:
        body = title

    subscribers = subscribers_collection.find({"categories": category})
    tokens = [s["token"] for s in subscribers]

    if not tokens:
        print(f"No subscribers for category '{category}' – skipping notification.")
        return

    BATCH_SIZE = 500
    for i in range(0, len(tokens), BATCH_SIZE):
        batch_tokens = tokens[i:i+BATCH_SIZE]

        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            tokens=batch_tokens
        )

        response = messaging.send_multicast(message)
        print(f"Sent {response.success_count}, Failed {response.failure_count}")

        for idx, resp in enumerate(response.responses):
            if not resp.success:
                failed_token = batch_tokens[idx]
                subscribers_collection.delete_one({"token": failed_token})
