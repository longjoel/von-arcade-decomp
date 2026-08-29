/* i960 reset wrapper for the C boot reconstruction. */
	.text
	.align 4
	.globl _system_address_table
_system_address_table:
	.word _system_address_table
	.word _rom_prcb
	.word 0
	.word _start_ip
	.word 0
	.word 0
	.word 0
	.word _checksum

	.align 6
	.globl _rom_prcb
_rom_prcb:
	.word 0
	.word 0x0000000c
	.word 0
	.word 0
	.word 0
	.word _boot_intr_table
	.word _intr_stack
	.word 0
	.word 0x000001ff
	.word _system_proc_table
	.word _boot_fault_table
	.space 132

	.align 4
_system_proc_table:
	.space 1088

	.align 4
_boot_fault_table:
	.space 16 * 8

	.align 4
_boot_intr_table:
	.space 16
	.rept 248
	.word _fatal_intr
	.endr

	.align 6
_intr_stack:
	.space 0x600

	.align 6
_user_stack:
	.space 0x800

	.align 4
	.globl _start_ip
_start_ip:
	lda 0x00500400,fp
	lda -0x40(fp),pfp
	lda 0x40(fp),sp
	mov 0,g14
	call _i960_reconstructed_main
	b _start_ip

	.align 4
_fatal_intr:
	b _fatal_intr
