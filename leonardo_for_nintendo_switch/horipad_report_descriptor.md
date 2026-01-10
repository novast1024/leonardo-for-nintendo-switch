## HORIPAD for Nintendo Switch
### vid: 0F0D pid: 00C1

### HID Report Descriptor
```
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

0xC0,              // End Collection
```

### Tree Diagram
```
Usage Page 0x01 : Generic Desktop Controls
│
├─ Usage 0x05 : Game Pad
│
├─ Usage 0x39 : Hat Switch
│
├─ Usage 0x30 : X
├─ Usage 0x31 : Y
├─ Usage 0x32 : Z
└─ Usage 0x35 : Rz


Usage Page 0x09 : Button
│
├─ Usage 0x01 : Button 1
├─ Usage 0x02 : Button 2
├─ ...
└─ Usage 0x0E : Button 14
```

### 0. Button (Low Byte)
| Bit    | 0 | 1 | 2 | 3 | 4 | 5 | 6  | 7  |
|--------|---|---|---|---|---|---|----|----|
| Button | Y | B | A | X | L | R | ZL | ZR |

### 1. Button (High Byte)
| Bit    | 0     | 1    | 2  | 3  | 4    | 5       | 6 | 7 |
|--------|-------|------|----|----|------|---------|---|---|
| Button | Minus | Plus | LS | RS | HOME | Capture | - | - |

### 2. Hat Switch (POV)
| Value   | Direction  |            |
|---------|------------|------------|
| 0x0     | North      | Up         |
| 0x1     | North-East | Up-Right   |
| 0x2     | East       | Right      |
| 0x3     | South-East | Down-Right |
| 0x4     | South      | Down       |
| 0x5     | South-West | Down-Left  |
| 0x6     | West       | Left       |
| 0x7     | North-West | Up-Left    |
| 0x8-0xF | Null State | Center     |

### 3. X Axis (LX)
|  <  |  +  |  >  |
|:---:|:---:|:---:|
|  0  | 128 | 255 |

### 4. Y Axis (LY)
|  ^  |  +  |  v  |
|:---:|:---:|:---:|
|  0  | 128 | 255 |

### 5. Z Axis (RX)
|  <  |  +  |  >  |
|:---:|:---:|:---:|
|  0  | 128 | 255 |

### 6. Rx Axis (RY)
|  ^  |  +  |  v  |
|:---:|:---:|:---:|
|  0  | 128 | 255 |

### 7. Padding Byte
Constant (always 0)