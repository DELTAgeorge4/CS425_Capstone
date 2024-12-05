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
    struct ether_header *eth_header = (struct ether_header *) packet;

    printf("Destination MAC address: ");
    for(int i = 0; i < 6; i++){
        if (i == 5){
            printf("%02x", eth_header->ether_dhost[i]);
        } else {
            printf("%02x:", eth_header->ether_dhost[i]);
        }
    }
    printf("\n");

    printf("Source MAC address: ");
    for(int i = 0; i < 6; i++){
        if (i == 5){
            printf("%02x", eth_header->ether_shost[i]);
        } else {
            printf("%02x:", eth_header->ether_shost[i]);
        }
    }
    printf("\n");

    printf("EtherType: "); 
    printf("0x%04x\n", ntohs(eth_header->ether_type));

    printf("Raw packet data:\n");
    for (int i = 0; i < header->caplen; i++) {
        printf("%02x ", packet[i]);
        if ((i + 1) % 16 == 0){
            printf("\n"); // New line every 16 bytes
        }
    }
    printf("\n");
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
    int timeout_limit = 10000; /* In milliseconds */
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