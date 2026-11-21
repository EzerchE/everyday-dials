namespace EverydayDials;

// Only the four shipped YouTube definitions select this canvas. All other apps
// retain the original generic layout and feedback shape.
static class YouTubeFeedback
{
    static readonly Dictionary<string,string> Dials=new()
    {
        ["youtube-controls-2"]="volume",["youtube-controls-0"]="seek",
        ["youtube-controls-1"]="speed",["youtube-controls-3"]="frame"
    };
    public static bool IsYouTube(DialSpec spec)=>Dials.ContainsKey(spec.Id);
    public static string Layout(DialSpec spec)=>IsYouTube(spec)?"layouts/youtube.json":"layouts/control.json";
    public const int FeedbackMilliseconds=140;
    public static string Background(DialSpec spec,int direction,bool pressed=false,bool? masterMuted=null)
    {
        string stem="dial-"+Dials[spec.Id];
        // Only Windows master mute has an exact source. Browser mute and playback
        // state are deliberately not inferred from the shortcuts we sent.
        if(spec.Volume&&masterMuted==true&&(pressed||direction==0))stem+="-muted";
        return "images/youtube-dials/"+stem+(pressed?"-pressed":direction<0?"-left":direction>0?"-right":"")+".png";
    }
    public static string EncoderImage(DialSpec spec,int direction=0)=>"images/youtube-encoders/dial-"+Dials[spec.Id]+".png";
}
