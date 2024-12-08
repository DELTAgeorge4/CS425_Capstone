// Code heavily modified/adapted from code on https://www.devdungeon.com/content/using-libpcap-c

#include <stdlib.h>
#include <stdio.h>
#include <pcap.h>
#include <string.h>

#define ETHERTYPES "ethertype_data.csv"

void display_devices(pcap_if_t*);
int print_device_info(char*);
char* select_device(pcap_if_t*);

void display_devices(pcap_if_t *devices){
    pcap_if_t *current_device = devices;
    int i = 1;
    while(current_device != NULL){
        printf("%d: Device name: %s\n", i, current_device->name);
        fflush(stdout);
        printf("Description: ");
        fflush(stdout);
        if (current_device->description){
            printf("%s\n", current_device->description);
        } else {
            printf("No description available\n");
        }
        fflush(stdout);
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

char* select_device(pcap_if_t* devs){
    display_devices(devs);

    printf("Enter the number for the device you would like to get information about: ");
    fflush(stdout);
    int choice;
    scanf("%d", &choice);

    pcap_if_t *chosen_dev = devs;
    for (int i = 1; i < choice; i++){
        chosen_dev = chosen_dev->next;
    }
    printf("%s\n", chosen_dev->name);
    fflush(stdout);
    return chosen_dev->name;
}

int main(void) {
    char ebuf[PCAP_ERRBUF_SIZE];
    pcap_if_t *devs;

    pcap_findalldevs(&devs, ebuf);

    char* device = select_device(devs);

    int status = print_device_info(device);
    if (status == 1){
        return 1;
    }

    exit(EXIT_SUCCESS);
}