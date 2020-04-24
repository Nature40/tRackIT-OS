import logging
import subprocess
import textwrap
import time

# from sensorproxy.wifi import WiFi, WiFiManager


logger = logging.getLogger(__name__)


class WireGuardException(Exception):
    pass


class WireGuard:
    """Class to hold configuration of a WireGuard-VPN-link"""

    # def __init__(self, mgr, ssid, psk, interface, self_address, self_private_key, peer_endpoint, peer_public_key, peer_allowed_ips):
    def __init__(self, interface, self_address, self_private_key, peer_endpoint, peer_public_key, peer_allowed_ips):
        """
        Args:
            XXX mgr (WiFiManager): WiFi manager to be used to connect
            XXX ssid (str): WiFi SSID of the LiftSystem
            XXX psk (str): WiFi pre-shared key of the LiftSystem
            interface (str): Network interface to be used by WireGuard (like wg0)
            self_address (str): WireGuard's IP address with subnet mask
            self_private_key (str): WireGuard's private key
            peer_endpoint (str): WireGuard peer's endpoint host/IP address and port
            peer_public_key (str): WireGuard peer's endpoint public key
            peer_allowed_ips (str): Routed IP network
        """

        # self.mgr = mgr
        # self.wifi = WiFi(ssid, psk)
        self.interface = interface
        self.self_address = self_address
        self.self_private_key = self_private_key
        self.peer_endpoint = peer_endpoint
        self.peer_public_key = peer_public_key
        self.peer_allowed_ips = peer_allowed_ips

    def _write_config(self):
        """Create and dump a WireGuard configuration file into /etc/wireguard/"""

        content = """\
        [Interface]
        Address = {address}
        PrivateKey = {private_key}

        [Peer]
        Endpoint = {endpoint}
        PublicKey = {endpoint_public_key}
        AllowedIPs = {allowed_ips}
        """.format(
                address=self.self_address,
                private_key=self.self_private_key,
                endpoint=self.peer_endpoint,
                endpoint_public_key=self.peer_public_key,
                allowed_ips=self.peer_allowed_ips)

        config_path = "/etc/wireguard/{}.conf".format(self.interface)

        with open(config_path, "w") as cfg:
            cfg.write(textwrap.dedent(content))

        logger.debug("Wrote WireGuard config to {}".format(config_path))

    def _wg_quick(self, action):
        """Start or stop a WireGuard connection by calling wg-quick

        Args:
            action <- {up, down}
        """

        cmd = ["wg-quick", action, self.interface]
        logger.debug("Launching WireGuard: {}".format(" ".join(cmd)))

        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        p.wait()
        stderr = p.stderr.read()

        if p.returncode != 0:
            raise WireGuardException("wg-quick failed, returned {}: {}".format(
                p.returncode, stderr.decode()))

    def up(self):
        """Starts the WireGuard VPN connection"""
        self._write_config()
        self._wg_quick("up")

        logger.info("Started WireGuard's {}".format(self.interface))

    def down(self):
        """Stops the WireGuard VPN connection"""
        self._wg_quick("down")

        logger.info("Stopped WireGuard's {}".format(self.interface))


if __name__ == '__main__':
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())

    wg = WireGuard(
            "wg0",
            "10.23.23.2/24", "iAJgg3wWJ5Szm1S6RCRop7BXUXezGEZcB2OfQxQVd34=",
            "10.0.1.172:51820", "IkE8N08w8rDPKyeMN6juIOiLoBHMHw4Gv+J17l3lkHw=",
            "10.23.23.0/24")
    wg.up()

    p = subprocess.Popen(["ip", "addr", "show", wg.interface], stdout=subprocess.PIPE)
    logger.info(p.stdout.read())

    time.sleep(10)

    wg.down()
