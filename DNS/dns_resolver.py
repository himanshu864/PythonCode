import socket
import struct
import random
import time
import sys

# --- Cache ---
# Structure: { 'hostname': {'ips': ['ip1', 'ip2'], 'expiry_time': timestamp} }
DNS_CACHE = {}

# --- Constants ---
DNS_SERVER_IP = "8.8.8.8"  # Google's Public DNS
DNS_PORT = 53
QUERY_TIMEOUT = 2  # seconds
BUFFER_SIZE = 1024

# DNS Query Types
TYPE_A = 1
# DNS Query Classes
CLASS_IN = 1


def encode_dns_name(domain_name):
    """Encodes a domain name in the DNS format (e.g., www.google.com -> 3www6google3com0)"""
    encoded = b""
    for label in domain_name.encode("ascii").split(b"."):
        encoded += struct.pack("!B", len(label)) + label
    return encoded + b"\x00"  # Null byte to terminate the name


def parse_dns_name(reader):
    """
    Parses a potentially compressed DNS name from a response.
    'reader' is an object with read(n) and tell() methods, and a 'data' attribute.
    Returns the decoded name (str) and the number of bytes originally consumed
    from the reader's position *before* pointer jumps.
    """
    parts = []
    bytes_consumed_original = 0
    jumped = False
    expected_end_offset = -1  # Track end offset after first jump

    while True:
        length_byte = reader.read(1)
        if not length_byte:
            raise EOFError("Reached end of data while parsing name.")

        length = length_byte[0]
        if not jumped:
            bytes_consumed_original += 1

        # Check for pointer (compression)
        if (length & 0xC0) == 0xC0:
            if not jumped:
                # This is the first jump, remember where we should be after the pointer
                expected_end_offset = (
                    reader.tell() + 1
                )  # +1 because we need to read the second byte of the pointer
                jumped = True

            pointer_byte2 = reader.read(1)
            if not pointer_byte2:
                raise EOFError("Reached end of data while parsing name pointer.")
            if not jumped:  # This check is redundant now but kept for clarity
                bytes_consumed_original += 1

            offset = ((length & 0x3F) << 8) | pointer_byte2[0]
            # Create a new reader for the jump
            import io

            jump_reader = io.BytesIO(reader.data)
            jump_reader.seek(offset)
            # Recursively parse the name at the pointer location
            parts.append(
                parse_dns_name(jump_reader)[0]
            )  # Only need the name part from recursive call
            # If this was the first jump, the parsing for this name is complete.
            # Return the combined name and the original bytes consumed (usually 2 for the pointer).
            return ".".join(parts), bytes_consumed_original

        # End of name marker
        elif length == 0:
            break

        # Normal label
        else:
            if not jumped:
                bytes_consumed_original += length
            label = reader.read(length)
            if len(label) < length:
                raise EOFError("Reached end of data while reading label.")
            parts.append(label.decode("ascii"))

    # If we never jumped, the total bytes consumed is correct
    # If we did jump, the original_bytes_consumed is set before the first jump (usually 2)
    return ".".join(parts), bytes_consumed_original


def build_dns_query(hostname, query_type=TYPE_A):
    """Builds a DNS query packet for the given hostname and type."""
    transaction_id = random.randint(0, 65535)

    # Header section (12 bytes)
    # Pack format: ! signifies network byte order (big-endian)
    # H = unsigned short (2 bytes)
    flags = 0x0100  # Standard query (Recursion Desired RD=1)
    qdcount = 1  # Question count
    ancount = 0  # Answer count
    nscount = 0  # Authority count
    arcount = 0  # Additional count

    header = struct.pack(
        "!HHHHHH", transaction_id, flags, qdcount, ancount, nscount, arcount
    )

    # Question section
    qname = encode_dns_name(hostname)
    qtype = struct.pack("!H", query_type)
    qclass = struct.pack("!H", CLASS_IN)

    query = header + qname + qtype + qclass
    return query, transaction_id


def parse_dns_response(response_bytes, expected_id):
    """Parses the DNS response packet and extracts A records and TTL."""
    try:
        # --- 1. Parse Header ---
        header_struct = struct.Struct("!HHHHHH")
        if len(response_bytes) < header_struct.size:
            print("Error: Response too short for header.")
            return None, None

        header = header_struct.unpack(response_bytes[: header_struct.size])
        resp_id, flags, qdcount, ancount, nscount, arcount = header

        # Verify Transaction ID
        if resp_id != expected_id:
            print(
                f"Error: Transaction ID mismatch. Expected {expected_id}, got {resp_id}"
            )
            return None, None

        # Check flags (QR=1 for response, RCODE=0 for no error)
        is_response = (flags & 0x8000) >> 15
        opcode = (flags & 0x7800) >> 11
        authoritative = (flags & 0x0400) >> 10
        truncated = (flags & 0x0200) >> 9
        recursion_desired = (flags & 0x0100) >> 8
        recursion_available = (flags & 0x0080) >> 7
        rcode = flags & 0x000F

        if not is_response:
            print("Error: Received packet is not a response.")
            return None, None
        if rcode != 0:
            print(f"Error: DNS server returned error code {rcode}")
            return None, None
        if truncated:
            print("Warning: Response was truncated. Results may be incomplete.")
            # We could handle this by retrying with TCP, but that's beyond the scope here.

        # --- 2. Setup Reader and Skip Question Section ---
        import io

        reader = io.BytesIO(response_bytes)
        reader.data = response_bytes  # Store full data for pointer jumps
        reader.seek(header_struct.size)  # Move past the header

        for _ in range(qdcount):
            # Parse and discard the question name
            qname, name_bytes_len = parse_dns_name(reader)
            # Skip QTYPE (2 bytes) and QCLASS (2 bytes)
            reader.seek(reader.tell() + 4)

        # --- 3. Parse Answer Section ---
        ips = []
        min_ttl = float("inf")

        if ancount == 0:
            print("No answer records found.")
            # This might be valid (e.g., NXDOMAIN), but for this assignment we seek A records.
            # We could parse Authority section for SOA record's negative caching TTL if needed.
            return None, None

        for _ in range(ancount):
            current_pos = reader.tell()
            # Parse name (often compressed)
            ans_name, name_bytes_len = parse_dns_name(reader)

            # Read the fixed part of the Resource Record (RR) header (10 bytes)
            # HHIH = Type (2), Class (2), TTL (4), RDLength (2)
            rr_header_struct = struct.Struct("!HHIH")
            rr_header_bytes = reader.read(rr_header_struct.size)
            if len(rr_header_bytes) < rr_header_struct.size:
                print("Error: Truncated answer RR header.")
                break
            rr_type, rr_class, rr_ttl, rdlength = rr_header_struct.unpack(
                rr_header_bytes
            )

            # Read the RDATA
            rdata = reader.read(rdlength)
            if len(rdata) < rdlength:
                print("Error: Truncated answer RDATA.")
                break

            # Process A records (IPv4)
            if rr_type == TYPE_A and rr_class == CLASS_IN:
                if rdlength == 4:  # Standard IPv4 length
                    ip_address = socket.inet_ntoa(
                        rdata
                    )  # Convert 4 bytes to dotted decimal string
                    ips.append(ip_address)
                    min_ttl = min(min_ttl, rr_ttl)
                    # print(f"  Found A record: {ans_name} -> {ip_address} (TTL: {rr_ttl})") # Debug
                else:
                    print(
                        f"Warning: Found A record with unexpected data length {rdlength}"
                    )
            # else: # Debugging for other record types
            # print(f"  Skipping RR type {rr_type}, class {rr_class} for {ans_name}")

        if not ips:
            print("No valid A records found in the answer section.")
            return None, None

        # Ensure we got a valid TTL
        if min_ttl == float("inf"):
            print("Warning: Could not determine a valid TTL for A records.")
            # Decide on a default behavior: maybe return None or a default small TTL?
            # For simplicity, let's treat this as failure to get a cacheable result.
            return ips, None

        return ips, min_ttl

    except EOFError as e:
        print(f"Error parsing response: Ran out of data. {e}")
        return None, None
    except struct.error as e:
        print(f"Error unpacking data: {e}")
        return None, None
    except Exception as e:
        print(f"An unexpected error occurred during parsing: {e}")
        import traceback

        traceback.print_exc()
        return None, None


def resolve(hostname, use_cache=True):
    """
    Resolves a hostname to an IP address using manual DNS query and caching.
    """
    global DNS_CACHE
    current_time = time.time()

    # --- 1. Check Cache ---
    if use_cache and hostname in DNS_CACHE:
        cache_entry = DNS_CACHE[hostname]
        if cache_entry["expiry_time"] > current_time:
            print(
                f"Cache HIT for {hostname}. Returning cached IPs: {cache_entry['ips']}"
            )
            return cache_entry["ips"]
        else:
            print(f"Cache EXPIRED for {hostname}.")
            del DNS_CACHE[hostname]  # Remove expired entry
    elif use_cache:
        print(f"Cache MISS for {hostname}.")

    # --- 2. Build Query ---
    print(f"Building query for {hostname}...")
    query_bytes, query_id = build_dns_query(hostname)

    # --- 3. Send Query via Socket ---
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(QUERY_TIMEOUT)

        print(f"Sending query to {DNS_SERVER_IP}:{DNS_PORT}...")
        sock.sendto(query_bytes, (DNS_SERVER_IP, DNS_PORT))

        # --- 4. Receive Response ---
        print("Waiting for response...")
        response_bytes, server_address = sock.recvfrom(BUFFER_SIZE)
        print(f"Received {len(response_bytes)} bytes from {server_address}")

    except socket.timeout:
        print(f"Error: Request timed out for {hostname}")
        return None
    except socket.error as e:
        print(f"Error: Socket error for {hostname}: {e}")
        return None
    finally:
        if sock:
            sock.close()

    # --- 5. Parse Response ---
    print(f"Parsing response for query ID {query_id}...")
    ips, ttl = parse_dns_response(response_bytes, query_id)

    # --- 6. Update Cache ---
    if ips and ttl is not None and ttl > 0:
        expiry_time = current_time + ttl
        DNS_CACHE[hostname] = {"ips": ips, "expiry_time": expiry_time}
        print(
            f"Cached result for {hostname}: IPs={ips}, TTL={ttl}s (Expires at {time.ctime(expiry_time)})"
        )
        return ips
    elif ips:
        # Got IPs but no valid TTL for caching
        print(f"Resolved {hostname} to {ips} but could not cache (invalid TTL).")
        return ips
    else:
        print(f"Failed to resolve {hostname}.")
        return None


# --- Main Execution Example ---
if __name__ == "__main__":
    host_to_resolve = "www.google.com"
    if len(sys.argv) > 1:
        host_to_resolve = sys.argv[1]

    print(f"--- Resolving {host_to_resolve} (1st time) ---")
    result1 = resolve(host_to_resolve)
    if result1:
        print(f"Resolved IPs: {result1}")
    print("-" * 20)

    print(f"--- Resolving {host_to_resolve} (2nd time - testing cache) ---")
    result2 = resolve(host_to_resolve)
    if result2:
        print(f"Resolved IPs: {result2}")
    print("-" * 20)

    # Example to test TTL expiry (if TTL is short enough)
    if result1 and host_to_resolve in DNS_CACHE:
        ttl_value = DNS_CACHE[host_to_resolve]["expiry_time"] - time.time()
        print(f"Cached TTL is approx {ttl_value:.0f}s. Waiting for slightly longer...")
        if ttl_value < 60:  # Only wait if TTL is reasonably short
            wait_time = ttl_value + 2
            print(f"Sleeping for {wait_time:.0f} seconds...")
            time.sleep(wait_time)
            print(
                f"--- Resolving {host_to_resolve} (3rd time - after waiting for expiry) ---"
            )
            result3 = resolve(host_to_resolve)
            if result3:
                print(f"Resolved IPs: {result3}")
            print("-" * 20)
        else:
            print("TTL is too long to demonstrate expiry in this example.")

    print("--- Resolving another host (cloudflare.com) ---")
    result4 = resolve("cloudflare.com")
    if result4:
        print(f"Resolved IPs: {result4}")
    print("-" * 20)

    print("--- Cache contents ---")
    print(DNS_CACHE)
