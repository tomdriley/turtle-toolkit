; --- Large Multiplication Benchmark (A * B = Result_High:Result_Low) ---
; Multiplicand (A) in R3
; Multiplier (B) in R0 (used as counter)
; Result Low Byte in R1
; Result High Byte in R2

START_MUL:
; PC = 0 (Assuming program starts at address 0)
SET 0       ; ACC = 0 (Initialize Accumulator)
PUT R1      ; R1 = 0 (Initialize Result_Low)
PUT R2      ; R2 = 0 (Initialize Result_High)

; PC = 6
SET 200     ; ACC = 200 (Example Multiplicand A)
PUT R3      ; R3 = 200

; PC = 10
SET 100     ; ACC = 100 (Example Multiplier B)
PUT R0      ; R0 = 100 (Loop counter)

; --- Start Multiplication Loop ---
LOOP_MUL:
; PC = 14
GET R0      ; ACC = R0 (Get loop counter)
NOP         ; Set the status register from ACC
; PC = 16
; BZ offset = (END_MUL PC) - (Current PC)
; END_MUL is at PC=42. Offset = 42 - 16 = 26.
; This means if R0 is 0, jump to END_MUL.
BZ END_MUL  ; If R0 is 0, branch to END_MUL (PC + 26)
            ; This is a branch instruction that checks if the counter is zero.
            ; If it is, it jumps to the end of the multiplication.

; PC = 18
GET R1      ; ACC = R1 (Get Result_Low)
; PC = 20
ADD R3      ; ACC = ACC + R3 (Add Multiplicand A to Result_Low).
            ; This updates the Carry flag in the STATUS register.
; PC = 22
PUT R1      ; R1 = ACC (Store the new Result_Low).
            ; The low 8 bits of the sum are now in R1.

; PC = 24
; BCS offset = (INCREMENT_HIGH PC) - (Current PC)
; INCREMENT_HIGH is at PC=28. Offset = 28 - 24 = 4.
BCS INCREMENT_HIGH ; If Carry flag is set, branch to INCREMENT_HIGH (PC + 4)

; PC = 26
; If no carry from the low byte addition, jump to DECREMENT_COUNTER.
; JMPI offset = (DECREMENT_COUNTER PC) - (Current PC)
; DECREMENT_COUNTER is at PC=34. Offset = 34 - 26 = 8.
JMPI DECREMENT_COUNTER ; Jump to DECREMENT_COUNTER (PC + 8), skipping the carry handling block.

; --- Handle Carry: Increment Result_High ---
INCREMENT_HIGH:
; PC = 28
GET R2      ; ACC = R2 (Get Result_High)
; PC = 30
ADDI 1      ; ACC = ACC + 1 (Increment Result_High)
; PC = 32
PUT R2      ; R2 = ACC (Store the updated Result_High)

; --- Decrement Counter and Loop ---
DECREMENT_COUNTER:
; PC = 34
GET R0      ; ACC = Counter
; PC = 36
SUBI 1      ; ACC = ACC - 1
; PC = 38
PUT R0      ; R0 = ACC (Update Counter)

; PC = 40
; Jump back to start of loop (LOOP_MUL).
; JMPI offset = (LOOP_MUL PC) - (Current PC)
; LOOP_MUL is at PC=14. Offset = 14 - 40 = -26.
JMPI LOOP_MUL ; Jump back to LOOP_MUL (PC - 26)

; --- End of Multiplication ---
END_MUL:
; PC = 42
HALT        ; Stop execution.
            ; The 16-bit result of 200 * 100 = 20000 (0x4E20)
            ; should be in R2 (0x4E) and R1 (0x20).

; --- Calculated Branch/Jump Offsets ---
; BZ END_MUL at PC=16: Offset = (END_MUL PC) - 16 = 42 - 16 = 26
; BCS INCREMENT_HIGH at PC=24: Offset = (INCREMENT_HIGH PC) - 24 = 28 - 24 = 4 (Correct)
; JMPI DECREMENT_COUNTER at PC=26: Offset = (DECREMENT_COUNTER PC) - 26 = 34 - 26 = 8 (Correct)
; JMPI LOOP_MUL at PC=40: Offset = (LOOP_MUL PC) - 40 = 14 - 40 = -26 (Correct)

; The code with final offsets:
; START_MUL:
; SET 0
; PUT R1
; PUT R2
; SET 200
; PUT R3
; SET 100
; PUT R0
; LOOP_MUL:
; GET R0
; BZ 26         ; Jump to PC + 26 (END_MUL)
; GET R1
; ADD R3
; PUT R1
; BCS 4         ; Jump to PC + 4 (INCREMENT_HIGH)
; JMPI 8        ; Jump to PC + 8 (DECREMENT_COUNTER)
; INCREMENT_HIGH:
; GET R2
; ADDI 1
; PUT R2
; DECREMENT_COUNTER:
; GET R0
; SUBI 1
; PUT R0
; JMPI -26      ; Jump to PC - 26 (LOOP_MUL)
; END_MUL:
; HALT