function submit_preview(form) { /* with timeout for ratelimiting*/
    if (typeof refresh_timeout !== 'undefined') {
        window.clearTimeout(refresh_timeout);
    }
    refresh_timeout = window.setTimeout(function(){form.submit();}, 200);
}

window.setTimeout(function(){document.getElementById("cardform").submit();}, 1);
