macro Console!code {
	local conlogcycle
	local conlogend

Console.log:
	mov eax, 4
	mov ebx, 1
	mov dword ecx, [ARG!Console.log!string]
	push esi
	mov dword esi, ARG!Console.log!string
	add esi, 4
	mov edx, dword [esi]
	pop esi
	int 0x80
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