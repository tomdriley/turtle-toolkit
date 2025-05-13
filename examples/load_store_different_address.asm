start:
    SET 1
    PUT DOFF    ; Addr <= 0x001
    STORE       ; Store 0x01 @ Addr 0x001
    SET 0
    PUT DOFF    ; Addr <= 0x000
    STORE       ; Store 0x00 @ Addr 0x000
    SET 1
    PUT DOFF    ; Addr <= 0x001
    SET 0x0A
    LOAD        ; Load from Addr 0x001
    HALT