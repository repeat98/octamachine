/* Firmware-free QEMU CACR and cache-instruction probe. */
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
    move.l  %d0, 0x00020008.l
    move.l  %d0, 0x0002000c.l
    move.l  %d0, 0x00020010.l
    move.l  %d0, 0x00020014.l
    move.l  #0x13579bdf, %d0
    move.l  %d0, 0x00030000.l
    lea     0x00030000, %a0
    cpushl  %bc, (%a0)
    move.l  #1, %d0
    move.l  %d0, 0x00020004.l
    movec   %d0, %cacr
    move.l  #1, %d0
    move.l  %d0, 0x00020008.l
    /* GNU as rejects CACR reads for ColdFire; encode MOVEC CACR -> D1. */
    .word   0x4e7a, 0x1002
    move.l  #1, %d0
    move.l  %d0, 0x0002000c.l
    move.l  %d1, 0x00020010.l
    move.l  #0xc0def00d, %d0
    move.l  %d0, 0x00020000.l
done:
    bra     done
illegal_handler:
    move.l  0x00030000.l, %d2
    move.l  %d2, 0x00020014.l
    move.l  #0xbad00004, %d0
    move.l  %d0, 0x00020000.l
illegal_loop:
    bra     illegal_loop
