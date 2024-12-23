import pdfkit
import imgkit
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
import qrcode

# HTML template
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Horizontal ID Card</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .id-card {
            width: 350px;
            height: 200px;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            background-color: #f8f9fa;
        }
        .id-card img {
            border-radius: 8px;
            width: 100%;
        }
        .profile-pic {
            width: 80px;
            height: 80px;
            overflow: hidden;
        }
        .qr-code img {
            width: 80px;
            height: 80px;
        }
        .info {
            flex-grow: 1;
            margin: 0 15px;
        }
        .info h5 {
            margin-bottom: 8px;
            font-weight: bold;
        }
        .info p {
            margin: 0;
        }
    </style>
</head>
<body>
    <div class="container mt-5 d-flex justify-content-center">
        <div class="id-card">
            <div class="profile-pic">
                <img src="https://via.placeholder.com/80" alt="Profile Picture">
            </div>
            <div class="info">
                <h5>John Doe</h5>
                <p>Position: Software Engineer</p>
                <p>Department: IT</p>
                <p>Email: john.doe@example.com</p>
            </div>
            <div class="qr-code">
                <img src="https://via.placeholder.com/80" alt="QR Code">
            </div>
        </div>
    </div>
</body>
</html>
"""


def create_html():
    # Save HTML to a file
    html_file = "id-generator1.html"
    with open(html_file, "w") as file:
        file.write(html_content)
    return html_file


def generate_pdf():
    html_file = create_html()
    # Convert HTML to PDF
    pdf_file = "id_card.pdf"
    pdfkit.from_file(html_file, pdf_file)


def generate_picture():
    html_file = create_html()
    # Convert HTML to Image
    image_file = "id_card.png"
    imgkit.from_file(html_file, image_file)


def generate_qr_code(user_id, file_name="user_qr.png"):
    """
    Generate a QR code using the given user ID and save it as an image.

    :param user_id: The user ID to encode in the QR code
    :param file_name: The file name for the QR code image
    """
    # Create a QR Code object
    qr = qrcode.QRCode(
        version=1,  # Controls the size of the QR Code
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )

    # Add data (user ID) to the QR Code
    qr.add_data(user_id)
    qr.make(fit=True)

    # Generate the QR Code image
    img = qr.make_image(fill_color="black", back_color="white")

    # Save the QR Code image
    img.save(file_name)
    print(f"QR code generated and saved as {file_name}")

# Example usage
user_id = "12345"
generate_qr_code(user_id, "user_id_qr.png")


# Send email with attachments
def send_email(sender_email, receiver_email, sender_password):
    # Email content setup
    subject = "ID Card"
    body = "Please find attached your ID card as a PDF and image."

    # Create the email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    # Attach PDF
    with open(pdf_file, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename={os.path.basename(pdf_file)}",
        )
        msg.attach(part)

    # Attach Image
    with open(image_file, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename={os.path.basename(image_file)}",
        )
        msg.attach(part)

    # Connect to the email server and send the email
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
            print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Replace with your email credentials and recipient
send_email("your_email@gmail.com", "recipient_email@gmail.com", "your_email_password")
