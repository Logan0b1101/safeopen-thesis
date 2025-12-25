rule Detect_Macro
{
    meta:
        description = "Detects potential VBA macros or OLE content"
        author = "SafeOpen Thesis"

    strings:
        $macro1 = { D0 CF 11 E0 A1 B1 1A E1 } // OLE header signature
        $macro2 = /ActiveXObject/i
        $macro3 = /AutoOpen/i
        $macro4 = /Shell\.Application/i

    condition:
        any of ($macro*)
}
