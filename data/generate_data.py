import csv
import random
from datetime import datetime, timedelta

def generate_demo_dataset():
    channels = ["App Review", "Support", "Survey", "NPS"]
    
    # Pre-redesign checkout issues (Jan 1 - Feb 14)
    pre_checkout_comments = [
        ("The checkout screen keeps spinning when I pay through UPI.", 1, "checkout", "negative"),
        ("Takes almost a full minute for the payment page to load on Android.", 2, "checkout", "negative"),
        ("Extremely slow checkout flow. I almost abandoned my cart twice today.", 1, "checkout", "negative"),
        ("Login works fine but clicking proceed to checkout freezes the app.", 2, "checkout", "negative"),
        ("Payment screen hangs forever after entering delivery address.", 1, "checkout", "negative"),
        ("App crash when trying to edit item count in checkout.", 1, "crashes", "negative"),
        ("Mobile checkout experience is laggy on iOS.", 2, "mobile", "negative"),
        ("Checkout load time is frustratingly slow during peak hours.", 2, "checkout", "negative"),
        ("Cart page hangs for 10 seconds before redirecting to payment.", 2, "checkout", "negative"),
        ("UI looks okay but checkout button unresponsive on mobile browser.", 2, "checkout", "negative"),
    ]
    
    # Post-redesign checkout praise (Feb 15 - Mar 31)
    post_checkout_comments = [
        ("The redesigned checkout is much faster on my phone.", 5, "checkout", "positive"),
        ("Checkout loading speed improved immensely after recent update!", 5, "checkout", "positive"),
        ("Smooth checkout experience today. Much better than last month.", 4, "checkout", "positive"),
        ("Love the new streamlined payment UI. Very fast.", 5, "checkout", "positive"),
        ("Quick checkout flow now, saved me lots of time.", 5, "checkout", "positive"),
        ("The checkout redesign is super smooth and intuitive.", 4, "checkout", "positive"),
        ("Super quick payment process, nice upgrade!", 5, "checkout", "positive"),
    ]

    # Payment failures (Emerging in March: Mar 1 - Mar 31)
    march_payment_failures = [
        ("UPI payment keeps failing again and again.", 1, "payments", "negative"),
        ("After the latest update, the payment succeeds but the order page doesn't refresh.", 1, "payments", "negative"),
        ("I've had two payment failures this week even though my bank approved the transaction.", 1, "payments", "negative"),
        ("Payment failed error 502 when using HDFC netbanking.", 1, "payments", "negative"),
        ("Credit card transaction timed out during payment verification step.", 2, "payments", "negative"),
        ("Double debited because payment failed screen showed retry.", 1, "payments", "negative"),
        ("GPay transaction failed twice in a row today.", 1, "payments", "negative"),
        ("Money deducted from bank but order status shows payment pending.", 1, "payments", "negative"),
        ("Failed payment gateway popup pops up randomly on final confirmation.", 2, "payments", "negative"),
    ]

    # General stable topic comments across all dates
    general_comments = [
        ("Great selection of products and fast delivery overall!", 5, "general", "positive"),
        ("App is generally decent, but search filter could use improvement.", 3, "search", "neutral"),
        ("Login authentication via OTP is smooth.", 4, "login", "positive"),
        ("Password reset link was delivered instantly.", 5, "login", "positive"),
        ("App notification settings are easy to customize.", 4, "notifications", "positive"),
        ("Customer support team resolved my query quickly.", 5, "general", "positive"),
        ("Pricing is reasonable compared to competitors.", 4, "pricing", "positive"),
        ("Search results take a few seconds to filter items.", 3, "search", "neutral"),
        ("App crashed once while scrolling product images.", 2, "crashes", "negative"),
        ("Clean visual design and easy navigation.", 5, "general", "positive"),
        ("Wish there were more payment options like Apple Pay.", 3, "payments", "neutral"),
        ("Notifications are a bit too frequent during sales.", 3, "notifications", "neutral"),
    ]

    rows = []
    current_date = datetime(2026, 1, 1)
    end_date = datetime(2026, 3, 31)
    row_id = 1000

    random.seed(42)

    while current_date <= end_date:
        # Determine day's weight/mix based on date
        is_pre_feb15 = current_date < datetime(2026, 2, 15)
        is_march = current_date >= datetime(2026, 3, 1)

        daily_count = random.randint(5, 8)
        for _ in range(daily_count):
            row_id += 1
            cust_id = f"CUST-{random.randint(10000, 99999)}"
            channel = random.choice(channels)
            
            # Select comment pool
            r = random.random()
            if is_pre_feb15:
                if r < 0.45:
                    item = random.choice(pre_checkout_comments)
                else:
                    item = random.choice(general_comments)
            elif is_march:
                if r < 0.40:
                    item = random.choice(march_payment_failures)
                elif r < 0.65:
                    item = random.choice(post_checkout_comments)
                else:
                    item = random.choice(general_comments)
            else: # Feb 15 to Feb 28
                if r < 0.35:
                    item = random.choice(post_checkout_comments)
                elif r < 0.50:
                    item = random.choice(pre_checkout_comments)
                else:
                    item = random.choice(general_comments)

            text, rating, topic, sentiment = item
            date_str = current_date.strftime("%Y-%m-%d %H:%M:%S")
            rows.append({
                "feedback_id": f"FB-{row_id}",
                "created_at": date_str,
                "channel": channel,
                "customer_id": cust_id,
                "review_text": text,
                "rating": rating
            })

        current_date += timedelta(days=1)

    return rows

if __name__ == "__main__":
    data = generate_demo_dataset()
    with open("c:/Users/Sowmya Mounika/OneDrive/Desktop/New folder/echolens/data/demo_feedback.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["feedback_id", "created_at", "channel", "customer_id", "review_text", "rating"])
        writer.writeheader()
        writer.writerows(data)
    print(f"Generated {len(data)} demo feedback records.")
