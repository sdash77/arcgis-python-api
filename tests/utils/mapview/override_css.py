from IPython.display import display, HTML

def override_css():
    css_override = "div.arcgisMapIPyWidgetDiv{"\
                       "width: 800px !important;"\
                       "height: 400px !important;}"
    display(HTML(
        f"Since importing <code>utils.mapview</code>, implementing CSS "\
        f"override to make all <code>MapView</code> instances the same "\
        f"width and height so screenshots are easier to compare. "\
        f"CSS applying: <code>{css_override}</code><hr>"\
        f'<style id="utils-mapview-override-css">{css_override}</style>'\
        f"<h3>- Make sure this message appears before drawing any maps.</h3>"\
        f"<h4>- Make sure window is fullscreen when taking screenshots</h4>"\
        f"<h4>- Make sure there are <code>time.sleep(X)</code> calls in "\
        f"individual cells surrounding <code>MapView.take_screenshot()</code>"\
        f" calls.</h4>"))
