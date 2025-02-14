def activation_email_content(base_url: str, token: str):
    """
    Returns subject and HTML body for an activation email.
    """
    activation_link = f"{base_url}/activate?token={token}"
    subject = "Confirm Your Subscription"
    body = f"""
    <html>
        <body>
            <p>Hello,</p>
            <p>Please confirm your subscription by clicking the button below:</p>
            <a href="{activation_link}" style="
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 15px 32px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                margin: 4px 2px;
                cursor: pointer;">
                Confirm Subscription
            </a>
            <p>If the button doesn't work, copy and paste this URL:</p>
            <p>{activation_link}</p>
        </body>
    </html>
    """
    return subject, body


def deletion_email_content(base_url: str, token: str):
    """
    Returns subject and HTML body for an account deletion email.
    """
    deletion_link = f"{base_url}/delete?token={token}"
    subject = "Confirm Account Deletion"
    body = f"""
    <html>
        <body>
            <p>We received a request to delete your account. If you made this request, click the button below:</p>
            <a href="{deletion_link}" style="
                background-color: #f44336;
                border: none;
                color: white;
                padding: 15px 32px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                margin: 4px 2px;
                cursor: pointer;">
                Confirm Account Deletion
            </a>
            <p>If the button doesn't work, copy and paste this URL:</p>
            <p>{deletion_link}</p>
        </body>
    </html>
    """
    return subject, body


def pause_email_content(base_url: str, token: str):
    """
    Returns subject and HTML body for a pause confirmation email.
    """
    pause_link = f"{base_url}/pause?token={token}"
    subject = "Confirm Email Pause"
    body = f"""
    <html>
        <body>
            <p>Hello,</p>
            <p>You requested to pause email notifications. Click the button below to confirm:</p>
            <a href="{pause_link}" style="
                background-color: #FFA500;
                border: none;
                color: white;
                padding: 15px 32px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                margin: 4px 2px;
                cursor: pointer;">
                Confirm Pause
            </a>
            <p>If the button doesn't work, copy and paste this URL:</p>
            <p>{pause_link}</p>
        </body>
    </html>
    """
    return subject, body


def resume_email_content(base_url: str, token: str):
    """
    Returns subject and HTML body for a resume confirmation email.
    """
    resume_link = f"{base_url}/resume?token={token}"
    subject = "Confirm Resume Notifications"
    body = f"""
    <html>
        <body>
            <p>Hello,</p>
            <p>You requested to resume email notifications. Click the button below to confirm:</p>
            <a href="{resume_link}" style="
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 15px 32px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                margin: 4px 2px;
                cursor: pointer;">
                Confirm Resume
            </a>
            <p>If the button doesn't work, copy and paste this URL:</p>
            <p>{resume_link}</p>
        </body>
    </html>
    """
    return subject, body
