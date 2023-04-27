SVF = 0

macro Console!code {
	local conlogcycle
	local conlogend

Console.log:
	mov word si, [ARG!Console.log!string]
	mov ah, 0x0E
conlogcycle:
	lodsb
	test al, al
	jz conlogend
	int 0x10
	jmp conlogcycle
conlogend:
	mov ax, 0
	ret
}

macro Console!rodata {
	CONST!Console.log!str!0 str ""
}

macro Console!data {
	ARG!Console.log!0:
	ARG!Console.log!string int CONST!Console.log!str!0
}

macro !Console.log!SVF{
	push word [ARG!Console.log!0]
}