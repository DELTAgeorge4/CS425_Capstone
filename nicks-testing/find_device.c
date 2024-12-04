// Code heavily modified/adapted from code on https://www.devdungeon.com/content/using-libpcap-c

#include <stdlib.h>
#include <stdio.h>
#include <pcap.h>
#include <arpa/inet.h>
#include <string.h>
#include <netinet/in.h>
#include <netinet/if_ether.h>
#include <time.h>

void display_devices(pcap_if_t*);
int print_device_info(char*);
char* select_device(pcap_if_t*);
void print_packet_info(const unsigned char *packet, struct pcap_pkthdr packet_header);
void my_packet_handler(unsigned char *args, const struct pcap_pkthdr *header, const unsigned char *packet);

void display_devices(pcap_if_t *devices){
    pcap_if_t *current_device = devices;

    int i = 1;
    while(current_device != NULL){
        printf("%d: Device name: %s\n", i, current_device->name);
        printf("Description: ");
        if (current_device->description){
            printf("%s\n", current_device->description);
        } else {
            printf("No description available\n");
        }
        current_device = current_device->next;
        i++;
    }
}

int print_device_info(char* device_name){
    char error_buffer[PCAP_ERRBUF_SIZE];
    char ip_address[13];
    char subnet_mask[13];

    bpf_u_int32 ip_raw; /* IP address as integer */
    bpf_u_int32 subnet_mask_raw; /* Subnet mask as integer */

    int lookup_return_code;
    lookup_return_code = pcap_lookupnet(
        device_name,
        &ip_raw,
        &subnet_mask_raw,
        error_buffer
    );
    if (lookup_return_code == -1) {
        printf("%s\n", error_buffer);
        return 1;
    }
    struct in_addr address;
    address.s_addr = ip_raw;
    strcpy(ip_address, inet_ntoa(address));
    if (ip_address == NULL) {
        perror("inet_ntoa"); /* print error */
        return 1;
    }
    address.s_addr = subnet_mask_raw;
    strcpy(subnet_mask, inet_ntoa(address));
    if (subnet_mask == NULL) {
        perror("inet_ntoa");
        return 1;
    }

    printf("Device: %s\n", device_name);
    printf("IP address: %s\n", ip_address);
    printf("Subnet mask: %s\n", subnet_mask);
    return 0;
}

char* select_device(pcap_if_t* devs){
    display_devices(devs);

    printf("Enter the number for the device you would like to get information about: ");
    int choice;
    scanf("%d", &choice);

    pcap_if_t *chosen_dev = devs;
    for (int i = 1; i < choice; i++){
        chosen_dev = chosen_dev->next;
    }
    printf("%s\n", chosen_dev->name);
    return chosen_dev->name;
}

void print_packet_info(const unsigned char *packet, struct pcap_pkthdr packet_header) {
    printf("Packet capture length: %d\n", packet_header.caplen);
    printf("Packet total length %d\n", packet_header.len);
}

void my_packet_handler(unsigned char *args, const struct pcap_pkthdr *header, const unsigned char *packet){
    /* First, lets make sure we have an IP packet */
    struct ether_header *eth_header;
    eth_header = (struct ether_header *) packet;
    if (ntohs(eth_header->ether_type) != ETHERTYPE_IP) {
        printf("Not an IP packet. Skipping...\n\n");
        return;
    }

    /* The total packet length, including all headers
       and the data payload is stored in
       header->len and header->caplen. Caplen is
       the amount actually available, and len is the
       total packet length even if it is larger
       than what we currently have captured. If the snapshot
       length set with pcap_open_live() is too small, you may
       not have the whole packet. */
    printf("Total packet available: %d bytes\n", header->caplen);
    printf("Expected packet size: %d bytes\n", header->len);

    /* Pointers to start point of various headers */
    const unsigned char *ip_header;
    const unsigned char *tcp_header;
    const unsigned char *payload;

    /* Header lengths in bytes */
    int ethernet_header_length = 14; /* Doesn't change */
    int ip_header_length;
    int tcp_header_length;
    int payload_length;

    /* Find start of IP header */
    ip_header = packet + ethernet_header_length;
    /* The second-half of the first byte in ip_header
       contains the IP header length (IHL). */
    ip_header_length = ((*ip_header) & 0x0F);
    /* The IHL is number of 32-bit segments. Multiply
       by four to get a byte count for pointer arithmetic */
    ip_header_length = ip_header_length * 4;
    printf("IP header length (IHL) in bytes: %d\n", ip_header_length);

    /* Now that we know where the IP header is, we can 
       inspect the IP header for a protocol number to 
       make sure it is TCP before going any further. 
       Protocol is always the 10th byte of the IP header */
    unsigned char protocol = *(ip_header + 9);
    if (protocol != IPPROTO_TCP) {
        printf("Not a TCP packet. Skipping...\n\n");
        return;
    }

    /* Add the ethernet and ip header length to the start of the packet
       to find the beginning of the TCP header */
    tcp_header = packet + ethernet_header_length + ip_header_length;
    /* TCP header length is stored in the first half 
       of the 12th byte in the TCP header. Because we only want
       the value of the top half of the byte, we have to shift it
       down to the bottom half otherwise it is using the most 
       significant bits instead of the least significant bits */
    tcp_header_length = ((*(tcp_header + 12)) & 0xF0) >> 4;
    /* The TCP header length stored in those 4 bits represents
       how many 32-bit words there are in the header, just like
       the IP header length. We multiply by four again to get a
       byte count. */
    tcp_header_length = tcp_header_length * 4;
    printf("TCP header length in bytes: %d\n", tcp_header_length);

    /* Add up all the header sizes to find the payload offset */
    int total_headers_size = ethernet_header_length+ip_header_length+tcp_header_length;
    printf("Size of all headers combined: %d bytes\n", total_headers_size);
    payload_length = header->caplen -
        (ethernet_header_length + ip_header_length + tcp_header_length);
    printf("Payload size: %d bytes\n", payload_length);
    payload = packet + total_headers_size;
    printf("Memory address where payload begins: %p\n\n", payload);

    /* Print payload in ASCII */
      
    if (payload_length > 0) {
        const unsigned char *temp_pointer = payload;
        int byte_count = 0;
        while (byte_count++ < payload_length) {
            printf("%c", *temp_pointer);
            temp_pointer++;
        }
        printf("\n");
    }
    
    return;
}

int main(void) {
    char ebuf[PCAP_ERRBUF_SIZE];
    pcap_if_t *devs;

    pcap_findalldevs(&devs, ebuf);

    char* device = select_device(devs);

    //memset(ebuf, 0, sizeof(ebuf)); // clear error buffer

    int status = print_device_info(device);
    if (status == 1){
        return 1;
    }
    
    // Open device for live capture 
    char error_buffer[PCAP_ERRBUF_SIZE];
    int total_packet_count = 200;
    int packet_count_limit = 0;
    int timeout_limit = 100000; /* In milliseconds */
    pcap_t *handle;
    int snapshot_length = 1024;
    handle = pcap_open_live(
        device,
        snapshot_length,
        packet_count_limit,
        timeout_limit,
        error_buffer
    );

    const unsigned char *packet; //u_char is used in linux instead, so maybe change for linux systems
    struct pcap_pkthdr packet_header;
    if (handle == NULL) {
        fprintf(stderr, "Failed to initialize pcap handle.\n");
        printf("You may need root priveleges for packet capture on this device.\n");
        exit(EXIT_FAILURE);
    }
    packet = pcap_next(handle, &packet_header);

    if (packet == NULL) {
        printf("No packet found.\n");
        return 2;
    }

    /* Our function to output some info */
    print_packet_info(packet, packet_header);

    pcap_loop(handle, 100, my_packet_handler, NULL);
    pcap_close(handle);

    return 0;

    exit(EXIT_SUCCESS);
}