import dns.resolver
import dns.flags
import random
import string

def random_string():
    """Returns a 6-character random string"""
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(6))

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


def test_1(target, domain):
    """Test case 1: a reqursive query for an unsigned domain without EDNS0"""

    # Issue a query
    qname = dns.name.from_text(text=domain)
    query = dns.message.make_query(qname=qname, rdtype=dns.rdatatype.A, flags=dns.flags.from_text("RD"))
    query.set_opcode(dns.opcode.QUERY)
    response = dns.query.udp(q=query, where=target, timeout=5)

    # Parse the response to generate the signature
    signature = parse_response_header(signature=get_signature(),response=response)

    return signature

def test_2(target, domain):
    """Test case 2: a reqursive query for a non-existing unsigned domain without EDNS0"""

    # Issue a query
    qname = dns.name.from_text(text=domain)
    query = dns.message.make_query(qname=qname, rdtype=dns.rdatatype.A, flags=dns.flags.from_text("RD"))
    query.set_opcode(dns.opcode.QUERY)
    response = dns.query.udp(q=query, where=target, timeout=5)

    # Parse the response to generate the signature
    signature = parse_response_header(signature=get_signature(),response=response)

    return signature

def test_3(target, domain):
    """Test case 3: a reqursive query for a non-existing resource record for an unsigned domain without EDNS0"""

    # Issue a query
    qname = dns.name.from_text(text=domain)
    query = dns.message.make_query(qname=qname, rdtype=dns.rdatatype.TXT, flags=dns.flags.from_text("RD"))
    query.set_opcode(dns.opcode.QUERY)
    response = dns.query.udp(q=query, where=target, timeout=5)

    # Parse the response to generate the signature
    signature = parse_response_header(signature=get_signature(),response=response)

    return signature

def test_4(target, domain):
    """Test case 4: a reqursive query for an experimental non-existing resource record for an unsigned domain without EDNS0"""

    # Issue a query
    qname = dns.name.from_text(text=domain)
    query = dns.message.make_query(qname=qname, rdtype=dns.rdatatype.NULL, flags=dns.flags.from_text("RD"))
    query.set_opcode(dns.opcode.QUERY)
    response = dns.query.udp(q=query, where=target, timeout=5)

    # Parse the response to generate the signature
    signature = parse_response_header(signature=get_signature(),response=response)

    return signature

def test_5(target, domain):
    """Test case 5: a reqursive query for the newest non-existing resource record for an unsigned domain without EDNS0"""

    # Issue a query
    qname = dns.name.from_text(text=domain)
    query = dns.message.make_query(qname=qname, rdtype=dns.rdatatype.ZONEMD, flags=dns.flags.from_text("RD"))
    query.set_opcode(dns.opcode.QUERY)
    response = dns.query.udp(q=query, where=target, timeout=5)

    # Parse the response to generate the signature
    signature = parse_response_header(signature=get_signature(),response=response)

    return signature

def test_6(target):
    """Test case 6: query a non-existing domain non-recursively"""

    # Find a non-existing domain name
    while True:
        domain = f"{random_string()}.com"
        try:
            dns.resolver.resolve(domain, "A")
        except dns.resolver.NXDOMAIN:
            break

    # Issue a query
    qname = dns.name.from_text(text=domain)
    query = dns.message.make_query(qname=qname, rdtype=dns.rdatatype.A, flags=0)
    query.set_opcode(dns.opcode.QUERY)

    try:
        response = dns.query.udp(q=query, where=target, timeout=5)
        # Parse the response to generate the signature
        signature = parse_response_header(signature=get_signature(),response=response)
    except dns.exception.Timeout:
        signature = {"error": "Timeout"}

    return signature

def test_7(target, domain):
    """Test case 7: a non-reqursive query for an unsigned domain without EDNS0 with QR=1"""

    # Issue a query
    qname = dns.name.from_text(text=domain)
    query = dns.message.make_query(qname=qname, rdtype=dns.rdatatype.A, flags=dns.flags.from_text("QR"))
    query.set_opcode(dns.opcode.QUERY)

    try:
        response = dns.query.udp(q=query, where=target, timeout=5)
        # Parse the response to generate the signature
        signature = parse_response_header(signature=get_signature(),response=response)
    except dns.exception.Timeout:
        signature = {"error": "Timeout"}

    return signature
