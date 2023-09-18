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


def random_subdomain():
    """Generate a 12-character random string"""
    return "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(12))


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

def get_signature_ttl():
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
        },
        "answer": {
            "TTL": None
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


def parse_response_header_ttl(response, signature):
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

    # Add the answer's TTL
    ttl = response.answer[0].ttl
    if ttl == 0:
        signature["answer"]["TTL"] = 0
    else:
        signature["answer"]["TTL"] = 1

    # Return the signature
    return signature


def test_baseline(target, domain):
    """
    Send the simplest request:

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


def test_baseline_norec(target, domain):
    """
    Send the simplest request:

    - Opcode: Query
    - Flags: 
    - Question: <custom_domain> A 
    """

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


def test_nx_subdomain(target, domain):
    """
    Query recursively a non-existing subdomain under our domain:

    - Opcode: Query
    - Flags: RD
    - Question: <random_subdomain>.<custom_domain> A
    """

    # Build a query
    query = dns.message.make_query(qname=dns.name.from_text(text=f"{random_subdomain()}.{domain}"), rdtype=dns.rdatatype.A, flags=dns.flags.from_text("RD"))
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
    Send the recursive query with the IQuery opcode:

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


def test_chaos_rd(target, domain):
    """
    The recursive CHAOS-class query:

    - Opcode: Query
    - Flags: RD
    - Question: <custom_domain> CH A  
    """

    # Build a query
    query = dns.message.make_query(qname=dns.name.from_text(text=domain), rdtype=dns.rdatatype.A, rdclass=dns.rdataclass.CHAOS, flags=dns.flags.from_text("RD"))
    query.set_opcode(dns.opcode.QUERY)
    # Send a query and generate a signature
    try: 
        response = dns.query.udp(q=query, where=target, timeout=5)
        signature = parse_response_header(signature=get_signature(),response=response)
    except dns.exception.Timeout:
        signature = {"error": "Timeout"}
    except dns.query.BadResponse as e:
        signature = {"error": str(e)}
    
    return signature


def test_is_response(target, domain):
    """
    Send a recursive query with response flag set:

    - Opcode: Query
    - Flags: QR RD
    - Question: <custom_domain> A

    """

    # Build a query
    query = dns.message.make_query(qname=dns.name.from_text(text=domain), rdtype=dns.rdatatype.A, flags=dns.flags.from_text("RD QR"))
    query.set_opcode(dns.opcode.QUERY)
    # Send a query and generate a signature
    try:
        response = dns.query.udp(q=query, where=target, timeout=5)
        signature = parse_response_header(signature=get_signature(),response=response)
    except dns.exception.Timeout:
        signature = {"error": "Timeout"}

    return signature


def test_tc(target, domain):
    """
    Send a recursive query with truncated flag set:

    - Opcode: Query
    - Flags: TC RD
    - Question: <custom_domain> A

    """

    # Build a query
    query = dns.message.make_query(qname=dns.name.from_text(text=domain), rdtype=dns.rdatatype.A, flags=dns.flags.from_text("TC RD"))
    query.set_opcode(dns.opcode.QUERY)
    # Send a query and generate a signature
    try:
        response = dns.query.udp(q=query, where=target, timeout=5)
        signature = parse_response_header(signature=get_signature(),response=response)
    except dns.exception.Timeout:
        signature = {"error": "Timeout"}

    return signature


def test_lame(target, domain):
    """
    Send the recursive query for a subdomain with lame delegation:

    - Opcode: Query
    - Flags: RD
    - Question: lame.<custom_domain> A 
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


def test_zero_ttl(target, domain):
    """
    Send the simplest request for a zone with 0 TTL:

    - Opcode: Query
    - Flags: RD
    - Question: zero-ttl.<custom_domain> A 

    Assumption: resolver's minimum TTL were not reconfigured
    """

    # Build a query
    query = dns.message.make_query(qname=dns.name.from_text(text=domain), rdtype=dns.rdatatype.A, flags=dns.flags.from_text("RD"))
    query.set_opcode(dns.opcode.QUERY)
    # Send a query and generate a signature
    try: 
        response = dns.query.udp(q=query, where=target, timeout=5)
        signature = parse_response_header_ttl(signature=get_signature_ttl(),response=response)
    except dns.exception.Timeout:
        signature = {"error": "Timeout"}
    
    return signature


def test_edns0(target, domain):
    """
    Send the recursive query signalling the support of EDNS(0):

    - Opcode: Query
    - Flags: RD
    - Question: <custom_domain> A 
    - EDNS(0): no options, payload 512

    Assumption: RFC 2671 (Extension Mechanisms for DNS (EDNS0)) supported.
    """

    # Build a query
    query = dns.message.make_query(qname=dns.name.from_text(text=domain), rdtype=dns.rdatatype.A, flags=dns.flags.from_text("RD"))
    query.use_edns(edns = True, payload=512)
    query.set_opcode(dns.opcode.QUERY)
    # Send a query and generate a signature
    try: 
        response = dns.query.udp(q=query, where=target, timeout=5)
        signature = parse_response_header(signature=get_signature(),response=response)
    except dns.exception.Timeout:
        signature = {"error": "Timeout"}
    
    return signature
