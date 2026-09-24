/* Independent ColdFire ISA/exception probe. See README.md. */

.text
.align 2
.globl _start
_start:
    lea     0x00007f00, %sp

    move.l  #trap_handler, %d0
    move.l  %d0, 0x00000080.l
    move.l  #privilege_handler, %d0
    move.l  %d0, 0x00000020.l
    move.l  #illegal_handler, %d0
    move.l  %d0, 0x00000010.l
    move.l  #privilege_handler, %d0
    move.l  %d0, 0x00100020.l
    move.l  #aligned_vbr_handler, %d0
    move.l  %d0, 0x00100080.l
    move.l  #privilege_handler, %d0
    move.l  %d0, 0x00100120.l
    move.l  #unaligned_vbr_handler, %d0
    move.l  %d0, 0x00100180.l

    moveq   #0, %d0
    move.l  %d0, 0x00020000.l
    move.l  %d0, 0x00020004.l
    move.l  %d0, 0x00020008.l
    move.l  %d0, 0x0002000c.l
    move.l  %d0, 0x00020010.l
    move.l  %d0, 0x00020014.l
    move.l  %d0, 0x00020018.l
    move.l  %d0, 0x0002001c.l
    move.l  %d0, 0x00020020.l
    move.l  %d0, 0x00020024.l
    move.l  %d0, 0x00020028.l
    move.l  %d0, 0x0002002c.l
    move.l  %d0, 0x00020030.l
    move.l  %d0, 0x00020034.l
    move.l  %d0, 0x00020038.l

    move.l  %a7, 0x00020004.l
    move.l  #3, %d0
    move.l  #7, %d1
    muls.l  %d0, %d1
    cmpi.l  #21, %d1
    bne     fail
    move.l  #0x00010007, %d0
    moveq   #5, %d1
    mulu.w  %d0, %d1
    cmpi.l  #35, %d1
    bne     fail
    move.l  %d1, -(%a7)
    move.l  (%a7)+, %d2
    cmpi.l  #35, %d2
    bne     fail
    moveq   #1, %d0
    move.l  %d0, 0x00020014.l

    move.w  #0x2500, %sr
    trap    #0
    move.l  %a7, 0x0002000c.l

    move.l  #0x00100100, %d0
    movec   %d0, %vbr
    trap    #0

    move.w  #0x0500, %sr
    move.l  %a7, 0x00020030.l
    moveq   #0, %d0
    movec   %d0, %vbr
user_after_movec:
    move.l  %a7, 0x00020034.l
    move.l  #0xc0def00d, %d0
    move.l  %d0, 0x00020000.l
done:
    bra     done

fail:
    move.l  #0xbad00001, %d0
    move.l  %d0, 0x00020000.l
    bra     done

trap_handler:
    move.l  %a7, 0x00020008.l
    move.l  (%a7), %d0
    move.l  %d0, 0x00020018.l
    move.l  4(%a7), %d0
    move.l  %d0, 0x0002001c.l
    addq.l  #1, 0x00020010.l
    rte

privilege_handler:
    move.l  %a7, 0x00020020.l
    move.l  (%a7), %d0
    move.l  %d0, 0x00020024.l
    move.l  4(%a7), %d0
    move.l  %d0, 0x00020028.l
    addq.l  #1, 0x0002002c.l
    addq.l  #4, 4(%a7)
    rte

aligned_vbr_handler:
    move.l  #1, %d0
    move.l  %d0, 0x00020038.l
    rte

unaligned_vbr_handler:
    move.l  #2, %d0
    move.l  %d0, 0x00020038.l
    rte

illegal_handler:
    move.l  #0xbad00004, %d0
    move.l  %d0, 0x00020000.l
illegal_loop:
    bra     illegal_loop
