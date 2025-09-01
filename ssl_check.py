import ssl
import socket
from datetime import datetime

def get_ssl_expiry_date(hostname):
    try:
        # Create SSL context
        context = ssl.create_default_context()

        # Open a socket connection to the host on port 443
        with socket.create_connection((hostname, 443), timeout=5) as sock:
            # Wrap the socket with SSL
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                ssl_info = ssock.getpeercert()

                # Extract the expiry date from the certificate
                expiry_str = ssl_info['notAfter']  # e.g. 'Nov 10 12:00:00 2025 GMT'
                expiry_date = datetime.strptime(expiry_str, "%b %d %H:%M:%S %Y %Z")

                return expiry_date  # Return as datetime object

    except Exception as e:
        return None  # Return None if SSL check fails


