// Code heavily modified/adapted from code on https://www.devdungeon.com/content/using-libpcap-c

#include <stdlib.h>
#include <stdio.h>
#include <pcap.h>
#include <string.h>

#define ETHERTYPES "ethertype_data.csv"

void display_devices(pcap_if_t*);
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


/*char* select_device(pcap_if_t* devs){
    display_devices(devs);

    printf("Enter the number for the device you would like to get information about: \n");
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
}*/

int main(void) {
    char ebuf[PCAP_ERRBUF_SIZE];
    pcap_if_t *devs;

    pcap_findalldevs(&devs, ebuf);

    display_devices(devs);

    return 0;
}