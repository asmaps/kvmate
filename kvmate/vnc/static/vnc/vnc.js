function openVNC()
{
    rfb = RFB({'target': $D('noVNC_canvas'),
              'onUpdateState': updateState,
              'onClipboard': clipReceive,
              'onDesktopName': updateDocumentTitle});

    rfb.set_encrypt(false);
    rfb.set_true_color(true);
    rfb.set_local_cursor(true);
    rfb.set_shared(true);
    rfb.set_view_only(false);
    rfb.set_connectTimeout(2);
//    rfb.set_repeaterID(getSetting('repeaterID'));
    rfb.connect(host, port, '', '');
}

function pasteText(text)
{
    var arr, i, n;
    n = text.length;
    for (i=0; i < n; i+=1) {
//        arr.push(text.charCodeAt(i));
        rfb.get_keyboard().get_onKeyPress()( text.charCodeAt(i) ,true);
    }
}

document.body.onpaste = function(e) {
    pasteText(e.clipboardData.getData("Text"));
    e.preventDefault();
}

function updateState(rfb, state, oldstate, msg) {
    var klass;
    rfb_state = state;
    switch (state) {
        case 'failed':
        case 'fatal':
            klass = "noVNC_status_error";
            break;
        case 'normal':
            klass = "noVNC_status_normal";
            break;
        case 'disconnected':
            $D('noVNC_logo').style.display = "block";
            // Fall through
        case 'loaded':
            klass = "noVNC_status_normal";
            break;
        default:
            klass = "noVNC_status_warn";
            break;
    }

    if (typeof(msg) !== 'undefined') {
        $D('noVNC_status').innerHTML = msg;
    }
}

function clipReceive(rfb, text) {
    Util.Debug(">> clipReceive: " + text.substr(0,40) + "...");
    $D('noVNC_clipboard_text').value = text;
    Util.Debug("<< clipReceive");
}

// Display the desktop name in the document title
function updateDocumentTitle(rfb, name) {
    document.title = name ;
}
