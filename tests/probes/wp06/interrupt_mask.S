/* Firmware-free level-4 timer interrupt probe for SR.I masking. */

.text
.align 2
.globl _start
_start:
    lea     0x00007f00, %sp
    move.l  #timer_handler, %d0
    move.l  %d0, 0x00000070.l       /* autovector: level 4 */
    moveq   #0, %d0
    move.l  %d0, 0x00020000.l       /* success marker */
    move.l  %d0, 0x00020004.l       /* handlers before unmask */
    move.l  %d0, 0x00020008.l       /* timer status before unmask */
    move.l  %d0, 0x0002000c.l       /* handler count */

    /* Keep level 4 masked with SR.I=5 while the timer raises IRQ 9. */
    move.w  #0x2500, %sr
    moveq   #0, %d1
    move.b  #0x90, %d1
    move.b  %d1, 0x1000001c.l       /* ICR9: autovector, level 4 */
    move.l  #0x3dfe, %d1
    move.w  %d1, 0x10000036.l       /* clear IMR bit 9 */
    moveq   #0x10, %d1
    move.w  %d1, 0x10000104.l       /* short reference interval */
    moveq   #0x1b, %d1
    move.w  %d1, 0x10000100.l       /* reset, clock mode 1, FRR, ORI */

    move.l  #200000, %d0
masked_wait:
    subq.l  #1, %d0
    bne     masked_wait
    move.l  0x0002000c.l, %d0
    move.l  %d0, 0x00020004.l
    moveq   #0, %d0
    move.b  0x10000111.l, %d0
    andi.l  #0x00000002, %d0
    move.l  %d0, 0x00020008.l
    move.l  0x00020004.l, %d1
    tst.l   %d1
    bne     interrupt_not_masked
    move.l  0x00020008.l, %d1
    cmpi.l  #2, %d1
    bne     timer_did_not_fire

    /* Level 4 now exceeds SR.I=3 and must be taken. */
    move.w  #0x2300, %sr
    move.l  #200000, %d0
unmasked_wait:
    tst.l   0x0002000c.l
    bne     delivered
    subq.l  #1, %d0
    bne     unmasked_wait
    bra     timer_did_not_fire

delivered:
    move.l  0x0002000c.l, %d0
    cmpi.l  #1, %d0
    bne     unexpected_repeat
    move.l  #0xc0def00d, %d0
    move.l  %d0, 0x00020000.l
done:
    bra     done

interrupt_not_masked:
    move.l  #0xbad00003, %d0
    move.l  %d0, 0x00020000.l
    bra     done

timer_did_not_fire:
    move.l  #0xbad00002, %d0
    move.l  %d0, 0x00020000.l
    bra     done

unexpected_repeat:
    move.l  #0xbad00004, %d0
    move.l  %d0, 0x00020000.l
    bra     done

timer_handler:
    moveq   #0, %d1
    move.w  %d1, 0x10000100.l       /* stop timer so it fires only once */
    moveq   #2, %d1
    move.b  %d1, 0x10000111.l       /* clear TER reference flag */
    addq.l  #1, 0x0002000c.l
    rte
