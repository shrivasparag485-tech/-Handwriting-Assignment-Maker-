from flask import Flask, render_template, request, send_file
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import ttfonts
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.colors import blue, black
import os, tempfile

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load fonts
pdfmetrics.registerFont(
    ttfonts.TTFont('Hand1', os.path.join(BASE_DIR, 'static/font1.ttf'))
)
pdfmetrics.registerFont(
    ttfonts.TTFont('Hand2', os.path.join(BASE_DIR, 'static/font2.ttf'))
)

PAGE_WIDTH = 595
PAGE_HEIGHT = 842


# 🔥 UPDATED WRAP (LINE BREAK SUPPORT)
def wrap_text(text, max_width, c, font, size):
    lines = []

    paragraphs = text.split("\n")  # preserve line breaks

    for para in paragraphs:
        words = para.split()
        current = ""

        for word in words:
            test = current + " " + word if current else word
            if c.stringWidth(test, font, size) <= max_width:
                current = test
            else:
                lines.append(current)
                current = word

        if current:
            lines.append(current)

        lines.append("")  # blank line for spacing

    return lines


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():
    content = request.form['content']
    ink     = request.form['ink']
    output  = request.form['output']
    style   = request.form['style']

    # Font select
    font = 'Hand1' if style == '1' else 'Hand2'

    # Color select
    color = blue if ink == 'blue' else black

    file_path = os.path.join(tempfile.gettempdir(), "assignment.pdf")
    c = canvas.Canvas(file_path, pagesize=A4)

    def new_page():
        c.drawImage(
            os.path.join(BASE_DIR, 'static/notebook.jpg'),
            0, 0,
            width=PAGE_WIDTH,
            height=PAGE_HEIGHT
        )

    new_page()

    # Layout tuning (unchanged)
    left_margin = 115
    right_limit = 600
    max_width = right_limit - left_margin

    start_y = 700
    line_gap = 30
    font_size = 23

    c.setFillColor(color)
    c.setFont(font, font_size)

    lines = wrap_text(content, max_width, c, font, font_size)

    y = start_y

    for line in lines:
        if y < 80:
            c.showPage()
            new_page()
            c.setFont(font, font_size)
            y = start_y

        if line == "":
            y -= line_gap   # blank line spacing
            continue

        c.drawString(left_margin, y, line)
        y -= line_gap

    c.save()

    # 🔥 Image output (unchanged)
    if output == 'image':
        from PIL import Image, ImageDraw, ImageFont

        img = Image.open(os.path.join(BASE_DIR, 'static/notebook.jpg'))
        draw = ImageDraw.Draw(img)

        font_file = 'font1.ttf' if style == '1' else 'font2.ttf'

        pil_font = ImageFont.truetype(
            os.path.join(BASE_DIR, f'static/{font_file}'), 46
        )

        rgb_color = (0, 0, 255) if ink == 'blue' else (0, 0, 0)

        y_img = 180
        left_img = 135

        for line in lines:
            if line == "":
                y_img += 60
                continue

            draw.text((left_img, y_img), line, fill=rgb_color, font=pil_font)
            y_img += 60

        img_path = os.path.join(tempfile.gettempdir(), "assignment.jpg")
        img.save(img_path)

        return send_file(img_path, as_attachment=True)

    return send_file(file_path, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)