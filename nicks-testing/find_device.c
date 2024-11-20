#include <stdlib.h>
#include <stdio.h>
#include <pcap.h>

int main(void) {

char ebuf[PCAP_ERRBUF_SIZE];
pcap_if_t *devs;

pcap_findalldevs(&devs, ebuf);

printf("%s\n", devs->name);

exit(EXIT_SUCCESS);
}