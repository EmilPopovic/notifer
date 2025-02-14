confirmation_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Notification Status</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 2rem;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background-color: #f8f9fa;
        }}
        .container {{
            background: white;
            padding: 2rem;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            max-width: 600px;
            text-align: center;
        }}
        h1 {{
            color: #2c3e50;
            margin-bottom: 1rem;
        }}
        p {{
            color: #666;
            font-size: 1.1rem;
            margin: 1rem 0;
        }}
        a {{
            color: #3498db;
            text-decoration: none;
            font-weight: 500;
        }}
        .emoji {{
            font-size: 3rem;
            margin: 1rem 0;
        }}
    </style>
    <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
    <div class="container">
        <div class="emoji">{emoji}</div>
        <h1>{title}</h1>
        <p>{message}</p>
        <p><a href="{base_url}">← Return to NotiFER</a></p>
    </div>
</body>
</html>
"""


error_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Error</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 2rem;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background-color: #f8f9fa;
        }}
        .container {{
            background: white;
            padding: 2rem;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            max-width: 600px;
            text-align: center;
        }}
        h1 {{
            color: #2c3e50;
            margin-bottom: 1rem;
        }}
        p {{
            color: #666;
            font-size: 1.1rem;
            margin: 1rem 0;
        }}
        a {{
            color: #3498db;
            text-decoration: none;
            font-weight: 500;
        }}
        .emoji {{
            font-size: 3rem;
            margin: 1rem 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="emoji">{emoji}</div>
        <h1>Something Went Wrong</h1>
        <p>{message}</p>
        <p><a href="{base_url}">← Return to NotiFER</a></p>
    </div>
</body>
</html>
"""


activation_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Account Activated</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 2rem;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background-color: #f8f9fa;
        }}
        .container {{
            background: white;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.1);
            max-width: 600px;
            text-align: center;
        }}
        .success-icon {{
            font-size: 4rem;
            color: #34c759;
            margin: 1rem 0;
        }}
        h1 {{
            color: #2c3e50;
            margin: 1rem 0;
            font-size: 2rem;
        }}
        p {{
            color: #666;
            font-size: 1.1rem;
            line-height: 1.6;
            margin: 1rem 0;
        }}
        .return-link {{
            display: inline-block;
            margin-top: 2rem;
            padding: 12px 24px;
            background-color: #3498db;
            color: white !important;
            text-decoration: none;
            border-radius: 6px;
            transition: transform 0.2s;
        }}
        .return-link:hover {{
            transform: translateY(-2px);
        }}
    </style>
    <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
    <div class="container">
        <div class="success-icon">✓</div>
        <h1>Account Activated!</h1>
        <p>You're now subscribed to calendar change notifications.</p>
        <p>We'll monitor your calendar and email you about any changes to your schedule.</p>
        <a href="{base_url}" class="return-link">Return to NotiFER</a>
    </div>
</body>
</html>
"""
