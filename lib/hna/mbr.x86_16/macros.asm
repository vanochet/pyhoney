macro display_hex bits,value
{   if value < 0
      display "not implemented neg value conversion to HEX",13,10
    else
      display "0x"
      repeat bits/4
        d = "0" + value shr (bits-%*4) and 0x0F
        if d > "9"
            d = d + "A"-"9"-1
        end if
        display d
      end repeat
    end if
    display 0x0D, 0x0A
}

macro !org adr {
	org adr
}

macro !entry fn {
	jmp fn
}

macro !section a& {}

macro !dbg.print string {
	local cycle
	local gend

	pusha

	mov word si, [string]
	mov ah, 0x0E
cycle:
	lodsb
	test al, al
	jz gend
	int 0x10
	jmp cycle
gend:
	mov ax, 0

	popa
}

struc str string {
	dw .value
.value:
	db string
	db 0x00
}

struc str!init string {
	dw .value
.value:
	times 64 db 0
	db 0x00
}

struc Sequence!init a& {
	rw 32
}

struc str!SEQ!init a& {
	dw 0 ; length of array
}

struc int integer {
	dw integer AND 0xFFFF
}

struc int!init integer& {
	dw 0
}