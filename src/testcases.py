import dns.resolver
import dns.update
import dns.flags
import random
import string

def non_existing_domain():
    """Generate a non-existing SLD under .com"""
    while True:
        domain = "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(12)) + ".com"
        try:
            # Try to resolve it locally
            dns.resolver.resolve(domain, "A")
        except dns.exception.Timeout:
            continue
        except dns.resolver.NXDOMAIN:
            break

    return domain

def get_signature():
    """Generate an empty signature dictionnary"""

    return {
        "header":{
            "QR": 0,
            "Opcode": 0,
            "AA": 0,
            "TC": 0,
            "RD": 0,
            "RA": 0,
            # Z flag does not seem to be supported by dnspython
            "AD": 0,
            "CD": 0,
            "RCODE": None,
            "QDCOUNT": 0,
            "ANCOUNT": 0,
            "NSCOUNT": 0,
            "ARCOUNT":0 
        }   
    }


def parse_response_header(response, signature):
    """Parse the response and return its signature"""

    # Add flags to the signature dictionnary
    for flag in dns.flags.to_text(response.flags).split(" "):
        signature["header"][flag] = 1

    # Add other header data into the signature
    signature["header"]["Opcode"] = dns.opcode.to_text(response.opcode())
    signature["header"]["RCODE"] = dns.rcode.to_text(response.rcode())
    signature["header"]["QDCOUNT"] = response.qcount
    signature["header"]["ANCOUNT"] = response.ancount
    signature["header"]["NSCOUNT"] = response.aucount
    signature["header"]["ARCOUNT"] = response.adcount

    # Return the signature
    return signature


def test_baseline(target, domain):
    """
    The simplest baseline test case:

    - Opcode: Query
    - Flags: RD
    - Question: <custom_domain> A  
    """

    # Build a query
    query = dns.message.make_query(qname=dns.name.from_text(text=domain), rdtype=dns.rdatatype.A, flags=dns.flags.from_text("RD"))
    query.set_opcode(dns.opcode.QUERY)
    # Send a query and generate a signature
    try: 
        response = dns.query.udp(q=query, where=target, timeout=5)
        signature = parse_response_header(signature=get_signature(),response=response)
    except dns.exception.Timeout:
        signature = {"error": "Timeout"}
    
    return signature


def test_nx_no_flags(target):
    """
    Query non-recursively a non-existing subdomain:

    - Opcode: Query
    - Flags:
    - Question: <non_existing_domain> A
    """

    # Generate a non-existing domain
    domain = non_existing_domain()

    # Build a query
    query = dns.message.make_query(qname=dns.name.from_text(text=domain), rdtype=dns.rdatatype.A, flags=0)
    query.set_opcode(dns.opcode.QUERY)
    # Send a query and generate a signature
    try:
        response = dns.query.udp(q=query, where=target, timeout=5)
        signature = parse_response_header(signature=get_signature(),response=response)
    except dns.exception.Timeout:
        signature = {"error": "Timeout"}

    return signature


def test_is_response(target, domain):
    """
    Send a query with response flag set:

    - Opcode: Query
    - Flags: QR
    - Question: <custom_domain> A

    """

    # Build a query
    query = dns.message.make_query(qname=dns.name.from_text(text=domain), rdtype=dns.rdatatype.A, flags=dns.flags.from_text("QR"))
    query.set_opcode(dns.opcode.QUERY)
    # Send a query and generate a signature
    try:
        response = dns.query.udp(q=query, where=target, timeout=5)
        signature = parse_response_header(signature=get_signature(),response=response)
    except dns.exception.Timeout:
        signature = {"error": "Timeout"}

    return signature

def test_nx_tc(target):
    """
    Send a query with truncated flag set:

    - Opcode: Query
    - Flags: TC
    - Question: <non_existing_domain> A

    """

    # Generate a non-existing domain
    domain = non_existing_domain()

    # Build a query
    query = dns.message.make_query(qname=dns.name.from_text(text=domain), rdtype=dns.rdatatype.A, flags=dns.flags.from_text("TC"))
    query.set_opcode(dns.opcode.QUERY)
    # Send a query and generate a signature
    try:
        response = dns.query.udp(q=query, where=target, timeout=5)
        signature = parse_response_header(signature=get_signature(),response=response)
    except dns.exception.Timeout:
        signature = {"error": "Timeout"}

    return signature


def test_nx_ad(target):
    """
    Send a query with authoritative data flag set:

    - Opcode: Query
    - Flags: AD
    - Question: <non_existing_domain> A

    """

    # Generate a non-existing domain
    domain = non_existing_domain()

    # Build a query
    query = dns.message.make_query(qname=dns.name.from_text(text=domain), rdtype=dns.rdatatype.A, flags=dns.flags.from_text("AD"))
    query.set_opcode(dns.opcode.QUERY)
    # Send a query and generate a signature
    try:
        response = dns.query.udp(q=query, where=target, timeout=5)
        signature = parse_response_header(signature=get_signature(),response=response)
    except dns.exception.Timeout:
        signature = {"error": "Timeout"}

    return signature


def test_iquery(target, domain):
    """
    Send the recursive query with the IQuery option:

    - Opcode: IQuery
    - Flags: RD
    - Question: <custom_domain> A  
    """

    # Build a query
    query = dns.message.make_query(qname=dns.name.from_text(text=domain), rdtype=dns.rdatatype.A, flags=dns.flags.from_text("RD"))
    query.set_opcode(dns.opcode.IQUERY)
    # Send a query and generate a signature
    try: 
        response = dns.query.udp(q=query, where=target, timeout=5)
        signature = parse_response_header(signature=get_signature(),response=response)
    except dns.exception.Timeout:
        signature = {"error": "Timeout"}
    
    return signature

def test_update(target, domain):
    """
    Send an Update query:

    - Opcode: Update
    - Flags: 
    - Question: <custom_domain> SOA
    """

    # Build a query
    update = dns.update.UpdateMessage(zone=domain)
    # Send a query and generate a signature
    try: 
        response = dns.query.udp(q=update, where=target, timeout=5)
        signature = parse_response_header(signature=get_signature(),response=response)
    except dns.exception.Timeout:
        signature = {"error": "Timeout"}
    
    return signature
