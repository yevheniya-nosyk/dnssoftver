import dns.resolver
import dns.flags

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

