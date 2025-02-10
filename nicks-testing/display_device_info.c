// Code heavily modified/adapted from code on https://www.devdungeon.com/content/using-libpcap-c

#include <stdlib.h>
#include <stdio.h>
#include <pcap.h>
#include <string.h>

int print_device_info(char*);

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
        fflush(stdout);
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
    fflush(stdout);
    printf("IP address: %s\n", ip_address);
    fflush(stdout);
    printf("Subnet mask: %s\n", subnet_mask);
    fflush(stdout);
    return 0;
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

    char* device = argv[1];

    int status = print_device_info(device);
    if (status == 1){
        return 1;
    }

    exit(EXIT_SUCCESS);
}