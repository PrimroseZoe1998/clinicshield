from pathlib import Path

import pytest

from clinicshield.ingest import InputError
from clinicshield.nmap_input import read_nmap


LAB_SCAN = (
    Path(__file__).resolve().parents[1] / "samples" / "lab_scan.xml"
)


def scan_xml(
    *,
    address="192.0.2.2",
    address_type="ipv4",
    host_state="up",
    port="8080",
    protocol="tcp",
    port_state="open",
    service_xml='<service name="http"/>',
):
    return f"""
    <nmaprun scanner="nmap">
      <host>
        <status state="{host_state}"/>
        <address addr="{address}" addrtype="{address_type}"/>
        <ports>
          <port protocol="{protocol}" portid="{port}">
            <state state="{port_state}"/>
            {service_xml}
          </port>
        </ports>
      </host>
    </nmaprun>
    """.encode("utf-8")


def test_reads_saved_lab_scan():
    records = read_nmap(LAB_SCAN.read_bytes(), authorized=True)
    assert len(records) == 1
    record = records[0]
    assert record.host == "192.0.2.2"
    assert record.asset_id == "192.0.2.2"
    assert record.port == 8080
    assert record.service == "http"
    assert record.product == "SimpleHTTPServer"
    assert record.version == "0.6"
    assert record.exposure == "unknown"


def test_requires_authorization_by_default():
    with pytest.raises(InputError, match="Confirm"):
        read_nmap(scan_xml())


@pytest.mark.parametrize("authorized", [False, None, 1, "yes"])
def test_requires_explicit_boolean_authorization(authorized):
    with pytest.raises(InputError, match="Confirm"):
        read_nmap(scan_xml(), authorized=authorized)


def test_rejects_non_bytes_input():
    with pytest.raises(InputError, match="as bytes"):
        read_nmap("text", authorized=True)


@pytest.mark.parametrize(
    "data",
    [
        b"",
        b"<nmaprun",
        b"<other/>",
        b'<nmaprun scanner="other"/>',
    ],
)
def test_rejects_invalid_scan_documents(data):
    with pytest.raises(InputError):
        read_nmap(data, authorized=True)


def test_accepts_normal_nmap_doctype():
    data = b"<!DOCTYPE nmaprun>" + scan_xml()
    assert len(read_nmap(data, authorized=True)) == 1


def test_rejects_entity_expansion():
    data = b"""
    <!DOCTYPE nmaprun [
      <!ENTITY secret "PRIVATE_SENTINEL">
    ]>
    <nmaprun scanner="nmap">&secret;</nmaprun>
    """
    with pytest.raises(InputError) as error:
        read_nmap(data, authorized=True)
    assert "PRIVATE_SENTINEL" not in str(error.value)


def test_rejects_external_entities():
    data = b"""
    <!DOCTYPE nmaprun [
      <!ENTITY external SYSTEM "file:///nonexistent-clinicshield-test">
    ]>
    <nmaprun scanner="nmap">&external;</nmaprun>
    """
    with pytest.raises(InputError, match="safe Nmap XML"):
        read_nmap(data, authorized=True)


@pytest.mark.parametrize("state", ["closed", "filtered", "open|filtered"])
def test_includes_only_confirmed_open_ports(state):
    assert read_nmap(
        scan_xml(port_state=state), authorized=True
    ) == []


def test_skips_down_hosts():
    assert read_nmap(
        scan_xml(host_state="down"), authorized=True
    ) == []


def test_accepts_ipv6_hosts():
    records = read_nmap(
        scan_xml(address="2001:db8::2", address_type="ipv6"),
        authorized=True,
    )
    assert records[0].host == "2001:db8::2"


def test_rejects_host_without_ip_address():
    with pytest.raises(InputError, match="missing its IP address"):
        read_nmap(
            scan_xml(address="00:11:22:33:44:55", address_type="mac"),
            authorized=True,
        )


def test_rejects_invalid_ip_without_exposing_it():
    with pytest.raises(InputError) as error:
        read_nmap(
            scan_xml(address="PRIVATE_SENTINEL"), authorized=True
        )
    assert "invalid IP address" in str(error.value)
    assert "PRIVATE_SENTINEL" not in str(error.value)


@pytest.mark.parametrize(
    "port,protocol",
    [("0", "tcp"), ("65536", "tcp"), ("abc", "tcp"), ("80", "icmp")],
)
def test_rejects_invalid_open_service_fields(port, protocol):
    with pytest.raises(InputError, match="port or protocol"):
        read_nmap(
            scan_xml(port=port, protocol=protocol),
            authorized=True,
        )


def test_accepts_udp_services():
    records = read_nmap(
        scan_xml(protocol="udp"), authorized=True
    )
    assert records[0].protocol == "udp"


@pytest.mark.parametrize(
    "name,expected",
    [
        ("ms-wbt-server", "rdp"),
        ("microsoft-ds", "smb"),
        ("netbios-ssn", "smb"),
        ("ssl/http", "https"),
        ("unrecognized-service", "other"),
    ],
)
def test_maps_service_names(name, expected):
    records = read_nmap(
        scan_xml(service_xml=f'<service name="{name}"/>'),
        authorized=True,
    )
    assert records[0].service == expected


def test_maps_http_with_ssl_tunnel():
    records = read_nmap(
        scan_xml(service_xml='<service name="http" tunnel="ssl"/>'),
        authorized=True,
    )
    assert records[0].service == "https"


def test_missing_banner_stays_unknown():
    records = read_nmap(
        scan_xml(service_xml=""), authorized=True
    )
    assert records[0].service == "other"
    assert records[0].product == ""
    assert records[0].version == "Unknown"
    assert records[0].exposure == "unknown"


def test_preserves_separate_open_services():
    data = b"""
    <nmaprun scanner="nmap">
      <host>
        <status state="up"/>
        <address addr="192.0.2.2" addrtype="ipv4"/>
        <ports>
          <port protocol="tcp" portid="22">
            <state state="open"/>
            <service name="ssh"/>
          </port>
          <port protocol="tcp" portid="443">
            <state state="open"/>
            <service name="https"/>
          </port>
        </ports>
      </host>
    </nmaprun>
    """
    records = read_nmap(data, authorized=True)
    assert [(record.port, record.service) for record in records] == [
        (22, "ssh"),
        (443, "https"),
    ]