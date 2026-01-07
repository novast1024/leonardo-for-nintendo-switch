#ifndef HORIPAD_H
#define HORIPAD_H

#include <HID.h>

#ifdef USBCON

class Horipad : PluggableUSBModule {
public:
    Horipad(void);
    void SendReport(void* data, int length);

protected:
    // Implementation of the PluggableUSBModule
    bool setup(USBSetup& setup);
    int getInterface(uint8_t* interfaceCount);
    int getDescriptor(USBSetup& setup);

private:
    uint8_t epType[1];
    uint8_t protocol;
    uint8_t idle;
};

#endif // USBCON

#endif