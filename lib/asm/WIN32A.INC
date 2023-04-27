
; Win32 programming headers (ASCII)

include 'MACRO/STRUCT.INC'
include 'MACRO/PROC32.INC'
include 'MACRO/COM32.INC'
include 'MACRO/IMPORT32.INC'
include 'MACRO/EXPORT.INC'
include 'MACRO/RESOURCE.INC'

struc TCHAR [val] { common match any, val \{ . db val \}
                           match , val \{ . db ? \} }
sizeof.TCHAR = 1

include 'EQUATES/KERNEL32.INC'
include 'EQUATES/USER32.INC'
include 'EQUATES/GDI32.INC'
include 'EQUATES/COMCTL32.INC'
include 'EQUATES/COMDLG32.INC'
include 'EQUATES/SHELL32.INC'
include 'EQUATES/WSOCK32.INC'

macro api [name] { if used name
                    label name dword at name#A
                   end if }
