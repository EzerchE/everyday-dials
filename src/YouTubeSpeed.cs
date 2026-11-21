namespace EverydayDials;

// YouTube recognizes Shift + OEM comma/period. Resolving literal < or > through
// an AltGr layout adds Ctrl+Alt, which the player does not accept for speed.
static class YouTubeSpeed
{
    public static bool IsCommand(string command)=>command is "YTSPEEDDOWN" or "YTSPEEDUP" or "YTSPEEDRESET";
    public static ushort[][] Packets(string command)=>command switch
    {
        "YTSPEEDDOWN"=>[new ushort[]{0x10,0xBC}],
        "YTSPEEDUP"=>[new ushort[]{0x10,0xBE}],
        // No public one-key reset exists. Use bounded player shortcuts to reach
        // its 0.25x floor, then three +0.25x steps. No seek or play/pause input.
        "YTSPEEDRESET"=>Enumerable.Range(0,32).Select(_=>new ushort[]{0x10,0xBC}).Concat(Enumerable.Range(0,3).Select(_=>new ushort[]{0x10,0xBE})).ToArray(),
        _=>[]
    };
}
