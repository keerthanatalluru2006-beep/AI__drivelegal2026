import psycopg2

# IMPORTANT: replace "drivelegal123" with YOUR actual postgres password
DB_PASSWORD = "drivelegal"

# Connect to our new database
conn = psycopg2.connect(
    host="localhost",
    database="drivelegal",
    user="postgres",
    password=DB_PASSWORD,
    port="5432"
)
cursor = conn.cursor()

# Create the violations table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS violations (
        id SERIAL PRIMARY KEY,
        keyword VARCHAR(100) UNIQUE NOT NULL,
        violation TEXT NOT NULL,
        fine TEXT NOT NULL,
        section TEXT NOT NULL,
        extra_penalty TEXT
    );
""")

# Our violations data (same as violations_data.py, now going into real PostgreSQL)
violations = [
    ("no helmet", "Riding without a helmet", "₹1,000", "Section 194D, Motor Vehicles Act, 1988", "License disqualification for 3 months"),
    ("no seatbelt", "Driving without seatbelt", "₹1,000", "Section 194B, Motor Vehicles Act, 1988", "None"),
    ("triple riding", "Triple riding on a two-wheeler", "₹1,000 (first offence), ₹2,000 (subsequent)", "Section 128 read with Section 194C, Motor Vehicles Act, 1988", "License disqualification possible"),
    ("red light jump", "Jumping a red light / signal violation", "₹1,000 to ₹5,000", "Section 184, Motor Vehicles Act, 1988", "License disqualification possible for repeat offences"),
    ("drunk driving", "Driving under the influence of alcohol", "₹10,000 and/or imprisonment up to 6 months (first offence)", "Section 185, Motor Vehicles Act, 1988", "Imprisonment up to 2 years for repeat offence within 3 years"),
    ("overspeeding", "Overspeeding", "₹1,000 to ₹2,000 (light motor vehicle)", "Section 183, Motor Vehicles Act, 1988", "License disqualification possible"),
    ("no license", "Driving without a valid license", "₹5,000", "Section 181, Motor Vehicles Act, 1988", "Imprisonment possible"),
    ("using phone while driving", "Using a mobile phone while driving", "₹1,000 to ₹5,000", "Section 184, Motor Vehicles Act, 1988", "License disqualification possible"),
    ("no insurance", "Driving without valid insurance", "₹2,000 (first offence), ₹4,000 (subsequent)", "Section 196, Motor Vehicles Act, 1988", "Imprisonment up to 3 months possible"),
    ("wrong side driving", "Driving on the wrong side of the road", "₹1,000 to ₹5,000", "Section 177/184, Motor Vehicles Act, 1988", "None"),
]

# Insert each violation, skip if it already exists (avoids duplicate errors on re-run)
for v in violations:
    cursor.execute("""
        INSERT INTO violations (keyword, violation, fine, section, extra_penalty)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (keyword) DO NOTHING;
    """, v)

conn.commit()
cursor.close()
conn.close()

print("Database setup complete! Table created and 10 violations inserted.")