/* Target-only probe for the CFV4e conditional dual-stack-pointer feature. */

#ifndef EUSP_MASK
#define EUSP_MASK 0x20
#endif

.text
.align 2
.globl _start
_start:
    lea     0x00007f00, %sp
    move.l  #trap_handler, %d0
    move.l  %d0, 0x00000080.l
    move.l  #illegal_handler, %d0
    move.l  %d0, 0x00000010.l

    moveq   #0, %d0
    move.l  %d0, 0x00020000.l
    move.l  %d0, 0x00020004.l
    move.l  %d0, 0x00020008.l
    move.l  %d0, 0x0002000c.l

    /* EUSP is cleared at reset. Enable it while privileged, then initialize
       both active supervisor and user stacks before dropping privilege. */
    move.l  #EUSP_MASK, %d0
    movec   %d0, %cacr
    lea     0x00007f00, %sp
    move.l  #0x00006000, %a0
    move.l  %a0, %usp
    move.w  #0x0500, %sr

    move.l  %sp, 0x00020004.l
    trap    #0
user_after_trap:
    move.l  %sp, 0x0002000c.l
    move.l  #0xc0def00d, %d0
    move.l  %d0, 0x00020000.l
done:
    bra     done

trap_handler:
    move.l  %sp, 0x00020008.l
    rte

illegal_handler:
    move.l  #0xbad00004, %d0
    move.l  %d0, 0x00020000.l
illegal_loop:
    bra     illegal_loop
