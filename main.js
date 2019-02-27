var socket=new WebSocket(((window.location.protocol=='https:')?'wss:':'ws:')+"//"+window.location.host+"/webs")
socket.onmessage=(e)=>{console.log(JSON.parse(e.data));}
function namedcmd(cmd,name)
{
    m={"type":cmd,"name":name};
    socket.send(JSON.stringify(m));
}