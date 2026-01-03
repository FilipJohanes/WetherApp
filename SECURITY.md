# Security Notice

## ⚠️ CRITICAL: HTTPS Required for Production

**Current Security Issue**: Passwords and sensitive data are transmitted in plain text over HTTP.

### Immediate Actions Required:

1. **Enable HTTPS** with SSL/TLS certificates
2. **Never use this application over plain HTTP in production**
3. **Use a reverse proxy** (nginx/Apache) with SSL termination

### How to Enable HTTPS:

#### Option 1: Using nginx as reverse proxy (Recommended)

```bash
# Install nginx and certbot
sudo apt-get install nginx certbot python3-certbot-nginx

# Get free SSL certificate from Let's Encrypt
sudo certbot --nginx -d yourdomain.com

# Configure nginx (example)
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    location / {
        proxy_pass http://127.0.0.1:5000;  # Web app
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /api/ {
        proxy_pass http://127.0.0.1:5001;  # API
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

#### Option 2: Self-signed certificate for testing (NOT for production)

```bash
# Generate self-signed certificate
openssl req -x509 -newkey rsa:4096 -nodes \
  -out cert.pem -keyout key.pem -days 365

# Run Flask with SSL
# In api.py and web_app.py, change:
app.run(host='0.0.0.0', port=5001, ssl_context=('cert.pem', 'key.pem'))
```

### Environment Variables to Update:

```bash
# In .env.frontend (web app)
BACKEND_API_URL=https://yourdomain.com/api  # Use HTTPS!

# In .env.backend (API)
# No changes needed if using reverse proxy
```

### Additional Security Measures:

1. **Rate Limiting**: Already implemented ✓
2. **API Key Authentication**: Already implemented ✓
3. **Password Hashing**: Already implemented (bcrypt) ✓
4. **HTTPS**: ⚠️ **MUST BE IMPLEMENTED**
5. **CSRF Protection**: Consider adding for web forms
6. **Security Headers**: Add in nginx/reverse proxy:
   - `Strict-Transport-Security`
   - `X-Content-Type-Options`
   - `X-Frame-Options`
   - `X-XSS-Protection`

### Verification:

After enabling HTTPS, verify:
- [ ] Web interface only accessible via HTTPS
- [ ] API only accessible via HTTPS
- [ ] HTTP requests redirect to HTTPS
- [ ] SSL certificate is valid and trusted
- [ ] No mixed content warnings in browser

### Resources:

- [Let's Encrypt](https://letsencrypt.org/) - Free SSL certificates
- [Mozilla SSL Configuration Generator](https://ssl-config.mozilla.org/)
- [Security Headers](https://securityheaders.com/) - Check your headers

## Reporting Security Issues

If you discover a security vulnerability, please email the maintainer directly instead of creating a public issue.
