/* Isolate target-model support for control registers used during MD startup. */

#ifndef CONTROL_REGISTER
#error "CONTROL_REGISTER must be supplied by the probe runner"
#endif

.text
.align 2
.globl _start
_start:
    moveq   #0, %d0
    /* ACR0 and ACR1 are handled as no-ops by the current cfv4e model. */
    .word   0x4e7b, 0x0004
    .word   0x4e7b, 0x0005
    /* D0 -> RAMBAR0 (0x0c04) or MBAR (0x0c0f). */
    .word   0x4e7b, CONTROL_REGISTER
done:
    bra     done
