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
}

macro !entry fn {
	entry fn
}

macro !section a& {
common
section a
}

macro !dbg.print string {
}

struc str string {
	dd .value
	dd .finish-.value-1
.value:
	db string
	db 0x00
}

struc str!init string {
	dd .value
	dd 0
.value:
	times 64 db 0
	db 0x00
}

struc Sequence!init a& {
	rw 32
}

struc str!SEQ!init a& {
	dd 0 ; length of array
}

struc int integer {
	dd integer AND 0xFFFF
}

struc int!init integer& {
	dd 0
}