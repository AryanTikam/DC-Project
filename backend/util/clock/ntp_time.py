"""
Network time protocol (NTP) based clock synchronization utility
"""

import time
import datetime
import threading
import socket
import struct
import logging

logger = logging.getLogger(__name__)

class NTPClient:
    """
    Simple NTP client for time synchronization in the distributed cab system.
    """
    # NTP constants
    _EPOCH_DELTA = 2208988800  # Seconds between 1900-01-01 and 1970-01-01
    _NTP_PORT = 123
    _NTP_MODE = 3  # Client mode
    _NTP_VERSION = 4
    _NTP_PACKET_FORMAT = "!12I"  # Format for the NTP packet
    
    def __init__(self, server="pool.ntp.org", port=123, timeout=5):
        self.server = server
        self.port = port
        self.timeout = timeout
        self.offset = 0  # Time offset in seconds
        self.last_sync_time = 0
        self._lock = threading.RLock()
    
    def get_time(self):
        """Get the current time adjusted by the NTP offset"""
        with self._lock:
            return time.time() + self.offset
    
    def get_utc_time(self):
        """Get the current UTC time as a datetime object"""
        return datetime.datetime.utcfromtimestamp(self.get_time())
    
    def get_utc_iso(self):
        """Get the current UTC time as an ISO-formatted string"""
        return self.get_utc_time().isoformat()
    
    def sync_time(self):
        """Synchronize time with the NTP server"""
        try:
            # Create NTP request packet
            packet = bytearray(48)
            packet[0] = 0x1B  # Set LI, VN, and mode (00 011 011)
            
            # Send request to NTP server
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.settimeout(self.timeout)
                sock.sendto(packet, (self.server, self.port))
                data, _ = sock.recvfrom(48)
            
            # Process NTP response
            if data:
                # Extract timestamps from the response
                unpacked = struct.unpack(self._NTP_PACKET_FORMAT, data[0:48])
                
                # Calculate time offset
                t1 = time.time()
                t2 = unpacked[8] / 2**32 - self._EPOCH_DELTA
                t3 = unpacked[9] / 2**32 - self._EPOCH_DELTA
                t4 = time.time()
                
                # Calculate offset: ((t2 - t1) + (t3 - t4)) / 2
                with self._lock:
                    self.offset = ((t2 - t1) + (t3 - t4)) / 2
                    self.last_sync_time = t4
                
                logger.info(f"NTP sync successful. Offset: {self.offset:.6f}s")
                return self.offset
        except Exception as e:
            logger.error(f"NTP sync failed: {e}")
            return None
    
    def start_periodic_sync(self, interval=3600):
        """
        Start a background thread to periodically sync time
        
        Args:
            interval (int): Time between syncs in seconds (default: 1 hour)
        """
        def _sync_worker():
            while True:
                self.sync_time()
                time.sleep(interval)
        
        # Start the sync thread
        sync_thread = threading.Thread(target=_sync_worker, daemon=True)
        sync_thread.start()
        
        return sync_thread


# Global NTP client for system-wide time synchronization
ntp_client = NTPClient()

def get_system_time():
    """Get the synchronized system time as a timestamp"""
    return ntp_client.get_time()

def get_utc_time():
    """Get the synchronized UTC time as a datetime object"""
    return ntp_client.get_utc_time()

def get_utc_iso():
    """Get the synchronized UTC time as an ISO string"""
    return ntp_client.get_utc_iso()

def sync_time():
    """Manually trigger time synchronization"""
    return ntp_client.sync_time()

def start_time_sync(interval=3600):
    """Start background time synchronization"""
    return ntp_client.start_periodic_sync(interval)