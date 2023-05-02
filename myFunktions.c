#include <avr/io.h>
#include <string.h>
#include <stdlib.h>

#include "uart.h"
#include "adc.h"
#include "global.h"
#include "zyklus.h"
#include "myFunktions.h"
#include "EinAusgabeUSB.h"
#include "df.h"
#include "cc-lib.h"

int16_t histerese=0;
int8_t ereignisBremsen=0;

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

uint16_t  linearisierungAD(uint16_t analogwert, uint8_t cosAlpha){
		//Die Funktion linearisiert den Analogwert mittels einer Hyperbel 2. Ordnung
		//Bei schräger Projektion auf ein Wand kann der reale Abstand
		// durch ein Multiplikation mit dem cosinusAlpha bestimmt werden.
		// die Variable cosAlpha entspricht dem cosinusAlpha X 100, d.h. 0?= 100, 45?= 70

		//Grenzwert festlegen!!
		//(analogwert-B) darf nicht 0 oder negativ werden!!
		// guter 

		uint16_t  abstand = 0;		//Variabel erzeugen und initialisieren 
		if (analogwert > 100){
			analogwert = 100;
		}

		abstand=(A/(analogwert-B)*cosAlpha);
		
		abstand = abstand / 100; 	// 
		return abstand;				// Ergebnis zurückliefern,
}

int16_t ro(void){					//Kurzform von int16_t pReglerServoRechts(void)

	return y;
}
/*
int16_t pReglerServoRechts(void){
	//ausrichten an der rechten Wand mit P-Regler
	//Funktion y(e) = me + b   z

	//==>  Variable sind in der global.h u. global.c definiert!  <====
	//int16_t m1=67;			//float Operation vermeiden
	//int16_t m2=100;			//Divisor Steigung
	//mit m=m1/m2=0,67, bei +- 15cm vom Sollwert

	//int16_t b=0;				//Durchbruch durch die Y-Achse
	//int16_t e;				//e=Regelabweichung in cm
	//int16_t sollwert = 35;//Sollwert 45 cm
	
	//int16_t y;				//y=Stellgroeße / Winkel

	//bestimmen der Regelabweichung
	//z.B. Sollwert greade (35cm),	20cm volllinks, 50cm vollrechts
	
	return y;
}
*/

void akkuSpannungPruefen(uint16_t schwellWert){
//Prüfe die AkkuSpannung nur wenn das CrazyCar nicht fährt! 
// Alle LEDs blicken, wenn Akku-Spannung < schwellwert !!

}

void ledSchalterTest(void){

}

//Zur Ausgabe eingener Daten die Variable int16_t ausgabe1, ausgabe2, 
//ausgabe3, char ausgabeT[MAXTEXTA]; verwenden,
//bei den Variablen int16_t h1,h2,h3 erfolgt eine Mittelwertbildung über 500ms

//-------------------------------------------------------------------------

