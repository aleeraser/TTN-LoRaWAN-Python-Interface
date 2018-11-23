
// MIT License
// https://github.com/gonzalocasas/arduino-uno-dragino-lorawan/blob/master/LICENSE
// Based on examples from https://github.com/matthijskooijman/arduino-lmic
// Copyright (c) 2015 Thomas Telkamp and Matthijs Kooijman

#include <hal/hal.h>
#include <lmic.h>

#ifdef CREDENTIALS
static u1_t NWKSKEY[16] = NWKSKEY1;
static u1_t APPSKEY[16] = APPSKEY1;
static u4_t DEVADDR = DEVADDR1;
#else
static u1_t NWKSKEY[16] = {0xBB, 0x48, 0x59, 0xA5, 0x09, 0x29, 0x57, 0x3A, 0x6F, 0xD2, 0x42, 0x73, 0xBD, 0x17, 0xEC, 0x3D};
static u1_t APPSKEY[16] = {0x90, 0x93, 0x9A, 0x46, 0x08, 0xA7, 0x42, 0x77, 0x6B, 0x00, 0x6D, 0x45, 0x6A, 0x77, 0x81, 0x14};
static u4_t DEVADDR = 0x260117BD;
#endif

// These callbacks are only used in over-the-air activation, so they are
// left empty here (we cannot leave them out completely unless
// DISABLE_JOIN is set in config.h, otherwise the linker will complain).
void os_getArtEui(u1_t *buf) {}
void os_getDevEui(u1_t *buf) {}
void os_getDevKey(u1_t *buf) {}

static osjob_t sendjob;

// Schedule TX every this many seconds (might become longer due to duty
// cycle limitations).
const unsigned TX_INTERVAL = 3;

// Pin mapping Dragino Shield
const lmic_pinmap lmic_pins = {
    .nss = 10,
    .rxtx = LMIC_UNUSED_PIN,
    .rst = 9,
    .dio = {2, 6, 7},
};
void onEvent(ev_t ev) {
    if (ev == EV_TXCOMPLETE) {
        Serial.println(F("EV_TXCOMPLETE (includes waiting for RX windows)"));
        // Schedule next transmission
        os_setTimedCallback(&sendjob, os_getTime() + sec2osticks(TX_INTERVAL), do_send);
    }
}

int msg_counter = 0;

void do_send(osjob_t *j) {
    // Payload to send (uplink)
    // static uint8_t message[] = "Hello, World!";
    String s = String(msg_counter);
    static uint8_t message[10];
    s.toCharArray((char *)message, 10);
    msg_counter++;

    // Check if there is not a current TX/RX job running
    if (LMIC.opmode & OP_TXRXPEND) {
        Serial.println(F("OP_TXRXPEND, not sending"));
    } else {
        // Prepare upstream data transmission at the next possible time.
        LMIC_setTxData2(1, message, sizeof(message) - 1, 0);
        Serial.println(F("Sending uplink packet..."));
    }
    // Next TX is scheduled after TX_COMPLETE event.
}

void setup() {
    Serial.begin(115200);
    Serial.println(F("Starting..."));

    // LMIC init
    os_init();

    // Reset the MAC state. Session and pending data transfers will be discarded.
    LMIC_reset();

    // Set static session parameters.
    LMIC_setSession(0x1, DEVADDR, NWKSKEY, APPSKEY);

    LMIC_setupChannel(0, 434000000, DR_RANGE_MAP(DR_SF12, DR_SF7), BAND_CENTI);
    LMIC_setupChannel(1, 434000000, DR_RANGE_MAP(DR_SF12, DR_SF7), BAND_CENTI);
    LMIC_setupChannel(2, 434000000, DR_RANGE_MAP(DR_SF12, DR_SF7), BAND_CENTI);
    LMIC_setupChannel(3, 434000000, DR_RANGE_MAP(DR_SF12, DR_SF7), BAND_CENTI);

    // Disable link check validation
    LMIC_setLinkCheckMode(0);

    // TTN uses SF9 for its RX2 window.
    LMIC.dn2Dr = DR_SF7;

    // Set data rate and transmit power for uplink (note: txpow seems to be ignored by the library)
    LMIC_setDrTxpow(DR_SF7, 14);

    // Start job
    do_send(&sendjob);
}

void loop() {
    os_runloop_once();
}
