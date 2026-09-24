/* Firmware-free user-mode privilege probe for ColdFire cache controls. */

#ifndef PROBE_KIND
#error "PROBE_KIND must select CPUSHL, CACR write, or CACR read"
#endif

.text
.align 2
.globl _start
_start:
    lea     0x00007f00, %sp
    move.l  #illegal_handler, %d0
    move.l  %d0, 0x00000010.l
    move.l  #privilege_handler, %d0
    move.l  %d0, 0x00000020.l

    moveq   #0, %d0
    move.l  %d0, 0x00020000.l
    move.l  %d0, 0x00020004.l
    move.l  %d0, 0x00020008.l
    move.l  %d0, 0x0002000c.l
    move.l  %d0, 0x00020010.l
    move.l  %d0, 0x00020014.l
    move.l  %d0, 0x00020018.l

    move.l  #0x13579bdf, %d0
    move.l  %d0, 0x00030000.l
    lea     0x00030000, %a0
    move.l  #user_privileged_instruction, %d0
    move.l  %d0, 0x00020010.l
    moveq   #0, %d0

    move.w  #0x0500, %sr
user_privileged_instruction:
#if PROBE_KIND == 0
    cpushl  %bc, (%a0)
#elif PROBE_KIND == 1
    movec   %d0, %cacr
#elif PROBE_KIND == 2
    /* GNU as rejects CACR reads for ColdFire; encode MOVEC CACR -> D1. */
    .word   0x4e7a, 0x1002
#else
#error "unsupported PROBE_KIND"
#endif
    move.l  #0xbad00001, %d0
    move.l  %d0, 0x00020000.l
unexpected_return:
    bra     unexpected_return

privilege_handler:
    move.l  #0xbad00008, %d1
    bra     exception_handler
illegal_handler:
    move.l  #0xbad00004, %d1
exception_handler:
    move.l  %sp, 0x00020014.l
    move.l  (%sp), %d0
    move.l  %d0, 0x00020008.l
    move.l  4(%sp), %d0
    move.l  %d0, 0x0002000c.l
    addq.l  #1, 0x00020004.l
    move.l  0x00030000.l, %d0
    move.l  %d0, 0x00020018.l
    move.l  %d1, 0x00020000.l
exception_loop:
    bra     exception_loop
