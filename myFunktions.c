#include <avr/io.h>

#include <string.h>

#include <stdlib.h>

#include <avr/interrupt.h>         //YF: Interrupt lib einbinden



#include "uart.h"

#include "adc.h"

#include "global.h"

#include "zyklus.h"

#include "myFunktions.h"

#include "EinAusgabeUSB.h"

#include "df.h"

#include "cc-lib.h"



//Alt

int16_t histerese = 0;

int8_t ereignisBremsen = 0;



/*##############################

 ########## Variablen ##########

###############################*/



int16_t diffabstand = 0;                      //YF V1.1: Umsetzung auf Global um Ausgabe zu ermöglichen

int16_t v = 0;                                                                      //YF V1.1: Geschwindigkeitsvariable Global

uint16_t countL = 0, countR = 0;   //YF V1.1: Geschwindigkeitszähler privat

int16_t vL = 0, vR = 0;                                             //YF V1.1: Radgeschwindigkeiten privat

uint32_t tstartL = 0, tstartR = 0, tReset = 0;   //YF V1.1: Startzeiten Messungen privat

int8_t ustell;      //V1.3 Stellgröße v-Regler


// <== Eigene Funktion und Bedingungen formulieren / schreiben
void fahren1(void) {
    servo(0);
	fahr(18);
    warte_sekunden(1);
	fahr(0);
	warte_sekunden(3);
}

void fahren2(void){

}

void uebung1(void){
	
}

void uebung2(void){

}

void uebung3(void){

}



/*###############################

 ########## V Regelung ##########

################################*/



// V1.3 Initialisierung V-Messung

void initVMessung(void) {

    DDRD &= ~((1 << PD3) | (1 << PD2));                            //YF: Als Input deklarieren INT0,1

    PORTD |= (1 << PD3) | (1 << PD2);                     //YF: Internen Pullup aktivieren

    MCUCR |= (1 << ISC11) | (1 << ISC01);             //YF: External Interrupt Failling Edge

    GICR |= (1 << INT1) | (1 << INT0);                  //YF: Aktivieren der externen Interrupts

}



//YF V1.1

void vMessung(void) {

    if (countL != 0) {

        int16_t trad = datenSatzZaehler - tstartL;       //YF Berechne vergangene Zeit

        vL = (double)(countL * 100) / (double)(trad * 2);         //YF Berechne Halbe Radgeschwindigkeit in cm/s

        tstartL = datenSatzZaehler;                            //YF Setze Zeit zurück

        countL = 0;                                                                                             //YF Setze Zähler zurück

        tReset = datenSatzZaehler;                                                                                       //YF Reset falls v=0

    }

    if (countR != 0) {

        int16_t trad = datenSatzZaehler - tstartR;//YF Berechne vergangene Zeit

        vR = (double)(countR * 100) / (double)(trad * 2);        //YF Berechne Halbe Radgeschwindigkeit in cm/s

        tstartR = datenSatzZaehler;                            //YF Setze Zeit zurück

        countR = 0;                                                                                            //YF Setze Zähler zurück

        tReset = datenSatzZaehler;                                                                                       //YF Reset falls v=0

    }

    // Falls letzte v-Messung lange her, setze zurück (alle 200ms->4cm/200ms=v<20cm/s)

    if ((tReset - datenSatzZaehler) > 20) {

        vR = 0;

        vL = 0;

    }

    v = vR + vL;              //YF Berechne Mittelwert

}



//YF V1.1: Zähle 4cm hoch, wenn Magnet detektiert

ISR(INT0_vect) {

    countL += 4;

}

//YF V1.1: Zähle 4cm hoch, wenn Magnet detektiert

ISR(INT1_vect) {

    countR += 4;

}