from uuid import uuid5, uuid4
from uuid import NAMESPACE_DNS as ns
from faker import Faker
import pandas as pd
import random
from random import randint
from datetime import datetime, date, timedelta
import math
import os

# Initialize faker
fake = Faker()

# Define the possible values for pizza types and payment methods
pizza_types = ["Margherita", "Pepperoni", "Vodka", "Veggie", "Custom"]
pizza_toppings = [
    "Pepperoni",
    "Mushrooms",
    "Onions",
    "Sausage",
    "Bacon",
    "Extra cheese",
    "Black olives",
    "Green peppers",
    "Spinach",
]
payment_methods = ["Cash", "Credit Card", "Debit Card", "Online Payment"]

# New constants
loyalty_statuses = ["Yes", "No", "Gold Member", "Silver Member"]
discount_codes = [None, "SUMMER21", "FIRSTORDER", "FREESHIP"]
referral_sources = ["Google", "Word of Mouth", "Social Media", "Advertisement"]
allergens_map = {
    "Mozzarella": ["Dairy"],
    "Basil": [],
    "Olive oil": [],
    "Pepperoni": ["Pork"],
    "Mushrooms": [],
    "Onions": [],
    "Green peppers": [],
    "Vodka sauce": ["Dairy", "Alcohol"]
    # ... (and so on for all toppings)
}
special_requests = [None, "Extra spicy", "Crust well-done", "Low cheese"]


def get_toppings(pizza_type):
    if pizza_type == "Margherita":
        toppings = ["Mozzarella", "Basil", "Olive oil"]
    elif pizza_type == "Pepperoni":
        toppings = ["Mozzarella", "Pepperoni"]
    elif pizza_type == "Vodka":
        toppings = ["Mozzarella", "Vodka sauce"]
    elif pizza_type == "Veggie":
        toppings = ["Mozzarella", "Mushrooms", "Onions", "Green peppers"]
    else:
        toppings = []
    return toppings


def generate_multiplier(timestamp):
    order_year = (
        timestamp.year + timestamp.month / 12.0
    )  # Convert timestamp to a decimal year

    # Calculate the order volume multipliers
    start_multiplier = 1 / (1 + math.exp(-(order_year - 2021) / 0.5))
    end_multiplier = 1 - 1 / (1 + math.exp(-(order_year - 2021.5) / 0.5))

    # Determine the final multiplier (it should be between 0 and 1)
    multiplier = start_multiplier * end_multiplier

    return multiplier


def generate_timestamp():
    """Generate a timestamp with increased frequency between three years ago and two and a half years ago."""
    while True:
        # Generate a timestamp
        timestamp = fake.date_time_between(start_date="-6y", end_date="now")
        multiplier = generate_multiplier(timestamp)

        leveling_out_date = datetime(2020, 3, 1)
        leveling_out_multiplier = generate_multiplier(leveling_out_date)

        # if timestamp > leveling_out_date:
        multiplier = max(leveling_out_multiplier, multiplier)

        # Generate a random number and compare it to the multiplier. The probability
        # that the number is less than the multiplier is equal to the multiplier.
        if random.random() < multiplier:
            return timestamp


def get_price(pizza_type, pizza_size, pizza_shape):
    """Return the price of a pizza based on its type and size."""
    if pizza_size == "Small":
        base_price = 8
    elif pizza_size == "Medium":
        base_price = 10
    else:
        base_price = 12

    if pizza_type == "Margherita":
        multiplier = 0.8
    elif pizza_type == "Pepperoni":
        multiplier = 1.2
    elif pizza_type == "BBQ Chicken":
        multiplier = 1.4
    elif pizza_type == "Hawaiian":
        multiplier = 1.2
    else:
        multiplier = 1.1

    if pizza_shape == "Round":
        shape_multiplier = 1
    else:
        shape_multiplier = 1.2

    return base_price * multiplier * shape_multiplier


def generate_data(order_id, customer_id=None, timestamp=None, type=None):
    # Generate a timestamp
    if timestamp is None:
        timestamp = generate_timestamp()
    if customer_id is None:
        customer_id = str(uuid5(ns, str(fake.random_number(digits=5))))
    else:
        customer_id = str(uuid5(ns, str(customer_id)))

    # Generate a timestamp
    order_year = (
        timestamp.year + timestamp.month / 12.0
    )  # Convert timestamp to a decimal year

    # Generate payment method and delivery. We use a sigmoid function that increases
    # around the year 2020 and then levels off
    online_payment_prob = 1 / (1 + math.exp(-(order_year - 2021) / 0.5))
    delivery_prob = 1 / (1 + math.exp(-(order_year - 2021) / 0.5))
    payment_method = random.choices(
        payment_methods,
        weights=[
            1 - online_payment_prob
            if method != "Online Payment"
            else online_payment_prob
            for method in payment_methods
        ],
        k=1,
    )[0]

    # If payment method is 'Online Payment', set delivery to 'Yes'
    if payment_method == "Online Payment":
        delivery = "Yes"
    else:
        delivery = random.choices(
            ["Yes", "No"], weights=[delivery_prob, 1 - delivery_prob], k=1
        )[0]

    num_pizzas = random.choices(range(1, 4), weights=[0.7, 0.2, 0.1], k=1)[
        0
    ]  # More likely to have 1 type, less likely to have 2 or 3
    rows = []

    for _ in range(num_pizzas):
        pizza_type = random.choice(pizza_types)
        pizza_size = random.choices(
            ["Small", "Medium", "Large"], weights=[0.2, 0.6, 0.2], k=1
        )[0]
        pizza_shape = random.choices(["Round", "Square"], weights=[0.8, 0.2], k=1)[0]
        quantity = random.choices([1.0, 2.0], weights=[0.8, 0.2], k=1)[0]

        loyalty_status = random.choice(loyalty_statuses)
        discount_code = random.choice(discount_codes)
        feedback_rating = (
            randint(1, 5) if random.random() > 0.2 else None
        )  # 20% chance no feedback
        delivery_time = randint(20, 60)  # random time between 20 to 60 minutes
        preparation_time = randint(10, 30)  # random time between 10 to 30 minutes
        allergens = list(
            set(
                sum(
                    [allergens_map[topping] for topping in get_toppings(pizza_type)], []
                )
            )
        )
        special_request = random.choice(special_requests)
        referral_source = random.choice(referral_sources)
        cook_id = f"C{randint(100, 999)}"  # Random cook ID like C101, C102, ...
        location_id = f"L{randint(1, 5)}"  # Random location ID like L1, L2, ...

        rows.append(
            {
                "order_id": order_id,
                "item_number": _,
                "timestamp": timestamp,
                # generate uuid from the random number: https://stackoverflow.com/questions/41186895/how-to-generate-uuid-from-a-random-integer
                "customer_id": customer_id,
                "pizza_shape": pizza_shape,
                "pizza_size": pizza_size,
                "pizza_type": pizza_type,
                "pizza_toppings": get_toppings(pizza_type),
                "price": get_price(pizza_type, pizza_size, pizza_shape),
                "item_price": get_price(pizza_type, pizza_size, pizza_shape)
                * float(quantity),
                "quantity": quantity,
                "payment_method": payment_method,
                "delivery": delivery,
                "type": type,
                "loyalty_status": loyalty_status,
                "discount_code": discount_code,
                "feedback_rating": feedback_rating,
                "delivery_time": delivery_time,
                "preparation_time": preparation_time,
                "allergens": allergens,
                "special_request": special_request,
                "referral_source": referral_source,
                "cook_id": cook_id,
                "location_id": location_id,
            }
        )

    return rows


def generate_sub_timestamp(month, year):
    # Generate a random day of the given month
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)
    dt = fake.date_between(start_date=start_date, end_date=end_date)
    return datetime(
        dt.year, dt.month, dt.day, randint(0, 23), randint(0, 59), randint(0, 59)
    )


# Generate the data
data = []
for order_id in range(6350):
    data.extend(generate_data(order_id, type="Single Order"))

# Generate data for subscription customers
for customer_id in range(232):
    # Each customer is a subscriber for between 3 months and 2 years
    num_months = randint(3, 24)

    # Calculate start month and year
    start_month = randint(1, 12)
    start_year = randint(2020, 2024)  # Adjust as needed

    for i in range(num_months):
        # Calculate the month and year for this order
        order_month = (start_month + i - 1) % 12 + 1
        order_year = start_year + (start_month + i - 1) // 12

        for _ in range(3):  # Each customer orders 3 pizzas a month
            order_id = len(
                data
            )  # Use the current length of subscription_data as order_id
            t = generate_sub_timestamp(order_month, order_year)
            if t < datetime.now():
                data.extend(generate_data(order_id, customer_id, t, "Subscription"))

# # Create a pandas DataFrame


# Create a pandas DataFrame
df = pd.DataFrame(data)

# Save to a CSV file
# df.to_csv("fake_pizza_sales_data.csv", index=False)

# Save to parquet file
df.to_parquet("data_catalog/sales_data.parquet", index=False)
