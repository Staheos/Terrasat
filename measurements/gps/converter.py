import xml.etree.ElementTree as ET
from datetime import datetime

# Sample GPS data
gps_data = open("gps_data.txt").read()

# Parse data
entries = gps_data.strip().split('--- GPS Data ---')
parsed_points = []

for entry in entries:
    if "Timestamp" not in entry:
        continue
    lines = entry.strip().split('\n')
    timestamp_str = lines[0].split(": ", 1)[1].strip()
    date_str = [line for line in lines if line.startswith("Date:")][0].split(": ", 1)[1].strip()

    # Combine date and time to full ISO format
    full_timestamp = f"{date_str}T{timestamp_str}"
    iso_time = datetime.fromisoformat(full_timestamp).isoformat()

    lat_str = lines[2].split(": ", 1)[1].strip()
    lon_str = lines[3].split(": ", 1)[1].strip()

    lat_val, lat_dir = lat_str.split()
    lat = float(lat_val) if lat_dir == 'N' else -float(lat_val)

    lon_val, lon_dir = lon_str.split()
    lon = float(lon_val) if lon_dir == 'E' else -float(lon_val)

    parsed_points.append((lat, lon, iso_time))


# Build GPX XML
gpx = ET.Element("gpx", attrib={
    "version": "1.1",
    "creator": "Terrasat",
    "xmlns": "http://www.topografix.com/GPX/1/1",
    "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
    "xsi:schemaLocation": "http://www.topografix.com/GPX/1/1 "
                          "http://www.topografix.com/GPX/1/1/gpx.xsd"
})

trk = ET.SubElement(gpx, "trk")
name = ET.SubElement(trk, "name")
name.text = "GPS Track"
trkseg = ET.SubElement(trk, "trkseg")

for lat, lon, time in parsed_points:
    trkpt = ET.SubElement(trkseg, "trkpt", attrib={"lat": str(lat), "lon": str(lon)})
    ET.SubElement(trkpt, "time").text = time

# Save to .gpx file
tree = ET.ElementTree(gpx)
with open("gps.gpx", "wb") as f:
    tree.write(f, encoding="utf-8", xml_declaration=True)

print("✅ GPX file 'output.gpx' created successfully!")
