import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import string
from datetime import datetime, timedelta

# Store OTP temporarily (in production, use Redis or database)
otp_storage = {}

def generate_otp(length=6):
    """Generate a random OTP code"""
    return ''.join(random.choices(string.digits, k=length))

def send_otp_email(email):
    """Send OTP to user's email"""
    try:
        # Generate OTP
        otp_code = generate_otp()
        
        # Store OTP with expiration (5 minutes)
        otp_storage[email] = {
            'code': otp_code,
            'expires_at': datetime.now() + timedelta(minutes=5)
        }
        
        # Email credentials
        taikhoan = "luisaccforwork@gmail.com"
        matkhau = "jfow ozvc tivl vqkq"
        
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = "Mã xác thực OTP - khampha.online"
        message["From"] = taikhoan
        message["To"] = email
        
        # Email content
        text = f"""
Xin chào!

Mã xác thực OTP của bạn là: {otp_code}

Mã này sẽ hết hạn sau 5 phút.

Nếu bạn không yêu cầu mã này, vui lòng bỏ qua email này.

Trân trọng,
Đội ngũ khampha.online
        """
        
        html = f"""
<html>
  <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
      <h2 style="color: #13a4ec; text-align: center;">khampha.online</h2>
      <h3>Xác thực tài khoản của bạn</h3>
      <p>Xin chào!</p>
      <p>Mã xác thực OTP của bạn là:</p>
      <div style="background-color: #f0f8ff; padding: 15px; text-align: center; margin: 20px 0; border-radius: 5px;">
        <h1 style="color: #13a4ec; margin: 0; letter-spacing: 5px; font-size: 32px;">{otp_code}</h1>
      </div>
      <p style="color: #666;">Mã này sẽ hết hạn sau <strong>5 phút</strong>.</p>
      <p style="color: #999; font-size: 14px;">Nếu bạn không yêu cầu mã này, vui lòng bỏ qua email này.</p>
      <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
      <p style="color: #999; font-size: 12px; text-align: center;">© 2024 khampha.online - Made with ❤️ in Vietnam</p>
    </div>
  </body>
</html>
        """
        
        message.attach(MIMEText(text, "plain"))
        message.attach(MIMEText(html, "html"))
        
        # Send email
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(taikhoan, matkhau)
            server.sendmail(taikhoan, email, message.as_string())
        
        return {'success': True, 'message': 'OTP đã được gửi đến email của bạn'}
    
    except Exception as e:
        print(f"Error sending OTP: {e}")
        return {'success': False, 'error': str(e)}

def verify_otp(email, otp_code, mark_verified=False):
    """Verify OTP code"""
    if email not in otp_storage:
        return {'success': False, 'error': 'OTP không tồn tại hoặc đã hết hạn'}
    
    stored_data = otp_storage[email]
    
    # Check if OTP expired
    if datetime.now() > stored_data['expires_at']:
        del otp_storage[email]
        return {'success': False, 'error': 'OTP đã hết hạn'}
    
    # Verify OTP
    if stored_data['code'] != otp_code:
        return {'success': False, 'error': 'Mã OTP không chính xác'}
    
    # Mark as verified if requested
    if mark_verified:
        stored_data['verified'] = True
        stored_data['verified_at'] = datetime.now()
    
    return {'success': True, 'message': 'Xác thực thành công'}

def is_otp_verified(email):
    """Check if OTP was verified for this email"""
    if email not in otp_storage:
        return False
    
    stored_data = otp_storage[email]
    
    # Check if verified and not expired
    if stored_data.get('verified') and datetime.now() <= stored_data['expires_at']:
        return True
    
    return False

def clear_otp(email):
    """Clear OTP for email after successful registration"""
    if email in otp_storage:
        del otp_storage[email]

def cleanup_expired_otps():
    """Remove expired OTPs from storage"""
    current_time = datetime.now()
    expired_emails = [email for email, data in otp_storage.items() 
                     if current_time > data['expires_at']]
    for email in expired_emails:
        del otp_storage[email]
