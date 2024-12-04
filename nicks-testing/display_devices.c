#include <pcap.h>

int main(){
    char ebuf[PCAP_ERRBUF_SIZE];
    pcap_if_t *devices;

    pcap_findalldevs(&devices, ebuf);
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