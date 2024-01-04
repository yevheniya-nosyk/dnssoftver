import dns.resolver
import dns.flags
import dotenv
import random
import string
import os

def random_string():
    """Generate a random 12-character string"""
    return "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(12))


def generate_dns_query(q_options):
    """Craft a DNS query and send it"""

    # Generate the query name, which will contain a random subdomain
    # unless the domain name is special
    if os.getenv('DOMAIN') in q_options['query_options']['domain']:
        domain = random_string() + "." + q_options['query_options']['domain']
    else:
        domain = q_options['query_options']['domain']

    # Extract flags from the query options and concatenate to a string
    flags = " ".join([q_options["query_options"][i] for i in q_options["query_options"] if i.startswith("flag_") if q_options["query_options"][i]])

    # Build the DNS query
    query = dns.message.make_query(
        qname=dns.name.from_text(text=domain), 
        rdtype=dns.rdatatype.from_text(text=q_options["query_options"]["resource_record"]), 
        rdclass=dns.rdataclass.from_text(text=q_options["query_options"]["class"]),
        flags=dns.flags.from_text(text=flags)
        )
    
    # Set the option code
    query.set_opcode(dns.opcode.from_text(text=q_options["query_options"]["opcode"]))

    # Send the query and parse the response
    try:
        response = dns.query.udp(q=query, where=q_options["ip"], timeout=5) 
        signature = parse_dns_query(response=response)
    except dns.exception.Timeout:
        signature = {"error": "Timeout after 5 seconds"}
    except dns.query.BadResponse as e:
        signature = {"error": str(e)}

    return {"software": q_options["software"], "query_name": q_options["query_name"], "signature": signature}


def parse_dns_query(response):
    """Parse the response and return its signature"""

    # Create an empty signature
    signature = {
        "QR": 0,
        "Opcode": 0,
        "AA": 0,
        "TC": 0,
        "RD": 0,
        "RA": 0,
        "RCODE": None,
        "QDCOUNT": 0,
        "ANCOUNT": 0,
        "NSCOUNT": 0,
        "ARCOUNT": 0 
    }

    # Add flags to the signature dictionnary
    for flag in dns.flags.to_text(response.flags).split(" "):
        if flag in signature:
            signature[flag] = 1

    # Add other header data into the signature
    signature["Opcode"] = dns.opcode.to_text(response.opcode())
    signature["RCODE"] = dns.rcode.to_text(response.rcode())
    signature["QDCOUNT"] = response.qcount
    signature["ANCOUNT"] = response.ancount
    signature["NSCOUNT"] = response.aucount
    signature["ARCOUNT"] = response.adcount

    # Return the signature
    return signature


# Load the .env file
dotenv.load_dotenv()

# The dictionnary below stores all the possible options to build DNS queries,
# such as domain names, resource records, classes, flags, etc.
# Empty strings signify that the corresponding flags are not set.

query_options = {
    "domain": [f"baseline.{os.getenv('DOMAIN')}", "1.2.3.4"],
    "resource_record": ["A"],
    "class": ["RESERVED0", "IN", "CH", "HS", "NONE", "ANY"],
    "opcode": ["QUERY", "IQUERY", "STATUS", "NOTIFY"],
    "flag_qr": ["QR", ""],
    "flag_aa": ["AA", ""],
    "flag_tc": ["TC", ""],
    "flag_rd": ["RD", ""],
    "flag_ra": ["RA", ""],
}
