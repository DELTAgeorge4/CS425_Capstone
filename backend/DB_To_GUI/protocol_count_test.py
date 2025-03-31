def identify_application_protocol(packet):
    """ Identify application-layer protocols using payload signatures. """
    if Raw in packet and len(packet[Raw].load) > 0:  # Ensure there's a payload
        raw_data = bytes(packet[Raw].load)

        # 🌐 Web Protocols
        if raw_data.startswith(b'GET ') or raw_data.startswith(b'POST ') or b'HTTP/' in raw_data:
            return 'HTTP'
        if raw_data.startswith(b'\x16\x03') and b'TLS' in raw_data:
            return 'TLS/SSL'
        
        # 📡 Network Services
        if raw_data.startswith(b'\x00\x01') or b'QUERY' in raw_data:
            return 'DNS'
        if raw_data.startswith(b'SSH-2.0') or raw_data.startswith(b'SSH-1.99'):
            return 'SSH'  # Detect SSH handshake
        if raw_data[:2] == b'\x00\x00' and len(raw_data) > 20:
            return 'Encrypted SSH'  # Detect encrypted SSH traffic
        if raw_data.startswith(b'220') and b'FTP' in raw_data:
            return 'FTP'
        if raw_data.startswith(b'\x03\x00') or raw_data.startswith(b'\x03\x01'):
            return 'SMB'
        if raw_data.startswith(b'\x17\x03'):
            return 'TLS Application Data'

        # 📧 Email Protocols
        if b'SMTP' in raw_data:
            return 'SMTP'
        if b'IMAP' in raw_data:
            return 'IMAP'
        if b'POP3' in raw_data:
            return 'POP3'
        
        # 🖥️ Remote Access Protocols
        if raw_data.startswith(b'RFB 003.') or b'VNC' in raw_data:
            return 'VNC'
        if raw_data.startswith(b'\x03\x00\x00\x0b\x06\xd0\x00\x00'):
            return 'RDP'

        # 🔐 Directory Services
        if b'LDAP' in raw_data:
            return 'LDAP'
        
        # 🔌 IoT/Network Management
        if b'SNMP' in raw_data:
            return 'SNMP'

        # 📡 Routing Protocols
        if b'BGP' in raw_data:
            return 'BGP'

        # 💾 Database Protocols
        if b'MySQL' in raw_data:
            return 'MySQL'
    
    return None  # Return None instead of 'Unknown' to avoid unnecessary increments