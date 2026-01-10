#include "horipad.h"

#ifdef USBCON

static const uint8_t HORIPAD_REPORT_DESCRIPTOR[] PROGMEM = {
    0x05, 0x01,        // Usage Page (Generic Desktop Ctrls)
    0x09, 0x05,        // Usage (Game Pad)
    0xA1, 0x01,        // Collection (Application)

    // --- Button 14 bits + 2 padding bits ---
    0x15, 0x00,        //   Logical Minimum (0)
    0x25, 0x01,        //   Logical Maximum (1)
    0x35, 0x00,        //   Physical Minimum (0)
    0x45, 0x01,        //   Physical Maximum (1)
    0x75, 0x01,        //   Report Size (1)
    0x95, 0x0E,        //   Report Count (14)
    0x05, 0x09,        //   Usage Page (Button)
    0x19, 0x01,        //   Usage Minimum (1)
    0x29, 0x0E,        //   Usage Maximum (14)
    0x81, 0x02,        //   Input (Data,Var,Abs)
    0x95, 0x02,        //   Report Count (2)
    0x81, 0x01,        //   Input (Const)

    // --- Hat Switch (POV) 4 bits + 4 padding bits ---
    0x05, 0x01,        //   Usage Page (Generic Desktop Ctrls)
    0x25, 0x07,        //   Logical Maximum (7)
    0x46, 0x3B, 0x01,  //   Physical Maximum (315)
    0x75, 0x04,        //   Report Size (4)
    0x95, 0x01,        //   Report Count (1)
    0x65, 0x14,        //   Unit (English Rotation, Degrees)
    0x09, 0x39,        //   Usage (Hat switch)
    0x81, 0x42,        //   Input (Data,Var,Abs,Null State)
    0x65, 0x00,        //   Unit (None)
    0x95, 0x01,        //   Report Count (1)
    0x81, 0x01,        //   Input (Const)

    // --- Axes (X, Y, Z, Rx) 32 bits ---
    0x26, 0xFF, 0x00,  //   Logical Maximum (255)
    0x46, 0xFF, 0x00,  //   Physical Maximum (255)
    0x09, 0x30,        //   Usage (X)
    0x09, 0x31,        //   Usage (Y)
    0x09, 0x32,        //   Usage (Z)
    0x09, 0x35,        //   Usage (Rz)
    0x75, 0x08,        //   Report Size (8)
    0x95, 0x04,        //   Report Count (4)
    0x81, 0x02,        //   Input (Data,Var,Abs)

    // --- 8 padding bits ---
    0x75, 0x08,        //   Report Size (8)
    0x95, 0x01,        //   Report Count (1)
    0x81, 0x01,        //   Input (Const)

    0xC0               // End Collection
};

bool Horipad::ready() {
    // IN endpoint ready: previous packet has been taken by the host (TXINI=1)

    // see USB Device Endpoint Registers in https://ww1.microchip.com/downloads/en/DeviceDoc/Atmel-7766-8-bit-AVR-ATmega16U4-32U4_Datasheet.pdf
    // UENUM - USB Endpoint Number Register
    // TXINI - Transmit IN Interrupt flag (Transmitter Ready Interrupt Flag)
    // UEINTX - USB Endpoint Interrupt Flags Register (X = selected endpoint)
    UENUM = pluggedEndpoint;
    return (UEINTX & (1 << TXINI));
}

void Horipad::SendReport(void* data, int length) {
    USB_Send(pluggedEndpoint | TRANSFER_RELEASE, data, length); // see USBCore.cpp
}

Horipad::Horipad(void) : PluggableUSBModule(1, 1, epType),
    protocol(HID_REPORT_PROTOCOL), idle(1) {
	epType[0] = EP_TYPE_INTERRUPT_IN;
	PluggableUSB().plug(this);
}

bool Horipad::setup(USBSetup& setup) {
	if (pluggedInterface != setup.wIndex) {
		return false;
	}

	uint8_t request = setup.bRequest;
	uint8_t requestType = setup.bmRequestType;

	if (requestType == REQUEST_DEVICETOHOST_CLASS_INTERFACE) {
		if (request == HID_GET_REPORT) {
			// TODO: HID_GetReport();
			return true;
		}
		if (request == HID_GET_PROTOCOL) {
			// TODO: Send8(protocol);
			return true;
		}
        if (request == HID_GET_IDLE) {
            // TODO: Send8(idle);
        }
	}

	if (requestType == REQUEST_HOSTTODEVICE_CLASS_INTERFACE) {
		if (request == HID_SET_PROTOCOL) {
			protocol = setup.wValueL;
			return true;
		}
		if (request == HID_SET_IDLE) {
			idle = setup.wValueH;
			return true;
		}
		if (request == HID_SET_REPORT) {
			//uint8_t reportID = setup.wValueL;
			//uint16_t length = setup.wLength;
			//uint8_t data[length];
			// Make sure to not read more data than USB_EP_SIZE.
			// You can read multiple times through a loop.
			// The first byte (may!) contain the reportID on a multreport.
			//USB_RecvControl(data, length);
		}
	}

	return false;
}

int Horipad::getInterface(uint8_t* interfaceCount) {
	*interfaceCount += 1; // uses 1
	HIDDescriptor hidInterface = {
		D_INTERFACE(pluggedInterface, 1, USB_DEVICE_CLASS_HUMAN_INTERFACE, HID_SUBCLASS_NONE, HID_PROTOCOL_NONE),
		D_HIDREPORT(sizeof(HORIPAD_REPORT_DESCRIPTOR)),
		D_ENDPOINT(USB_ENDPOINT_IN(pluggedEndpoint), USB_ENDPOINT_TYPE_INTERRUPT, USB_EP_SIZE, 0x01)
	};
	return USB_SendControl(0, &hidInterface, sizeof(hidInterface));
}

int Horipad::getDescriptor(USBSetup& setup) {
	// Check if this is a HID Class Descriptor request
	if (setup.bmRequestType != REQUEST_DEVICETOHOST_STANDARD_INTERFACE) { return 0; }
	if (setup.wValueH != HID_REPORT_DESCRIPTOR_TYPE) { return 0; }

	// In a HID Class Descriptor wIndex cointains the interface number
	if (setup.wIndex != pluggedInterface) { return 0; }

	// Reset the protocol on reenumeration. Normally the host should not assume the state of the protocol
	// due to the USB specs, but Windows and Linux just assumes its in report mode.
	protocol = HID_REPORT_PROTOCOL;

    return USB_SendControl(TRANSFER_PGM, HORIPAD_REPORT_DESCRIPTOR, sizeof(HORIPAD_REPORT_DESCRIPTOR));
}

#endif // USBCON
