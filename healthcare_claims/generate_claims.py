from faker import Faker
import pandas as pd
import random
import datetime

fake = Faker("en-US")

# Sample data structures
payors = [
    "BlueShield",
    "Medicare",
    "HealthFirst",
    "WellCare",
    "Aetna",
    "Cigna",
    "UnitedHealthcare",
    "Anthem",
    "Humana",
]


def assign_payor_v2():
    prob = random.random()
    if prob < 0.4:  # 40% probability
        return "Medicare"
    elif prob < 0.6:  # 20% probability
        return "Aetna"
    elif prob < 0.7:  # 10% probability
        return "BlueShield"
    else:
        # Exclude Medicare, Aetna, and BlueShield from the list and choose randomly
        remaining_payors = [
            payor
            for payor in payors
            if payor not in ["Medicare", "Aetna", "BlueShield"]
        ]
        return random.choice(remaining_payors)


plans = ["Silver Plan", "Gold Plan", "Platinum Plan"]

cpt_codes = {
    "99211": "Office visit, minimal complexity",
    "99212": "Office visit, low complexity",
    "99213": "Office visit, moderate complexity",
    "99214": "Office visit, high complexity",
    "99215": "Office visit, very high complexity",
    "80053": "Comprehensive metabolic panel",
    "71045": "Chest X-ray",
    "90715": "Tdap vaccine > 7 years im",
}

icd_codes = {
    "E11.9": "Type 2 diabetes without complications",
    "I10": "Essential hypertension",
    "K21.9": "Gastro-esophageal reflux disease without esophagitis",
    "J06.9": "Acute upper respiratory infection, unspecified",
}

# Generating 500 unique patient names
patients = []
for _ in range(2300000):
    patient_id = fake.unique.random_number()
    first_name = fake.first_name()
    last_name = fake.last_name()
    age = random.randint(18, 90)
    address = fake.address().replace("\n", ", ")
    state = address.split(" ")[-2]

    payor = assign_payor_v2()

    patients.append([patient_id, first_name, last_name, age, address, state, payor])

# Create a DataFrame from the patient data
patient_df = pd.DataFrame(
    patients,
    columns=[
        "patient_id",
        "first_name",
        "last_name",
        "age",
        "address",
        "state",
        "payor",
    ],
)

# Save the DataFrame to a parquet file

# Generating 25 provider names
providers = ["Dr. " + fake.unique.last_name() for _ in range(25)]

# Resetting unique names generator in Faker for future use
fake.unique.clear()

# Generate synthetic claims data for a reduced dataset
claims = []
claim_details = []

# Generate data for 180 days (6 months)
HISTORY_IN_DAYS = round(365 * 3.5)
START_TREND = datetime.date.today() - datetime.timedelta(
    days=730
)  # Approximate two years in days
END_TREND = datetime.date.today() - datetime.timedelta(days=365)
PATIENT_VOLUME_INITIAL = 1200
PATIENT_VOLUME_FINAL = 11000


start_date = datetime.date.today() - datetime.timedelta(days=HISTORY_IN_DAYS)
end_date = datetime.date.today()

date_generated = start_date


def get_patient_volume_for_day(date_generated):
    days_since_trend_start = (date_generated - START_TREND).days

    if days_since_trend_start < 0:
        return PATIENT_VOLUME_INITIAL
    elif START_TREND < date_generated <= END_TREND:
        # Linearly increase the patients from 10 to 120 over a year (365 days)
        increment = (PATIENT_VOLUME_FINAL - PATIENT_VOLUME_INITIAL) / 365
        return PATIENT_VOLUME_INITIAL + increment * (days_since_trend_start)
    else:
        return PATIENT_VOLUME_FINAL


def get_claim_status(how_old_fraction):
    REJECTION_RATE = 0.055
    if age > 30:
        paid_p = 0.95 * pow(how_old_fraction, 0.1)
        # a third of claims are getting rejected, maxed out at rejection rate:
        reject_p = min((1 - paid_p) / 3, REJECTION_RATE)
        unpaid_p = 1 - reject_p - paid_p

    else:
        paid_p = 0
        reject_p = REJECTION_RATE
        unpaid_p = 1 - reject_p

    return random.choices(["Paid", "Unpaid", "Rejected"], [paid_p, unpaid_p, reject_p])[
        0
    ]


while date_generated <= end_date:
    age = (end_date - date_generated).days
    how_old_fraction = age / HISTORY_IN_DAYS

    num_patients_sampled = round(
        get_patient_volume_for_day(date_generated)
    ) + random.randint(0, 17)
    for idx, patient in patient_df.sample(n=num_patients_sampled).iterrows():
        # pow 2 makes lower numbers picked more often
        rand_provider = round(pow(random.random(), 2) * len(providers))
        rand_provider = max(min(rand_provider, len(providers) - 1), 0)
        provider = providers[rand_provider]

        claim_id = len(claims) + 1
        visit_codes = ["99211", "99212", "99213", "99214", "99215"]
        probabilities = [0.05, 0.15, 0.50, 0.25, 0.05]
        cpt_code_visit = random.choices(visit_codes, probabilities)[0]
        total_amount = random.randint(50, 150)
        allowed_amount = total_amount * 0.9
        actual_paid_amount = random.uniform(0.7, 0.9) * total_amount
        payor = patient["payor"]
        plan = random.choice(plans)

        claims.append(
            {
                "ClaimID": claim_id,
                "PatientID": patient["patient_id"],
                "ProviderID": provider,
                "DateOfService": date_generated,
                "TotalAmount": total_amount,
                "AllowedAmount": allowed_amount,
                "ActualPaidAmount": actual_paid_amount,
                "Status": get_claim_status(how_old_fraction),
                "SubmissionDate": date_generated
                - datetime.timedelta(days=random.randint(1, 5)),
                "PaymentDate": date_generated
                + datetime.timedelta(days=random.randint(1, 5)),
                "PayorName": payor,
                "PlanInformation": plan,
            }
        )

        claim_details.append(
            {
                "ClaimDetailID": len(claim_details) + 1,
                "ClaimID": claim_id,
                "PatientID": patient["patient_id"],
                "CPTCode": cpt_code_visit,
                "ICDCode": random.choice(list(icd_codes.keys())),
                "ServiceDate": date_generated,
                "Quantity": 1,
                "UnitCost": total_amount,
                "TotalCost": total_amount,
                "AllowedAmount": allowed_amount,
                "ActualPaidAmount": actual_paid_amount,
                "ServiceDescription": cpt_codes[cpt_code_visit],
            }
        )

        if random.choice([True, False]):
            cpt_code_lab = random.choice(["80053", "71045", "90715"])
            total_amount_lab = random.randint(20, 100)
            allowed_amount_lab = total_amount_lab * 0.9
            actual_paid_amount_lab = random.uniform(0.7, 0.9) * total_amount_lab

            claim_details.append(
                {
                    "ClaimDetailID": len(claim_details) + 1,
                    "ClaimID": claim_id,
                    "PatientID": patient["patient_id"],
                    "CPTCode": cpt_code_lab,
                    "ICDCode": random.choice(list(icd_codes.keys())),
                    "ServiceDate": date_generated,
                    "Quantity": 1,
                    "UnitCost": total_amount_lab,
                    "TotalCost": total_amount_lab,
                    "AllowedAmount": allowed_amount_lab,
                    "ActualPaidAmount": actual_paid_amount_lab,
                    "ServiceDescription": cpt_codes[cpt_code_lab],
                }
            )

    date_generated += datetime.timedelta(days=1)

# Convert lists to pandas DataFrame
claims_df = pd.DataFrame(claims)
claim_details_df = pd.DataFrame(claim_details)

# Write to parquet files
claims_df.to_parquet("data_catalog/claims.parquet", index=False)
claim_details_df.to_parquet("data_catalog/claim_details.parquet", index=False)
patient_df.to_parquet("data_catalog/patients.parquet", index=False)
