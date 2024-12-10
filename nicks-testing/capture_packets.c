// Code heavily modified/adapted from code on https://www.devdungeon.com/content/using-libpcap-c

#include <stdlib.h>
#include <stdio.h>
#include <pcap.h>
#include <arpa/inet.h>
#include <string.h>
#include <netinet/in.h>
#include <netinet/if_ether.h>
#include <time.h>

#define ETHERTYPES "ethertype_data.csv"

void print_packet_info(const unsigned char *packet, struct pcap_pkthdr packet_header);
void find_ethertype(int ethertype_num, char* eth_name);
void my_packet_handler(unsigned char *args, const struct pcap_pkthdr *header, const unsigned char *packet);

void print_packet_info(const unsigned char *packet, struct pcap_pkthdr packet_header) {
    printf("Packet capture length: %d\n", packet_header.caplen);
    fflush(stdout);
    printf("Packet total length %d\n", packet_header.len);
    fflush(stdout);
}

void find_ethertype(int ethertype_num, char* eth_name){
    //https://en.wikipedia.org/wiki/Ethernet_frame used for info on parsing ethernet frames
    FILE* ether_file = fopen(ETHERTYPES, "r");
    if (!ether_file){
        printf("Error opening file\n");
        fflush(stdout);
        strcpy(eth_name, "NULL\0");
    }

    char line[1024];
    //char ethertype_name[200];
    strcpy(eth_name, "NULL\0");
    while (fgets(line, 1024, ether_file)){
        char *ethertype_range = strtok(line, ",");
        char *ethertype_description = strtok(NULL, ",");
        char *range = strchr(ethertype_range, '-');
        int eth_start;
        int eth_end;
        if (range){
            eth_start = atoi(ethertype_range);
            eth_end = atoi(range + 1);
        } else {
            eth_start = atoi(ethertype_range);
            eth_end = eth_start;
        }
        /*printf("Start: %d\n", eth_start);
        fflush(stdout);
        printf("End: %d\n", eth_end);
        fflush(stdout);
        printf("Description: %s\n", ethertype_description);
        fflush(stdout);*/

        if (ethertype_num >= eth_start){
            if (ethertype_num <= eth_end){
                strcpy(eth_name, ethertype_description);
            }
        }
    }
    fclose(ether_file);
}

void my_packet_handler(unsigned char *args, const struct pcap_pkthdr *header, const unsigned char *packet){
    struct ether_header *eth_header = (struct ether_header *) packet;

    printf("Destination MAC address: ");
    fflush(stdout);
    for(int i = 0; i < 6; i++){
        if (i == 5){
            printf("%02x", eth_header->ether_dhost[i]);
            fflush(stdout);
        } else {
            printf("%02x:", eth_header->ether_dhost[i]);
            fflush(stdout);
        }
    }
    printf("\n");
    fflush(stdout);

    printf("Source MAC address: ");
    fflush(stdout);
    for(int i = 0; i < 6; i++){
        if (i == 5){
            printf("%02x", eth_header->ether_shost[i]);
        } else {
            printf("%02x:", eth_header->ether_shost[i]);
        }
        fflush(stdout);
    }
    printf("\n");
    fflush(stdout);

    printf("EtherType: "); 
    fflush(stdout);
    printf("0x%04x\n", ntohs(eth_header->ether_type));
    fflush(stdout);
    unsigned int type_or_length = ntohs(eth_header->ether_type);
    char ethertype_name[200];
    find_ethertype(type_or_length, ethertype_name);
    if (type_or_length > 1536){
        printf("EtherType: %s", ethertype_name);
    } else if (type_or_length < 1500){
        printf("EtherType: Length value");
    } else {
        printf("EtherType: Invalid");
    }
    fflush(stdout);
    printf("\n");
    fflush(stdout);

    unsigned char fcs[5];
    fcs[4] = '\0';
    unsigned char payload[header->caplen - 17]; // 17 = length of ethernet header - null terminator
    payload[header->caplen - 16] = '\0';
    printf("Raw packet data:\n");
    fflush(stdout);
    for (int i = 0; i < header->caplen; i++) {
        printf("%02x ", packet[i]);
        fflush(stdout);

        // Saving payload and FCS
        /*if (i >= 14){
            if (i >= header->caplen - 4){
                fcs[i - header->caplen] = packet[i];
            } else {
                payload[i - 14] = packet[i];
            }
        }*/
    }

    printf("\n");
    fflush(stdout);
    unsigned char network_layer_packet[1024];
    for (int i = 14; i < header->caplen - 4; i++){
        break;
    }
    return;
}

int main(int argc, char *argv[]) {
    if (argc < 2){
        printf("Not enough arguments provided\n");
        fflush(stdout);
        return 1;
    } else if (argc > 2){
        printf("Too many arguments provided\n");
        fflush(stdout);
        return 1;
    }
    
    char* device = argv[1]; // device name should be given by user when running program

    // Open device for live capture 
    printf("Starting packet capture on %s...\n", device);
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
        fflush(stderr);
        printf("You may need root priveleges for packet capture on this device.\n");
        fflush(stdout);
        exit(EXIT_FAILURE);
    }
    packet = pcap_next(handle, &packet_header);

    if (packet == NULL) {
        printf("No packet found.\n");
        fflush(stdout);
        return 2;
    }

    /* Our function to output some info */
    print_packet_info(packet, packet_header);

    pcap_loop(handle, 100, my_packet_handler, NULL);
    pcap_close(handle);

    exit(EXIT_SUCCESS);
}