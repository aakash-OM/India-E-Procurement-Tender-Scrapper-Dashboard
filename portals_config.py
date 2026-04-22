"""
Government Portal Registry – All Indian Government e-Procurement Portals
"""

CENTRAL_PORTALS = [
    {
        "id": "gem", "name": "GeM", "full_name": "Government e-Marketplace",
        "url": "https://bidplus.gem.gov.in", "search_url": "https://bidplus.gem.gov.in/all-bids",
        "type": "central", "category": "Central Government",
        "implemented": True, "icon": "fa-landmark", "color": "#00d4ff",
        "description": "Primary central govt procurement marketplace"
    },
    {
        "id": "cppp", "name": "CPPP", "full_name": "Central Public Procurement Portal",
        "url": "https://eprocure.gov.in/cppp/", "search_url": "https://eprocure.gov.in/cppp/",
        "type": "central", "category": "Central Government",
        "implemented": False, "icon": "fa-building-columns", "color": "#7b2fff",
        "description": "Unified central government procurement portal"
    },
    {
        "id": "mstc", "name": "MSTC", "full_name": "MSTC Limited e-Commerce",
        "url": "https://www.mstcecommerce.com", "search_url": "https://www.mstcecommerce.com",
        "type": "central", "category": "Central Government",
        "implemented": False, "icon": "fa-store", "color": "#00ff88",
        "description": "MSTC e-auction and procurement portal"
    },
    {
        "id": "nsic", "name": "NSIC", "full_name": "National Small Industries Corporation",
        "url": "https://www.nsic.co.in", "search_url": "https://www.nsic.co.in",
        "type": "central", "category": "Central Government",
        "implemented": False, "icon": "fa-industry", "color": "#ffa502",
        "description": "MSME procurement and tender portal"
    },
]

RAILWAY_DEFENCE_PORTALS = [
    {
        "id": "ireps", "name": "IREPS", "full_name": "Indian Railway E-Procurement System",
        "url": "https://www.ireps.gov.in", "search_url": "https://www.ireps.gov.in",
        "type": "psu", "category": "Railways & Defence",
        "implemented": False, "icon": "fa-train", "color": "#ff6b35",
        "description": "Indian Railways entire procurement"
    },
    {
        "id": "rites", "name": "RITES", "full_name": "RITES Limited (Rail India Technical)",
        "url": "https://www.rites.com/web/rites/tenders", "search_url": "https://www.rites.com/web/rites/tenders",
        "type": "psu", "category": "Railways & Defence",
        "implemented": False, "icon": "fa-train-subway", "color": "#00d4ff",
        "description": "RITES tender management portal"
    },
    {
        "id": "ircon", "name": "IRCON", "full_name": "IRCON International Limited",
        "url": "https://www.ircon.org/index.php/tenders", "search_url": "https://www.ircon.org/index.php/tenders",
        "type": "psu", "category": "Railways & Defence",
        "implemented": False, "icon": "fa-hard-hat", "color": "#ffa502",
        "description": "Railway construction tenders"
    },
    {
        "id": "bel", "name": "BEL", "full_name": "Bharat Electronics Limited",
        "url": "https://www.bel-india.in/Content.aspx?tp=1&mn=57", "search_url": "https://www.bel-india.in/Content.aspx?tp=1&mn=57",
        "type": "psu", "category": "Railways & Defence",
        "implemented": False, "icon": "fa-satellite-dish", "color": "#2ed573",
        "description": "Defence electronics procurement"
    },
    {
        "id": "hal", "name": "HAL", "full_name": "Hindustan Aeronautics Limited",
        "url": "https://hal-india.co.in/Tenders/", "search_url": "https://hal-india.co.in/Tenders/",
        "type": "psu", "category": "Railways & Defence",
        "implemented": False, "icon": "fa-plane", "color": "#1e90ff",
        "description": "Aerospace and defence tenders"
    },
    {
        "id": "isro", "name": "ISRO", "full_name": "Indian Space Research Organisation",
        "url": "https://www.isro.gov.in/Tenders.html", "search_url": "https://www.isro.gov.in/Tenders.html",
        "type": "psu", "category": "Railways & Defence",
        "implemented": False, "icon": "fa-rocket", "color": "#ff6b35",
        "description": "Space technology procurement"
    },
]

ENERGY_PSU_PORTALS = [
    {
        "id": "ntpc", "name": "NTPC", "full_name": "NTPC Limited",
        "url": "https://www.ntpctender.com", "search_url": "https://www.ntpctender.com",
        "type": "psu", "category": "Power & Energy",
        "implemented": False, "icon": "fa-bolt", "color": "#00d4ff",
        "description": "National Thermal Power Corporation tenders"
    },
    {
        "id": "nhpc", "name": "NHPC", "full_name": "NHPC Limited",
        "url": "https://www.nhpcindia.com/tender", "search_url": "https://www.nhpcindia.com/tender",
        "type": "psu", "category": "Power & Energy",
        "implemented": False, "icon": "fa-water", "color": "#1e90ff",
        "description": "National Hydroelectric Power tenders"
    },
    {
        "id": "pgcil", "name": "Power Grid", "full_name": "Power Grid Corporation of India",
        "url": "https://www.powergridindia.com/tenders", "search_url": "https://www.powergridindia.com/tenders",
        "type": "psu", "category": "Power & Energy",
        "implemented": False, "icon": "fa-plug", "color": "#7b2fff",
        "description": "National power transmission grid tenders"
    },
    {
        "id": "ongc", "name": "ONGC", "full_name": "Oil and Natural Gas Corporation",
        "url": "https://www.ongcindia.com/wps/wcm/connect/ongc/home/tender/", "search_url": "https://www.ongcindia.com/wps/wcm/connect/ongc/home/tender/",
        "type": "psu", "category": "Petroleum & Energy",
        "implemented": False, "icon": "fa-oil-well", "color": "#ff9500",
        "description": "Upstream oil & gas procurement"
    },
    {
        "id": "gail", "name": "GAIL", "full_name": "Gas Authority of India Limited",
        "url": "https://www.gailonline.com/", "search_url": "https://www.gailonline.com/",
        "type": "psu", "category": "Petroleum & Energy",
        "implemented": False, "icon": "fa-fire", "color": "#ff6b35",
        "description": "Natural gas infrastructure tenders"
    },
    {
        "id": "iocl", "name": "IOCL", "full_name": "Indian Oil Corporation Limited",
        "url": "https://tenders.iocl.com", "search_url": "https://tenders.iocl.com",
        "type": "psu", "category": "Petroleum & Energy",
        "implemented": False, "icon": "fa-gas-pump", "color": "#ff4757",
        "description": "India's largest oil refining company tenders"
    },
    {
        "id": "bpcl", "name": "BPCL", "full_name": "Bharat Petroleum Corporation Limited",
        "url": "https://www.bpclsmartbuy.com", "search_url": "https://www.bpclsmartbuy.com",
        "type": "psu", "category": "Petroleum & Energy",
        "implemented": False, "icon": "fa-droplet", "color": "#ffa502",
        "description": "Bharat Petroleum procurement portal"
    },
    {
        "id": "hpcl", "name": "HPCL", "full_name": "Hindustan Petroleum Corporation Limited",
        "url": "https://www.hindustanpetroleum.com/TendersIntimation", "search_url": "https://www.hindustanpetroleum.com/TendersIntimation",
        "type": "psu", "category": "Petroleum & Energy",
        "implemented": False, "icon": "fa-flask", "color": "#ff6348",
        "description": "Hindustan Petroleum tenders"
    },
]

MANUFACTURING_PSU_PORTALS = [
    {
        "id": "bhel", "name": "BHEL", "full_name": "Bharat Heavy Electricals Limited",
        "url": "https://www.bhel.com/tenders", "search_url": "https://www.bhel.com/tenders",
        "type": "psu", "category": "Manufacturing",
        "implemented": False, "icon": "fa-cogs", "color": "#00ff88",
        "description": "Heavy electrical engineering procurement"
    },
    {
        "id": "sail", "name": "SAIL", "full_name": "Steel Authority of India Limited",
        "url": "https://www.sail.co.in/en/tenders", "search_url": "https://www.sail.co.in/en/tenders",
        "type": "psu", "category": "Manufacturing",
        "implemented": False, "icon": "fa-warehouse", "color": "#a4b0be",
        "description": "India's largest steel producer tenders"
    },
    {
        "id": "coal_india", "name": "Coal India", "full_name": "Coal India Limited",
        "url": "https://coalindia.in/en-us/TENDERS.aspx", "search_url": "https://coalindia.in/en-us/TENDERS.aspx",
        "type": "psu", "category": "Manufacturing",
        "implemented": False, "icon": "fa-mountain", "color": "#636e72",
        "description": "World's largest coal producer tenders"
    },
    {
        "id": "nbcc", "name": "NBCC", "full_name": "National Buildings Construction Corporation",
        "url": "https://nbccindia.com/tendernotice_new.aspx", "search_url": "https://nbccindia.com/tendernotice_new.aspx",
        "type": "psu", "category": "Infrastructure",
        "implemented": False, "icon": "fa-building", "color": "#ff4757",
        "description": "Government buildings construction tenders"
    },
    {
        "id": "aai", "name": "AAI", "full_name": "Airports Authority of India",
        "url": "https://www.aai.aero/en/business-opportunities/tenders", "search_url": "https://www.aai.aero/en/business-opportunities/tenders",
        "type": "psu", "category": "Infrastructure",
        "implemented": False, "icon": "fa-plane-departure", "color": "#7b2fff",
        "description": "Airport infrastructure procurement"
    },
    {
        "id": "nhai", "name": "NHAI", "full_name": "National Highways Authority of India",
        "url": "https://nhai.gov.in/ShowTender", "search_url": "https://nhai.gov.in/ShowTender",
        "type": "psu", "category": "Infrastructure",
        "implemented": False, "icon": "fa-road", "color": "#ff9500",
        "description": "Highway construction and maintenance tenders"
    },
    {
        "id": "dmrc", "name": "DMRC", "full_name": "Delhi Metro Rail Corporation",
        "url": "https://www.delhimetrorail.com/tenders.aspx", "search_url": "https://www.delhimetrorail.com/tenders.aspx",
        "type": "psu", "category": "Metro/Transport",
        "implemented": False, "icon": "fa-train-subway", "color": "#00d4ff",
        "description": "Delhi Metro Rail procurement"
    },
]

STATE_PORTALS = [
    # North India
    {"id": "up",  "name": "Uttar Pradesh",    "state": "Uttar Pradesh",    "region": "North",    "url": "https://etender.up.nic.in",      "abbreviation": "UP",  "type": "state", "implemented": False, "icon": "fa-map-location-dot", "color": "#7b2fff"},
    {"id": "hr",  "name": "Haryana",           "state": "Haryana",           "region": "North",    "url": "https://etenders.hry.nic.in",    "abbreviation": "HR",  "type": "state", "implemented": False, "icon": "fa-map-location-dot", "color": "#00d4ff"},
    {"id": "pb",  "name": "Punjab",             "state": "Punjab",             "region": "North",    "url": "https://eproc.punjab.gov.in",    "abbreviation": "PB",  "type": "state", "implemented": False, "icon": "fa-map-location-dot", "color": "#ff6b35"},
    {"id": "rj",  "name": "Rajasthan",          "state": "Rajasthan",          "region": "North",    "url": "https://sppp.rajasthan.gov.in",  "abbreviation": "RJ",  "type": "state", "implemented": False, "icon": "fa-map-location-dot", "color": "#ffa502"},
    {"id": "dl",  "name": "Delhi",              "state": "Delhi",              "region": "North",    "url": "https://etenders.delhi.gov.in",  "abbreviation": "DL",  "type": "state", "implemented": False, "icon": "fa-map-location-dot", "color": "#00ff88"},
    {"id": "hp",  "name": "Himachal Pradesh",   "state": "Himachal Pradesh",   "region": "North",    "url": "https://hptenders.gov.in",       "abbreviation": "HP",  "type": "state", "implemented": False, "icon": "fa-map-location-dot", "color": "#1e90ff"},
    {"id": "uk",  "name": "Uttarakhand",        "state": "Uttarakhand",        "region": "North",    "url": "https://uktenders.gov.in",       "abbreviation": "UK",  "type": "state", "implemented": False, "icon": "fa-map-location-dot", "color": "#2ed573"},
    {"id": "jk",  "name": "Jammu & Kashmir",    "state": "Jammu & Kashmir",    "region": "North",    "url": "https://jktenders.gov.in",       "abbreviation": "JK",  "type": "state", "implemented": False, "icon": "fa-map-location-dot", "color": "#ff4757"},
    # West India
    {"id": "mh",  "name": "Maharashtra",        "state": "Maharashtra",        "region": "West",     "url": "https://mahatenders.gov.in",     "abbreviation": "MH",  "type": "state", "implemented": False, "icon": "fa-map-location-dot", "color": "#ff9500"},
    {"id": "gj",  "name": "Gujarat",            "state": "Gujarat",            "region": "West",     "url": "https://tender.gujarat.gov.in",  "abbreviation": "GJ",  "type": "state", "implemented": False, "icon": "fa-map-location-dot", "color": "#00d4ff"},
    {"id": "ga",  "name": "Goa",                "state": "Goa",                "region": "West",     "url": "https://goatenders.gov.in",      "abbreviation": "GA",  "type": "state", "implemented": False, "icon": "fa-map-location-dot", "color": "#7b2fff"},
    # South India
    {"id": "ka",  "name": "Karnataka",          "state": "Karnataka",          "region": "South",    "url": "https://etender.karnataka.gov.in","abbreviation": "KA", "type": "state", "implemented": False, "icon": "fa-map-location-dot", "color": "#ff6b35"},
    {"id": "tg",  "name": "Telangana",          "state": "Telangana",          "region": "South",    "url": "https://tenders.telangana.gov.in","abbreviation": "TG", "type": "state", "implemented": False, "icon": "fa-map-location-dot", "color": "#1e90ff"},
    {"id": "ap",  "name": "Andhra Pradesh",     "state": "Andhra Pradesh",     "region": "South",    "url": "https://tender.apeprocurement.gov.in","abbreviation": "AP","type": "state", "implemented": False, "icon": "fa-map-location-dot", "color": "#00ff88"},
    {"id": "tn",  "name": "Tamil Nadu",         "state": "Tamil Nadu",         "region": "South",    "url": "https://tntenders.gov.in",       "abbreviation": "TN",  "type": "state", "implemented": False, "icon": "fa-map-location-dot", "color": "#ffa502"},
    {"id": "kl",  "name": "Kerala",             "state": "Kerala",             "region": "South",    "url": "https://etenders.kerala.gov.in", "abbreviation": "KL",  "type": "state", "implemented": False, "icon": "fa-map-location-dot", "color": "#2ed573"},
    # East India
    {"id": "wb",  "name": "West Bengal",        "state": "West Bengal",        "region": "East",     "url": "https://wbtenders.gov.in",       "abbreviation": "WB",  "type": "state", "implemented": False, "icon": "fa-map-location-dot", "color": "#ff4757"},
    {"id": "od",  "name": "Odisha",             "state": "Odisha",             "region": "East",     "url": "https://tenders.odisha.gov.in",  "abbreviation": "OD",  "type": "state", "implemented": False, "icon": "fa-map-location-dot", "color": "#00d4ff"},
    {"id": "br",  "name": "Bihar",              "state": "Bihar",              "region": "East",     "url": "https://eproc.bihar.gov.in",     "abbreviation": "BR",  "type": "state", "implemented": False, "icon": "fa-map-location-dot", "color": "#7b2fff"},
    {"id": "jh",  "name": "Jharkhand",          "state": "Jharkhand",          "region": "East",     "url": "https://jharkhandtenders.gov.in","abbreviation": "JH",  "type": "state", "implemented": False, "icon": "fa-map-location-dot", "color": "#ff6b35"},
    # Central India
    {"id": "mp",  "name": "Madhya Pradesh",     "state": "Madhya Pradesh",     "region": "Central",  "url": "https://mptenders.gov.in",       "abbreviation": "MP",  "type": "state", "implemented": False, "icon": "fa-map-location-dot", "color": "#ffa502"},
    {"id": "cg",  "name": "Chhattisgarh",       "state": "Chhattisgarh",       "region": "Central",  "url": "https://eproc.cgstate.gov.in",   "abbreviation": "CG",  "type": "state", "implemented": False, "icon": "fa-map-location-dot", "color": "#00ff88"},
    # Northeast India
    {"id": "as",  "name": "Assam",              "state": "Assam",              "region": "Northeast", "url": "https://assamtenders.gov.in",   "abbreviation": "AS",  "type": "state", "implemented": False, "icon": "fa-map-location-dot", "color": "#1e90ff"},
    {"id": "mn",  "name": "Manipur",            "state": "Manipur",            "region": "Northeast", "url": "https://manipurtender.nic.in",  "abbreviation": "MN",  "type": "state", "implemented": False, "icon": "fa-map-location-dot", "color": "#2ed573"},
    {"id": "ml",  "name": "Meghalaya",          "state": "Meghalaya",          "region": "Northeast", "url": "https://meghalayatender.gov.in","abbreviation": "ML",  "type": "state", "implemented": False, "icon": "fa-map-location-dot", "color": "#ff9500"},
    {"id": "mz",  "name": "Mizoram",            "state": "Mizoram",            "region": "Northeast", "url": "https://mizoramtender.gov.in",  "abbreviation": "MZ",  "type": "state", "implemented": False, "icon": "fa-map-location-dot", "color": "#00d4ff"},
    {"id": "nl",  "name": "Nagaland",           "state": "Nagaland",           "region": "Northeast", "url": "https://nagalandtender.nic.in", "abbreviation": "NL",  "type": "state", "implemented": False, "icon": "fa-map-location-dot", "color": "#7b2fff"},
    {"id": "tr",  "name": "Tripura",            "state": "Tripura",            "region": "Northeast", "url": "https://tripuratender.nic.in",  "abbreviation": "TR",  "type": "state", "implemented": False, "icon": "fa-map-location-dot", "color": "#ff6b35"},
    {"id": "ar",  "name": "Arunachal Pradesh",  "state": "Arunachal Pradesh",  "region": "Northeast", "url": "https://arunachaltender.nic.in","abbreviation": "AR",  "type": "state", "implemented": False, "icon": "fa-map-location-dot", "color": "#ffa502"},
    {"id": "sk",  "name": "Sikkim",             "state": "Sikkim",             "region": "Northeast", "url": "https://sikkimtender.gov.in",   "abbreviation": "SK",  "type": "state", "implemented": False, "icon": "fa-map-location-dot", "color": "#00ff88"},
    # UTs
    {"id": "ch",  "name": "Chandigarh",         "state": "Chandigarh",         "region": "North",    "url": "https://etenders.chd.nic.in",   "abbreviation": "CH",  "type": "state", "implemented": False, "icon": "fa-map-location-dot", "color": "#00d4ff"},
    {"id": "py",  "name": "Puducherry",         "state": "Puducherry",         "region": "South",    "url": "https://py.gov.in/tenders",     "abbreviation": "PY",  "type": "state", "implemented": False, "icon": "fa-map-location-dot", "color": "#1e90ff"},
    {"id": "an",  "name": "Andaman & Nicobar",  "state": "Andaman & Nicobar",  "region": "South",    "url": "https://andamantender.gov.in",  "abbreviation": "AN",  "type": "state", "implemented": False, "icon": "fa-map-location-dot", "color": "#2ed573"},
    {"id": "ld",  "name": "Lakshadweep",        "state": "Lakshadweep",        "region": "South",    "url": "https://lakshadweep.gov.in",    "abbreviation": "LD",  "type": "state", "implemented": False, "icon": "fa-map-location-dot", "color": "#ffa502"},
]

ALL_PORTALS = CENTRAL_PORTALS + RAILWAY_DEFENCE_PORTALS + ENERGY_PSU_PORTALS + MANUFACTURING_PSU_PORTALS + STATE_PORTALS
PORTAL_BY_ID = {p["id"]: p for p in ALL_PORTALS}

REGIONS = {
    "North":     ["Uttar Pradesh", "Haryana", "Punjab", "Rajasthan", "Delhi", "Himachal Pradesh", "Uttarakhand", "Jammu & Kashmir", "Chandigarh"],
    "West":      ["Maharashtra", "Gujarat", "Goa"],
    "South":     ["Karnataka", "Telangana", "Andhra Pradesh", "Tamil Nadu", "Kerala", "Puducherry", "Andaman & Nicobar", "Lakshadweep"],
    "East":      ["West Bengal", "Odisha", "Bihar", "Jharkhand"],
    "Central":   ["Madhya Pradesh", "Chhattisgarh"],
    "Northeast": ["Assam", "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Tripura", "Arunachal Pradesh", "Sikkim"],
}

DEFAULT_KEYWORDS = {
    "Electrical Equipment": [
        "Transformer", "Power Transformer", "Distribution Transformer",
        "Circuit Breaker", "VCB", "ACB", "MCB", "MCCB",
        "Switchgear", "Control Panel", "MCC Panel", "PCC Panel",
        "Busbar", "Busduct", "Isolator", "Disconnector",
        "Capacitor Bank", "Reactor", "HRC Fuse", "LT Fuse",
    ],
    "Cables & Accessories": [
        "Cable", "HT Cable", "LT Cable", "Power Cable", "Control Cable",
        "Cable Jointing", "Cable Tray", "XLPE Cable", "OPGW", "OFC",
        "Copper Lug", "Aluminium Lug", "Bimetallic Connector",
    ],
    "Transformer Parts": [
        "Tap Changer", "OLTC", "Silica Gel Breather", "Buchholz Relay",
        "WTI OTI", "Conservator", "Bushing", "HV LV Bushing",
        "Radiator", "Oil Level Gauge", "PRV", "MOG", "Marshalling Box",
        "Press Board", "Crepe Paper", "Cork Washer", "Nomex Paper",
    ],
    "Power & Substation": [
        "Substation", "Grid Station", "Solar Panel", "Solar Inverter",
        "Energy Meter", "Smart Meter", "AMR Meter", "SCADA",
        "Current Transformer", "Potential Transformer", "Protection Relay",
        "Lightning Arrester", "Surge Arrestor", "Earthing Material",
    ],
    "Fittings & Hardware": [
        "Copper Busbar", "Aluminium Busbar", "Copper Sheet", "Brass Fitting",
        "PG Clamp", "JAW Clamp", "BI-Metallic Clamp", "Copper Thimble",
        "Nut Bolt", "MS Hardware", "GI Sheet", "Steel Structure",
    ],
    "IT & Communication": [
        "SCADA System", "RTU", "PLC", "HMI", "DCS",
        "Fiber Optic Cable", "Communication Tower", "Network Switch", "Server",
    ],
}
