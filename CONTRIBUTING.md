# Contributing to SOAI 2025 Admin Dashboard

Welcome! 👋  
We’re excited that you’re interested in contributing to the **SOAI 2025 Admin Dashboard**. Contributions of all kinds are welcome — code, documentation, design, suggestions, and more!

Please read through this guide to get started.

---

## 📌 Project Overview

This is the **Admin Dashboard** for the **SOAI 2025** project under Swecha. It serves as the control panel for managing students, activities, mentors, and administrative functions.

**Project Repository**: [code.swecha.org/soai2025/admin-dashboard](https://code.swecha.org/soai2025/admin-dashboard)

---

## 🛠️ How to Contribute

### Step 1: Fork and Clone the Repository

```bash
git clone https://code.swecha.org/your-username/admin-dashboard.git
cd admin-dashboard
```

### Step 2: Set Up Your Development Environment

1. **Create a Virtual Environment**  
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Secrets File**  
   Create a file named `secrets.toml` inside the `.streamlit/` directory and fill it based on the provided `secrets.example.toml` or setup documentation.

4. **(Optional) Run the App Locally**  
   ```bash
   streamlit run app.py
   ```

### Step 3: Create a New Branch

```bash
git checkout -b feature/your-feature-name
```

### Step 4: Make Your Changes

- Follow project conventions  
- Keep code clean and well-commented  
- Ensure the app runs without errors  

### Step 5: Commit Your Changes

Use clear and descriptive commit messages:

```bash
git add .
git commit -m "Add: feature description"
```

### Step 6: Push and Open a Merge Request

```bash
git push origin feature/your-feature-name
```

Then, go to the GitLab repository and open a **Merge Request** targeting the `main` or `dev` branch.

---

## ✅ Guidelines

### Code Style

- Use consistent naming conventions  
- Organize code modularly  
- Remove unused variables and imports  

### Branch Naming Convention

- `feature/your-feature`  
- `bugfix/fix-description`  
- `docs/update-readme`  

### Merge Request Checklist

- [ ] Code compiles without errors  
- [ ] Follows coding standards  
- [ ] Commit messages are descriptive  
- [ ] No sensitive data is included  
- [ ] Related issues are linked (if any)  

---

## 🐞 Reporting Bugs

If you find a bug:

1. Create an issue in the [GitLab Issues Tab](https://code.swecha.org/soai2025/admin-dashboard/-/issues)  
2. Include:
   - Steps to reproduce  
   - Expected vs actual behavior  
   - Screenshots (if possible)  

---

## 🙌 Community and Communication

For questions, suggestions, or help, reach out via the official [Swecha GitLab](https://code.swecha.org/) or community channels.

---

## 📄 License

This project is licensed under the [GNU GPLv3 License](https://www.gnu.org/licenses/gpl-3.0.html) unless specified otherwise.

---

Thanks for contributing! 🎉
