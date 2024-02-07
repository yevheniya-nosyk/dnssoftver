# Copyright 2023 Yevheniya Nosyk
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
    domain = random_string() + "." + q_options['query_options']['domain']

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
    except Exception as e:
        # Catch any other exception
        signature = {"other_exception": str(e)}

    if "software" in q_options:
        return {"software": q_options["software"], "query_name": q_options["query_name"], "signature": signature}
    else:
        return {"ip": q_options["ip"], "query_name": q_options["query_name"], "signature": signature}
        


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
    signature["QDCOUNT"] = response.section_count("QUESTION")
    signature["ANCOUNT"] = response.section_count("ANSWER")
    signature["NSCOUNT"] = response.section_count("AUTHORITY")
    signature["ARCOUNT"] = response.section_count("ADDITIONAL")

    # Return the signature
    return signature


# Load the .env file
dotenv.load_dotenv()

# The dictionnary below stores all the possible options to build DNS queries,
# such as domain names, resource records, classes, flags, etc.
# Empty strings signify that the corresponding flags are not set.

query_options = {
    "domain": ["baseline.dnssoftver.com"],
    "resource_record": ["A"],
    "class": ["RESERVED0", "IN", "CH", "HS", "NONE", "ANY"],
    "opcode": ["QUERY", "IQUERY", "STATUS", "NOTIFY"],
    "flag_qr": ["QR", ""],
    "flag_aa": ["AA", ""],
    "flag_tc": ["TC", ""],
    "flag_rd": ["RD", ""],
    "flag_ra": ["RA", ""],
}
