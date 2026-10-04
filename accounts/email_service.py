from django.conf import settings

from brevo import Brevo
from brevo.transactional_emails import (
    SendTransacEmailRequestSender,
    SendTransacEmailRequestToItem,
)


def send_otp_email(
    email,
    otp,
    expiry_minutes=5,
):
    """
    Send a login OTP using Brevo.
    """

    client = Brevo(
        api_key=settings.BREVO_API_KEY,
        timeout=10.0,  # 10 seconds
    )

    result = client.transactional_emails.send_transac_email(
        subject="Your InternLink Ug Login Code",

        html_content=f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Your Login Code</title>
        </head>

        <body style="
            margin: 0;
            padding: 0;
            background-color: #f8fafc;
            font-family: Arial, sans-serif;
        ">

            <div style="
                max-width: 500px;
                margin: 40px auto;
                padding: 30px;
                background: #ffffff;
                border-radius: 16px;
                border: 1px solid #e2e8f0;
            ">

                <h1 style="
                    color: #1e293b;
                    margin-bottom: 10px;
                ">
                    InternLink Ug
                </h1>

                <p style="
                    color: #475569;
                    font-size: 16px;
                ">
                    Use the following one-time password
                    to complete your login:
                </p>

                <div style="
                    margin: 30px 0;
                    padding: 20px;
                    text-align: center;
                    background: #e6fff6;
                    border: 1px solid #12e49e;
                    border-radius: 10px;
                ">

                    <span style="
                        font-size: 32px;
                        font-weight: bold;
                        letter-spacing: 8px;
                        color: #1e293b;
                    ">
                        {otp}
                    </span>

                </div>

                <p style="
                    color: #64748b;
                    font-size: 14px;
                ">
                    This code will expire in
                    {expiry_minutes} minutes.
                </p>

                <p style="
                    color: #64748b;
                    font-size: 14px;
                ">
                    If you did not request this code,
                    you can safely ignore this email.
                </p>

            </div>

        </body>
        </html>
        """,

        sender=SendTransacEmailRequestSender(
            email=settings.BREVO_SENDER_EMAIL,
            name=settings.BREVO_SENDER_NAME,
        ),

        to=[
            SendTransacEmailRequestToItem(
                email=email,
            )
        ],
    )

    return result
