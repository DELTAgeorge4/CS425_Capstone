#include <stdio.h>
#include <stdlib.h>
#include <libpq-fe.h>

#define DB_NAME "suricata" //Don't know if null terminator is needed

int main(){
    printf(DB_NAME);
    return 0;
}