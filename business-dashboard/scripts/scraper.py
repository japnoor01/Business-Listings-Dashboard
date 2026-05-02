"""
Business Listings Data Generator
Simulates scraping from multiple sources: Justdial, Sulekha, IndiaMart, Google Maps
Generates 500+ realistic Indian business listings
"""

import json
import random
from datetime import datetime, timedelta

# Realistic Indian business data
CITIES = [
    "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai",
    "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Surat",
    "Lucknow", "Kanpur", "Nagpur", "Indore", "Bhopal",
    "Visakhapatnam", "Patna", "Vadodara", "Ludhiana", "Agra"
]

CATEGORIES = [
    "Restaurant", "Hospital", "Salon & Spa", "Gym & Fitness",
    "Hotel", "Electronics", "Clothing & Fashion", "Grocery",
    "Pharmacy", "Real Estate", "Education & Coaching",
    "Automobile", "IT Services", "Legal Services", "Banking & Finance",
    "Construction", "Travel & Tours", "Event Management", "Jewellery",
    "Home Decor"
]

SOURCES = ["Justdial", "Sulekha", "IndiaMart", "Google Maps", "TradeIndia"]

BUSINESS_PREFIXES = {
    "Restaurant": ["Spice", "Royal", "Golden", "Maharaja", "Saffron", "Heritage", "Paradise", "Curry", "Masala", "Nawab"],
    "Hospital": ["City", "Apollo", "Sunrise", "Grace", "Metro", "National", "Star", "Care", "Life", "Prime"],
    "Salon & Spa": ["Glam", "Luxe", "Studio", "Looks", "Beauty", "Chic", "Glow", "Radiant", "Elite", "Zen"],
    "Gym & Fitness": ["Power", "Iron", "Peak", "Flex", "Pro", "Max", "Strong", "Ultra", "Alpha", "Body"],
    "Hotel": ["Grand", "Royal", "Park", "City", "Crown", "Palace", "Comfort", "Stay", "Executive", "Premier"],
    "Electronics": ["Tech", "Digital", "Smart", "Volt", "Circuit", "Pixel", "Giga", "Mega", "Power", "Nova"],
    "Clothing & Fashion": ["Style", "Trend", "Vogue", "Fab", "Chic", "Mode", "Dapper", "Ethnic", "Urban", "Classic"],
    "Grocery": ["Fresh", "Daily", "Super", "Mega", "Family", "Choice", "Select", "Prime", "Nature", "Green"],
    "Pharmacy": ["Health", "Care", "Life", "Med", "Cure", "Heal", "Plus", "Well", "Safe", "Sure"],
    "Real Estate": ["Prime", "Elite", "Global", "Empire", "Crown", "Horizon", "Landmark", "Century", "Vision", "Dream"],
    "Education & Coaching": ["Excel", "Bright", "Success", "Pioneer", "Mentor", "Apex", "Scholar", "Wisdom", "Future", "Ace"],
    "Automobile": ["Speed", "Auto", "Motor", "Drive", "Torque", "Gear", "Turbo", "Classic", "Modern", "Swift"],
    "IT Services": ["Tech", "Soft", "Cyber", "Digital", "Code", "Cloud", "Data", "Net", "Sys", "Info"],
    "Legal Services": ["Justice", "Law", "Legal", "Advocate", "Rights", "Shield", "Counsel", "Lexis", "Charter", "Lex"],
    "Banking & Finance": ["Capital", "Trust", "Wealth", "Invest", "Finance", "Money", "Asset", "Growth", "Profit", "Fund"],
    "Construction": ["Build", "Infra", "Structure", "Construct", "Create", "Design", "Plan", "Arch", "Metro", "Urban"],
    "Travel & Tours": ["Globe", "Voyage", "Journey", "Explore", "Dream", "Trek", "Tour", "Travel", "Holiday", "Wander"],
    "Event Management": ["Celebrate", "Grand", "Event", "Occasions", "Festive", "Premier", "Elite", "Dream", "Magic", "Star"],
    "Jewellery": ["Gold", "Diamond", "Gem", "Sparkle", "Glitter", "Royal", "Heritage", "Classic", "Precious", "Shine"],
    "Home Decor": ["Interior", "Decor", "Home", "Style", "Living", "Design", "Cozy", "Elegant", "Modern", "Classic"]
}

BUSINESS_SUFFIXES = {
    "Restaurant": ["Kitchen", "Dhaba", "Bistro", "Cafe", "Eatery", "Diner", "Grill", "House", "Corner", "Palace"],
    "Hospital": ["Hospital", "Clinic", "Medical Centre", "Healthcare", "Nursing Home", "Medical", "Diagnostics", "Care Centre"],
    "Salon & Spa": ["Salon", "Spa", "Beauty Parlour", "Unisex Salon", "Hair Studio", "Beauty Studio"],
    "Gym & Fitness": ["Gym", "Fitness Centre", "Health Club", "Fitness Studio", "Sports Club", "Workout Zone"],
    "Hotel": ["Hotel", "Inn", "Residency", "Suites", "Lodge", "Guest House", "Resort", "Retreat"],
    "Electronics": ["Electronics", "Gadgets", "Appliances", "Store", "World", "Hub", "Zone", "Point"],
    "Clothing & Fashion": ["Boutique", "Fashion House", "Garments", "Clothing", "Wear", "Store", "Collections"],
    "Grocery": ["Mart", "Store", "Market", "Bazaar", "Shop", "Superstore", "Kirana", "Provisions"],
    "Pharmacy": ["Pharmacy", "Medical Store", "Chemist", "Drug Store", "Medicals", "Health Store"],
    "Real Estate": ["Properties", "Realty", "Builders", "Developers", "Infrastructure", "Housing", "Estates"],
    "Education & Coaching": ["Academy", "Institute", "Classes", "Coaching", "School", "Centre", "Tutorials"],
    "Automobile": ["Motors", "Automobiles", "Service Centre", "Auto Works", "Garage", "Workshop"],
    "IT Services": ["Technologies", "Solutions", "Systems", "Infotech", "Software", "Consulting", "Services"],
    "Legal Services": ["Associates", "Law Firm", "Advocates", "Legal Services", "Consultants", "Partners"],
    "Banking & Finance": ["Financial Services", "Investments", "Finance", "Consultants", "Advisors", "Solutions"],
    "Construction": ["Builders", "Construction", "Contractors", "Engineers", "Infrastructure", "Projects"],
    "Travel & Tours": ["Travels", "Tours", "Holidays", "Vacations", "Adventures", "Expeditions"],
    "Event Management": ["Events", "Celebrations", "Occasions", "Management", "Planners", "Organizers"],
    "Jewellery": ["Jewellers", "Jewellery", "Ornaments", "Gems", "Diamonds", "Jewels"],
    "Home Decor": ["Interiors", "Furnishings", "Decor", "Design Studio", "Furniture", "Living"]
}

STREET_TYPES = ["Road", "Street", "Avenue", "Nagar", "Colony", "Marg", "Lane", "Chowk", "Bazaar", "Market", "Plaza", "Complex"]
AREAS = {
    "Mumbai": ["Andheri", "Bandra", "Borivali", "Dadar", "Kurla", "Malad", "Thane", "Worli", "Powai", "Juhu"],
    "Delhi": ["Connaught Place", "Karol Bagh", "Lajpat Nagar", "Saket", "Dwarka", "Rohini", "Janakpuri", "Nehru Place"],
    "Bangalore": ["Koramangala", "Indiranagar", "Whitefield", "HSR Layout", "Marathahalli", "JP Nagar", "Yelahanka"],
    "Hyderabad": ["Banjara Hills", "Jubilee Hills", "Hitech City", "Madhapur", "Gachibowli", "Secunderabad", "Ameerpet"],
    "Chennai": ["Anna Nagar", "T. Nagar", "Adyar", "Velachery", "OMR", "Chromepet", "Perambur", "Nungambakkam"],
    "Kolkata": ["Park Street", "Salt Lake", "New Town", "Ballygunge", "Howrah", "Dum Dum", "Gariahat"],
    "Pune": ["Koregaon Park", "Baner", "Kothrud", "Hadapsar", "Hinjewadi", "Wakad", "Viman Nagar"],
    "Ahmedabad": ["Navrangpura", "CG Road", "Maninagar", "Vastrapur", "Bopal", "SG Highway", "Satellite"],
    "Jaipur": ["MI Road", "C-Scheme", "Vaishali Nagar", "Malviya Nagar", "Mansarovar", "Jagatpura"],
    "Surat": ["Ring Road", "Adajan", "Piplod", "Vesu", "Althan", "Athwa", "Katargam"],
    "Lucknow": ["Hazratganj", "Gomti Nagar", "Alambagh", "Aliganj", "Rajajipuram", "Indira Nagar"],
    "Kanpur": ["Civil Lines", "Kidwai Nagar", "Swaroop Nagar", "Kakadeo", "Arya Nagar"],
    "Nagpur": ["Dharampeth", "Sitabuldi", "Sadar", "Wardha Road", "Amravati Road", "Manish Nagar"],
    "Indore": ["Vijay Nagar", "Palasia", "New Palasia", "Scheme 54", "MG Road", "Sapna Sangeeta"],
    "Bhopal": ["MP Nagar", "Arera Colony", "Shahpura", "Kolar Road", "Bairagarh", "Ayodhya Nagar"],
    "Visakhapatnam": ["MVP Colony", "Dwaraka Nagar", "Rushikonda", "Gajuwaka", "Steel Plant Area"],
    "Patna": ["Fraser Road", "Boring Road", "Patliputra", "Kankarbagh", "Rajendra Nagar"],
    "Vadodara": ["Alkapuri", "Fatehganj", "Karelibaug", "Manjalpur", "Gotri", "Vadsar"],
    "Ludhiana": ["Ferozepur Road", "Model Town", "BRS Nagar", "Dugri", "Pakhowal Road"],
    "Agra": ["Sadar", "Civil Lines", "Kamla Nagar", "Sikandra", "Dayalbagh", "Belanganj"]
}

def generate_phone():
    """Generate realistic Indian mobile number"""
    prefixes = ["98", "99", "97", "96", "95", "94", "93", "92", "91", "90", "89", "88", "87", "86", "85", "84", "83", "82", "81", "80", "70", "77", "78", "79"]
    prefix = random.choice(prefixes)
    suffix = ''.join([str(random.randint(0, 9)) for _ in range(8)])
    if random.random() < 0.15:  # 15% chance no phone
        return None
    return f"+91-{prefix}{suffix}"

def generate_address(city):
    """Generate realistic Indian address"""
    areas = AREAS.get(city, ["Main Area", "City Center", "New Area"])
    area = random.choice(areas)
    number = random.randint(1, 999)
    street_type = random.choice(STREET_TYPES)
    return f"{number}, {area} {street_type}, {city}"

def generate_business_name(category):
    """Generate realistic business name for category"""
    prefixes = BUSINESS_PREFIXES.get(category, ["New", "Modern", "Classic", "Premier", "Top"])
    suffixes = BUSINESS_SUFFIXES.get(category, ["Services", "Solutions", "Enterprise", "Group"])
    
    style = random.choice(["prefix_suffix", "prefix_only", "single_word"])
    if style == "prefix_suffix":
        return f"{random.choice(prefixes)} {random.choice(suffixes)}"
    elif style == "prefix_only":
        return f"{random.choice(prefixes)} {category}"
    else:
        return f"{random.choice(prefixes)} {random.choice(suffixes)}"

def generate_listings(count=600):
    """Generate realistic business listings"""
    listings = []
    
    for i in range(count):
        category = random.choice(CATEGORIES)
        city = random.choice(CITIES)
        
        listing = {
            "business_name": generate_business_name(category),
            "category": category,
            "city": city,
            "address": generate_address(city),
            "phone": generate_phone(),
            "source": random.choice(SOURCES),
            "created_at": (datetime.now() - timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d %H:%M:%S")
        }
        listings.append(listing)
    
    return listings

if __name__ == "__main__":
    listings = generate_listings(600)
    
    # Save to JSON
    with open("/home/claude/business-dashboard/data/listings.json", "w") as f:
        json.dump(listings, f, indent=2)
    
    print(f"Generated {len(listings)} business listings")
    
    # Print summary stats
    from collections import Counter
    cities = Counter(l["city"] for l in listings)
    cats = Counter(l["category"] for l in listings)
    sources = Counter(l["source"] for l in listings)
    
    print("\nCity distribution (top 5):")
    for city, count in cities.most_common(5):
        print(f"  {city}: {count}")
    
    print("\nCategory distribution (top 5):")
    for cat, count in cats.most_common(5):
        print(f"  {cat}: {count}")
    
    print("\nSource distribution:")
    for src, count in sources.most_common():
        print(f"  {src}: {count}")
