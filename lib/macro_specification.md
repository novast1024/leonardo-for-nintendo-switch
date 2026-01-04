
## structure (code: 0x01, 0x02)

- loop begin + loop count (varint)
- loop end

| Code |                |
|------|----------------|
| 0x01 | Loop Begin     |
| 0x02 | Loop End       |

## reserved report (code: 0x10-0x36)

- code + delta time (varint)

| Code |                |                         |
|------|----------------|-------------------------|
| 0x10 | Netural        | 00 00 08 80 80 80 80 00 |
| 0x11 | Y              | 01 00 08 80 80 80 80 00 |
| 0x12 | B              | 02 00 08 80 80 80 80 00 |
| 0x13 | A              | 04 00 08 80 80 80 80 00 |
| 0x14 | X              | 08 00 08 80 80 80 80 00 |
| 0x15 | L              | 10 00 08 80 80 80 80 00 |
| 0x16 | R              | 20 00 08 80 80 80 80 00 |
| 0x17 | ZL             | 40 00 08 80 80 80 80 00 |
| 0x18 | ZR             | 80 00 08 80 80 80 80 00 |
| 0x19 | Minus          | 00 01 08 80 80 80 80 00 |
| 0x1a | Plus           | 00 02 08 80 80 80 80 00 |
| 0x1b | LS             | 00 04 08 80 80 80 80 00 |
| 0x1c | RS             | 00 08 08 80 80 80 80 00 |
| 0x1d | HOME           | 00 10 08 80 80 80 80 00 |
| 0x1e | Capture        | 00 20 08 80 80 80 80 00 |
| 0x1f | Hat Up         | 00 00 00 80 80 80 80 00 |
| 0x20 | Hat Up-Right   | 00 00 01 80 80 80 80 00 |
| 0x21 | Hat Right      | 00 00 02 80 80 80 80 00 |
| 0x22 | Hat Down-Right | 00 00 03 80 80 80 80 00 |
| 0x23 | Hat Down       | 00 00 04 80 80 80 80 00 |
| 0x24 | Hat Down-Left  | 00 00 05 80 80 80 80 00 |
| 0x25 | Hat Left       | 00 00 06 80 80 80 80 00 |
| 0x26 | Hat Up-Left    | 00 00 07 80 80 80 80 00 |
| 0x27 | LS Up          | 00 00 08 80 00 80 80 00 |
| 0x28 | LS Up-Right    | 00 00 08 DA 25 80 80 00 |
| 0x29 | LS Right       | 00 00 08 FF 80 80 80 00 |
| 0x2a | LS Down-Right  | 00 00 08 DA DA 80 80 00 |
| 0x2b | LS Down        | 00 00 08 80 FF 80 80 00 |
| 0x2c | LS Down-Left   | 00 00 08 25 DA 80 80 00 |
| 0x2d | LS Left        | 00 00 08 00 80 80 80 00 |
| 0x2e | LS Up-Left     | 00 00 08 25 25 80 80 00 |
| 0x2f | RS Up          | 00 00 08 80 80 80 00 00 |
| 0x30 | RS Up-Right    | 00 00 08 80 80 DA 25 00 |
| 0x31 | RS Right       | 00 00 08 80 80 FF 80 00 |
| 0x32 | RS Down-Right  | 00 00 08 80 80 DA DA 00 |
| 0x33 | RS Down        | 00 00 08 80 80 80 FF 00 |
| 0x34 | RS Down-Left   | 00 00 08 80 80 25 DA 00 |
| 0x35 | RS Left        | 00 00 08 80 80 00 80 00 |
| 0x36 | RS Up-Left     | 00 00 08 80 80 25 25 00 |


### diff from neutral report (code: 0x80 - 0xFF)

- code + delta bytes + delta time (varint)

#### code
| 7 | 6  | 5  | 4  | 3  | 2   | 1        | 0       |
|---|----|----|----|----|-----|----------|---------|
| 1 | RY | RX | LY | LX | Hat | Btn High | Btn Low |

#### e.g.
- `0xFF <Btn Low> <Btn High> <Hat> <LX> <LY> <RX> <RY> <delta time>`
- `0x81 <Btn Low> <delta time>`