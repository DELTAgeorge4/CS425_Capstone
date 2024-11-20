// Code from Pawel Sosnowski on https://www.devdungeon.com/content/using-libpcap-c

#include <stdlib.h>
#include <stdio.h>
#include <pcap.h>

int main(void) {

char ebuf[PCAP_ERRBUF_SIZE];
pcap_if_t *devs;

pcap_findalldevs(&devs, ebuf);

for (int i = 0; devs[i] != NULL; i++){
    printf("%s", devs[i]->name);
}

printf("%s\n", devs->name);

exit(EXIT_SUCCESS);
}