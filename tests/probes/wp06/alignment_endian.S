/* Firmware-free data-alignment and byte-order probe. See README.md. */

.text
.align 2
.globl _start
_start:
    move.l  #access_error, %d0
    move.l  %d0, 0x00000008.l
    move.l  %d0, 0x0000000c.l

    move.l  #0x12345678, %d0
    move.l  %d0, 0x00030000.l
    moveq   #0, %d0
    move.b  0x00030000.l, %d0
    move.l  %d0, 0x00020004.l

    moveq   #0, %d0
    move.w  0x00030000.l, %d0
    move.l  %d0, 0x00020008.l

    moveq   #0, %d0
    move.w  0x00030001.l, %d0
    move.l  %d0, 0x0002000c.l

    move.l  0x00030000.l, %d0
    move.l  %d0, 0x00020010.l

    move.l  0x00030001.l, %d0
    move.l  %d0, 0x00020014.l

    move.l  #0xa1b2c3d4, %d0
    move.l  %d0, 0x00030101.l
    move.l  0x00030101.l, %d0
    move.l  %d0, 0x00020018.l

    move.l  #0xc0def00d, %d0
    move.l  %d0, 0x00020000.l
done:
    bra     done

access_error:
    move.l  #0xbad00004, %d0
    move.l  %d0, 0x00020000.l
error_loop:
    bra     error_loop
