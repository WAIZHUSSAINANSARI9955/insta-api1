# GitHub Push Instructions

Is project ko GitHub par push karne ke liye jo process follow kiya gaya hai, uski saari details yahan hain:

### 1. Repository Details
- **Repository Name**: `insta-api1`
- **Owner**: `WAIZHUSSAINANSARI9955`
- **GitHub URL**: `https://github.com/WAIZHUSSAINANSARI9955/insta-api1.git`

### 2. Remote Configuration
Hamne remote origin ko token ke saath set kiya hai taake authentication fail na ho:
```powershell
git remote add origin https://github.com/WAIZHUSSAINANSARI9955/insta-api1.git
```

### 3. Push Commands (Step-by-Step)
Agar aapko dobara push karna ho, toh ye steps use karein:

**Method A: Standard Push (May ask for login)**
```powershell
git add .
git commit -m "Your message here"
git push origin main
```

**Method B: Force Token Push (Best for 403 Errors)**
Agar permission denied ka error aaye, toh token use karein:
```powershell
# Token format: https://USERNAME:TOKEN@github.com/OWNER/REPO.git
git remote set-url origin https://WAIZHUSSAINANSARI9955:<YOUR_GITHUB_TOKEN>@github.com/WAIZHUSSAINANSARI9955/insta-api1.git
git push -u origin main
```

### 4. Important Git Tips
- **.gitignore**: `.env` aur `venv` files ko push nahi kiya gaya hai safety ke liye.
- **Main Branch**: Hamara primary branch `main` hai.

---
*Note: Yeh file sirf local reference ke liye hai aur GitHub par push nahi ki gayi hai.*
