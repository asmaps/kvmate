function openVNC()
{
    rfb = RFB({'target': $D('noVNC_canvas'),
              'onUpdateState': updateState,
              });
    rfb.set_encrypt(false);
    rfb.set_true_color(true);
    rfb.set_local_cursor(true);
    rfb.set_shared(true);
    rfb.set_view_only(false);
    rfb.set_connectTimeout(2);
    rfb.connect(host, port, '', '');
}

function pasteText(text)
{
    for (var i=0; i < text.length; i+=1) {
        rfb.get_keyboard().get_onKeyPress()(text.charCodeAt(i), true);
    }
}

document.onpaste = function(e) {
    pasteText(e.clipboardData.getData("Text"));
    e.preventDefault();
}

function updateState(rfb, state, oldstate, msg) {
    // don't care about states, just print me the message
    if (typeof(msg) !== 'undefined') {
        $D('noVNC_status').innerHTML = msg;
    }
}
