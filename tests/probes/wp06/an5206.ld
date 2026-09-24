OUTPUT_FORMAT("elf32-m68k")
OUTPUT_ARCH(m68k)
ENTRY(_start)
PHDRS { ram PT_LOAD FLAGS(5); }
SECTIONS
{
  . = 0x00010000;
  .text : { *(.text) } :ram
}
