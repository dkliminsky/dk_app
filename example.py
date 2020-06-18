from connect import DKConnect, build_commands

con = DKConnect()
while True:
    if con.find_and_connect():
        break

cmd = build_commands(con)

print("uid:", cmd.get_uid().hex())
print("name:", cmd.get_name())
print("software:", cmd.get_software_version())
print("hardware:", cmd.get_hardware_version())
print("license key:", cmd.get_license_key().hex())
print("access level:", cmd.get_access_level())

print("free mem:", cmd.get_free_mem())
print("voltage:", cmd.get_battery_voltage())
