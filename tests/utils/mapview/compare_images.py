import base64
from io import BytesIO
import logging
log = logging.getLogger()

from PIL import Image
from IPython.display import HTML
from IPython.display import display

class UnsimilarImageError(Exception):
    pass

def compare_images(img1_path, img2_path, max_perc_diff = 0.01):
    img1 = Image.open(img1_path)
    img2 = Image.open(img2_path)

    # Bounds/sanity checks
    diff_ratios = (img1.height / img1.width) - (img2.height / img2.width)
    if diff_ratios > 0.05:
        _display_notebook_comparison(img1,img2,"!=")
        raise UnsimilarImageError("Ratios are not the same for images, "\
                                  "cannot compare, failing!")
    if img1.mode != img2.mode:
        raise UnsimilarImageError("Different kinds of images, failing!")
        
    # Resize image so they are the same size
    arbitrary_dimensions = (800,400)
    img1 = img1.resize(arbitrary_dimensions)
    img2 = img2.resize(arbitrary_dimensions)
 
    # Calculate the perc diff. Taken from Python section from
    # https://rosettacode.org/wiki/Percentage_difference_between_images
    pairs = zip(img1.getdata(), img2.getdata())
    if len(img1.getbands()) == 1:
        # for gray-scale jpegs
        dif = sum(abs(p1-p2) for p1,p2 in pairs)
    else:
        dif = sum(abs(c1-c2) for p1,p2 in pairs for c1,c2 in zip(p1,p2))

    ncomponents = img1.size[0] * img1.size[1] * 3
    perc_diff = (dif / 255.0) / ncomponents
    printable_perc_diff = "{0:.2f}".format(perc_diff * 100)

    if perc_diff > max_perc_diff:
        msg = f"Images are {printable_perc_diff}% different, which is "\
            f"higher than the {max_perc_diff * 100}% max limit. Failing."
        display(HTML("❌ " + msg))
        _display_notebook_comparison(img1,img2,"!=")
        raise UnsimilarImageError(msg)
    else:
        display(HTML(
            f"✅ Images are {printable_perc_diff}% different, which "\
            f"is below the {max_perc_diff * 100}% max limit."))
        _display_notebook_comparison(img1,img2,"==")
        return True

def _display_notebook_comparison(img1, img2, comparison_symbol="=="):
    def _img_to_base64(img):
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        return "data:image/png;base64,{}".format(base64.b64encode(buffered.getvalue()).decode("utf-8"))
    img1_base64 = _img_to_base64(img1.resize((250,100)))
    img2_base64 = _img_to_base64(img2.resize((250,100)))
    display(HTML("""
        <div style="display: inline-block">""" + \
            f'<img src="{img1_base64}"></img>' + """
        </div>
        <div style="display: inline-block">""" + \
             f"<h1>{comparison_symbol}</h1>" + """
        </div>
        <div style="display: inline-block"> """ + \
            f'<img src="{img2_base64}"></img>' + """
        </div>
        """))


