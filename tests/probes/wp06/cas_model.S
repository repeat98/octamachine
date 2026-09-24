/* Firmware-free CAS.L feature probe; assembled with the 68020 syntax. */
.text
.align 2
.globl _start
_start:
    lea     0x00007f00, %sp
    move.l  #illegal_handler, %d0
    move.l  %d0, 0x00000010.l
    moveq   #0, %d0
    move.l  %d0, 0x00020000.l
    move.l  %d0, 0x00020004.l
    lea     0x00030000, %a0
    move.l  #0x12345678, (%a0)
    move.l  #0x12345678, %d0
    move.l  #0x87654321, %d1
    cas.l   %d0, %d1, (%a0)
    move.l  (%a0), %d2
    move.l  %d2, 0x00020004.l
    cmpi.l  #0x87654321, %d2
    bne     fail
    move.l  #0xc0def00d, %d0
    move.l  %d0, 0x00020000.l
done:
    bra     done
fail:
    move.l  #0xbad00001, %d0
    move.l  %d0, 0x00020000.l
fail_loop:
    bra     fail_loop
illegal_handler:
    move.l  0x00030000.l, %d1
    move.l  %d1, 0x00020004.l
    move.l  #0xbad00004, %d0
    move.l  %d0, 0x00020000.l
illegal_loop:
    bra     illegal_loop
