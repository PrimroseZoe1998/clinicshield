from pathlib import Path

from defusedxml import ElementTree as ET


def test_lab_scan_contains_expected_host_and_service():
    project = Path(__file__).resolve().parents[1]
    root = ET.parse(project / "samples" / "lab_scan.xml").getroot()

    assert root.tag == "nmaprun"

    hosts = root.findall("host")
    assert len(hosts) == 1

    host = hosts[0]
    assert host.find("status").get("state") == "up"
    assert host.find("address[@addrtype='ipv4']").get("addr") == "192.0.2.2"

    open_ports = [
        port
        for port in host.findall("ports/port")
        if port.find("state").get("state") == "open"
    ]
    assert len(open_ports) == 1

    port = open_ports[0]
    assert port.get("protocol") == "tcp"
    assert port.get("portid") == "8080"
    assert port.find("service").get("name") == "http"
    assert port.find("service").get("product") == "SimpleHTTPServer"