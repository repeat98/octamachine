/* Firmware-free RAM code-write probe for QEMU TCG translation invalidation. */
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
    jsr     smc_site
    move.l  %d0, 0x00020004.l
    lea     smc_site, %a0
    move.w  #0x7002, (%a0)
    jsr     smc_site
    move.l  %d0, 0x00020008.l
    cmpi.l  #2, %d0
    bne     fail
    move.l  #0xc0def00d, %d0
    move.l  %d0, 0x00020000.l
done:
    bra     done
smc_site:
    moveq   #1, %d0
    rts
fail:
    move.l  #0xbad00001, %d0
    move.l  %d0, 0x00020000.l
fail_loop:
    bra     fail_loop
illegal_handler:
    move.l  #0xbad00004, %d0
    move.l  %d0, 0x00020000.l
illegal_loop:
    bra     illegal_loop
